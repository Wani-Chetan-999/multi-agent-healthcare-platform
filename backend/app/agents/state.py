from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class HealthcareAgentState(TypedDict):
    """
    The unified state boundary across our LangGraph execution core.
    """
    messages: List[BaseMessage]        # Holds the ongoing chat interaction loop
    user_id: int                      # Tracks the active authorized database user
    session_id: str                   # Tracks the multi-turn session id
    next_action: str                  # Structural routing signal flag
    triage_evaluation: Dict[str, Any] # Specialized payload containing extraction metadata