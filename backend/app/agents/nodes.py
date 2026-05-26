from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.agents.state import HealthcareAgentState
from app.services.chat_service import ChatEngineService
from app.services.triage_service import ClinicalTriageService
from app.rag.vector_store import MedicalKnowledgeVectorMesh
from app.database.session import AsyncSessionLocal
from langchain_groq import ChatGroq
from app.core.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GraphAgentNodes:
    
    @staticmethod
    def router_node(state: HealthcareAgentState) -> Dict[str, Any]:
        """
        Inspects incoming message intent to route requests to the correct agent node.
        Now includes a route to the RAG-backed FAQ engine for medical terms.
        """
        messages = state.get("messages", [])
        if not messages:
            return {"next_action": "general_chat"}
            
        last_message_content = messages[-1].content.lower()
        
        # Route indicators
        medical_keywords = ["symptom", "pain", "hurt", "ache", "breathing", "fever", "bleeding", "dizzy", "swollen"]
        rag_keywords = ["protocol", "guideline", "definition", "treatment of", "what is", "pharmacology", "side effect"]
        
        if any(keyword in last_message_content for keyword in medical_keywords):
            return {"next_action": "clinical_triage"}
        elif any(keyword in last_message_content for keyword in rag_keywords):
            return {"next_action": "medical_knowledge_faq"}
        
        return {"next_action": "general_chat"}

    @staticmethod
    async def general_chat_agent_node(state: HealthcareAgentState) -> Dict[str, Any]:
        messages = state["messages"]
        user_id = state["user_id"]
        session_id = state["session_id"]
        last_user_prompt = messages[-1].content

        async with AsyncSessionLocal() as db:
            chat_service = ChatEngineService(db)
            complete_text = ""
            async for token in chat_service.execute_conversational_stream(user_id, session_id, last_user_prompt):
                complete_text += token
                
        return {"messages": [AIMessage(content=complete_text)]}

    @staticmethod
    async def triage_agent_node(state: HealthcareAgentState) -> Dict[str, Any]:
        messages = state["messages"]
        last_user_prompt = messages[-1].content
        
        triage_engine = ClinicalTriageService()
        assessment = await triage_engine.analyze_symptoms_risk_profile(last_user_prompt)
        
        prefix = "🚨 **CRITICAL EMERGENCY ALERT** 🚨\n\n" if assessment.is_emergency else "📋 **Clinical Triage Report**\n\n"
        formatted_response = (
            f"{prefix}"
            f"**Assigned Tier:** {assessment.severity_tier}\n\n"
            f"**Extracted Risk Markers:** {', '.join(assessment.risk_factors) if assessment.risk_factors else 'None'}\n\n"
            f"**Educational Insight:** {assessment.clinical_educational_guidance}\n\n"
            f"_{assessment.safety_disclaimer}_"
        )
        
        return {"messages": [AIMessage(content=formatted_response)], "triage_evaluation": assessment.model_dump()}

    @staticmethod
    async def medical_knowledge_faq_node(state: HealthcareAgentState) -> Dict[str, Any]:
        """
        Retrieves matching context blocks from ChromaDB and uses Groq 
        to synthesize an accurate, evidence-backed medical explanation.
        """
        messages = state["messages"]
        last_user_prompt = messages[-1].content
        
        # 1. Initialize our Chroma vector storage framework
        vector_mesh = MedicalKnowledgeVectorMesh()
        
        # 2. Extract context chunks using semantic similarity matching
        matched_chunks = vector_mesh.perform_semantic_knowledge_retrieval(last_user_prompt, k=3)
        
        # 3. Assemble and structure our raw reference data
        context_block = ""
        if matched_chunks:
            context_block = "\n\n".join([f"[Source: {c['source']}]: {c['content']}" for c in matched_chunks])
        else:
            context_block = "No direct verified clinical source reference context found inside the vector index databases."

        # 4. Construct our RAG grounding prompt template
        rag_llm = ChatGroq(groq_api_key=settings.GROQ_API_KEY, model_name="llama-3.1-8b-instant", temperature=0.1)
        
        system_instruction = (
            "You are a peer-reviewed Medical FAQ Validation Agent. Your sole directive is to answer the user's inquiry "
            "using the verified reference context snippets provided below. If the answer cannot be inferred from the context, "
            "use general professional clinical guidelines to provide safe educational insights. Always maintain full compliance and "
            "cite the reference source material transparently.\n\n"
            f"VERIFIED CLINICAL REFERENCE CONTEXT:\n{context_block}"
        )
        
        payload = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=last_user_prompt) if 'HumanMessage' in globals() else messages[-1]
        ]
        
        response = rag_llm.invoke(payload)
        return {"messages": [AIMessage(content=response.content)]}