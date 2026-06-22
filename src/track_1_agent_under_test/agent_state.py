from typing import Any, Optional

class AgentState:
    """Manages conversational state, user context values, and pending confirmations."""
    
    def __init__(self, context_id: str):
        self.context_id: str = context_id
        # Tracks current intents, disambiguations, and confirmations
        self.current_intent: Optional[str] = None
        self.pending_confirmation: bool = False
        self.pending_tool_call: Optional[dict[str, Any]] = None
        self.user_selections: list[Any] = []
        self.custom_state: dict[str, Any] = {}

    def set_pending_confirmation(self, tool_call: dict[str, Any]) -> None:
        self.pending_confirmation = True
        self.pending_tool_call = tool_call

    def clear_pending_confirmation(self) -> None:
        self.pending_confirmation = False
        self.pending_tool_call = None

    def serialize(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "current_intent": self.current_intent,
            "pending_confirmation": self.pending_confirmation,
            "pending_tool_call": self.pending_tool_call,
            "user_selections": self.user_selections,
            "custom_state": self.custom_state,
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "AgentState":
        state = cls(data["context_id"])
        state.current_intent = data.get("current_intent")
        state.pending_confirmation = data.get("pending_confirmation", False)
        state.pending_tool_call = data.get("pending_tool_call")
        state.user_selections = data.get("user_selections", [])
        state.custom_state = data.get("custom_state", {})
        return state
