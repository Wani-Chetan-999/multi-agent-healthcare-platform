from langgraph.graph import StateGraph, END
from app.agents.state import HealthcareAgentState
from app.agents.nodes import GraphAgentNodes

def conditional_routing_logic(state: HealthcareAgentState) -> str:
    return state["next_action"]

workflow = StateGraph(HealthcareAgentState)

# Register our three specialized graph execution nodes
workflow.add_node("router", GraphAgentNodes.router_node)
workflow.add_node("general_chat", GraphAgentNodes.general_chat_agent_node)
workflow.add_node("clinical_triage", GraphAgentNodes.triage_agent_node)
workflow.add_node("medical_knowledge_faq", GraphAgentNodes.medical_knowledge_faq_node) # Linked RAG Node

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    conditional_routing_logic,
    {
        "general_chat": "general_chat",
        "clinical_triage": "clinical_triage",
        "medical_knowledge_faq": "medical_knowledge_faq"  # Linked routing edge target
    }
)

workflow.add_edge("general_chat", END)
workflow.add_edge("clinical_triage", END)
workflow.add_edge("medical_knowledge_faq", END)

compiled_healthcare_graph = workflow.compile()