from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from Advisor.nodes.query_rewrite import query_rewrite_node
from Advisor.nodes.rag_fusion import rag_fusion_node
from Advisor.nodes.recommendation import recommendation_node
from Advisor.nodes.knowledge_agent import knowledge_agent_node
from Advisor.nodes.intent_classifier import intent_classifier_node

from dotenv import load_dotenv
load_dotenv()


class AgentState(TypedDict):
    user_query: str
    intent: Literal["policy_recommendation", "financial_knowledge"]  # ADD THIS
    rewritten_queries: list[str]
    rag_context: str
    final_output: str

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("intent_classifier", intent_classifier_node)
    graph.add_node("query_rewrite", query_rewrite_node)
    graph.add_node("rag_fusion", rag_fusion_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("knowledge_agent", knowledge_agent_node)

    # Start
    graph.add_edge(START, "intent_classifier")

    # Conditional routing
    def route_intent(state: AgentState):
        return state["intent"]
    
    graph.add_conditional_edges(
        "intent_classifier",
        route_intent,
        {
            "policy_recommendation": "query_rewrite",
            "financial_knowledge": "knowledge_agent",
        }
    )

    # Policy path
    graph.add_edge("query_rewrite", "rag_fusion")
    graph.add_edge("rag_fusion", "recommendation")
    graph.add_edge("recommendation", END)

    # Knowledge path
    graph.add_edge("knowledge_agent", END)

    return graph.compile()