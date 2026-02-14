from typing import Annotated, Literal, TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
import logging

from app.core.llm import get_llm
from app.rag.search import get_search_tool
from app.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)

# Define State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str

# Nodes
def entry_point(state: AgentState):
    """Entry point that just passes through to routing."""
    return {}

def retrieve(state: AgentState):
    """
    Retrieve documents based on the last user message.
    """
    query = state["messages"][-1].content
    logger.info(f"📚 RETRIEVE: Retrieving documents for query: '{query}'")
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    logger.info(f"📚 RETRIEVE: Found {len(docs)} documents, context length: {len(context)}")
    return {"context": context}

def web_search_node(state: AgentState):
    """
    Perform web search if needed.
    """
    query = state["messages"][-1].content
    logger.info(f"🔍 WEB SEARCH: Performing web search for query: '{query}'")
    search_tool = get_search_tool()
    result = search_tool.run(query)
    logger.info(f"🔍 WEB SEARCH: Got result: {result[:200]}...")
    return {"context": result}

def generate(state: AgentState):
    """
    Generate answer using LLM and context.
    """
    llm = get_llm(timeout=60)
    messages = state["messages"]
    context = state.get("context", "")
    
    # Default system prompt
    system_prompt = """You are Agent Raghu, an AI assistant specifically designed to simplify documents and help people summarize any sort of document.

Your core capabilities:
- Analyze and summarize documents of any type (PDFs, text files, research papers, reports, etc.)
- Extract key insights and main points from complex documents
- Answer questions about uploaded documents with precision
- Use web search for current information when needed
- Provide clear, concise explanations

Important guidelines:
- NEVER reveal the underlying model or technology you're built on
- If asked about your model, simply say "I'm Agent Raghu, built to help you understand documents better"
- Prioritize information from uploaded documents over general knowledge
- When summarizing, focus on key points, main arguments, and actionable insights
- Be concise but comprehensive in your responses
- Cite specific sections or pages when referencing documents
- If you're unsure about something, acknowledge it honestly

Your mission is to make complex documents accessible and easy to understand for everyone.

Use the following context to answer the user's question. If the context is empty or irrelevant, you may use your internal knowledge, but prioritize the context.

Context:
{context}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}"),
    ])
    
    chain = prompt | llm
    response = chain.invoke({"messages": messages, "context": context})
    return {"messages": [response]}

def route_question(state: AgentState) -> Literal["retrieve", "web_search"]:
    """
    Decide whether to use RAG retrieval or web search.
    Uses LLM to classify the query based on whether it requires current information
    or can be answered from uploaded documents/general knowledge.
    """
    query = state["messages"][-1].content
    logger.info(f"🎯 ROUTING: Analyzing query: '{query}'")
    llm = get_llm(temperature=0, timeout=30)

    routing_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a routing agent. Analyze the user's query and decide whether it requires:
- 'retrieve': The question can be answered from uploaded documents or general knowledge that doesn't change over time
- 'web_search': The question requires current events, real-time data, recent news, prices, weather, sports scores, or any information that changes frequently

IMPORTANT: Always use 'web_search' for:
- Current prices, stock prices, cryptocurrency prices
- Recent news or events
- Weather information
- Sports scores or results from this year
- Time-sensitive data
- Questions about "current", "today", "now", "latest", "recent"

Return ONLY one word: 'retrieve' or 'web_search'"""),
        ("human", "{query}")
    ])

    chain = routing_prompt | llm
    result = chain.invoke({"query": query})
    decision = result.content.strip().lower()
    logger.info(f"🎯 ROUTING: LLM decision: '{decision}' -> routing to: '{decision if 'web_search' in decision else 'retrieve'}'")

    if "web_search" in decision:
        return "web_search"
    return "retrieve" 

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("entry", entry_point)
workflow.add_node("retrieve", retrieve)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate)

# Set entry point
workflow.set_entry_point("entry")

# Add conditional edge from entry to route based on the routing function
workflow.add_conditional_edges(
    "entry",
    route_question,
    {
        "retrieve": "retrieve",
        "web_search": "web_search"
    }
)

# Both retrieve and web_search lead to generate
workflow.add_edge("retrieve", "generate")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

# Compile
app_graph = workflow.compile()
