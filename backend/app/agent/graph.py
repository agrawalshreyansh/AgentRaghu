from typing import Annotated, Literal, TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from app.core.llm import get_llm
from app.rag.search import get_search_tool
from app.rag.vector_store import get_vector_store

# Define State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str

# Nodes
def retrieve(state: AgentState):
    """
    Retrieve documents based on the last user message.
    """
    query = state["messages"][-1].content
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"context": context}

def web_search_node(state: AgentState):
    """
    Perform web search if needed.
    (Simplified: For now, we can make this decision based on a router or just always do it if RAG fails, 
    but let's make it a tool call or a specific step).
    For this 'Premium' agent, let's implement a smarter router.
    """
    query = state["messages"][-1].content
    search_tool = get_search_tool()
    result = search_tool.run(query)
    return {"context": result} # Overwrite or append context? Let's assume we use this if we route here.

def generate(state: AgentState):
    """
    Generate answer using LLM and context.
    """
    llm = get_llm()
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

def route_question(state: AgentState) -> Literal["retrieve", "web_search", "generate"]:
    """
    Decide whether to use RAG, Web Search, or just Chat.
    For simplicity, let's use a keyword check or a small LLM call.
    Let's try a simple router using the LLM.
    """
    llm = get_llm(temperature=0)
    # Simple classification
    # ... implementation of classification ...
    # For now, let's default to 'retrieve' for RAG agent focus.
    # A real implementation would ask the LLM "Is this about the uploaded docs or general knowledge?"
    
    # Heuristic: If we have vector store connection, try retrieval.
    # To truly be "Web Search Enabled", let's randomize or just parallelize?
    # Let's start with a fixed RAG flow for now as per "RAG based agent" priority.
    return "retrieve" 

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate)

# Edges
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

# Compile
app_graph = workflow.compile()
