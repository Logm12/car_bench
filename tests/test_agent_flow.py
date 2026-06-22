import unittest
from src.track_1_agent_under_test.vivi_prompts import VIVI_SYSTEM_PROMPT, INTENT_CLASSIFICATION_SYSTEM_PROMPT
from src.track_1_agent_under_test.agent_state import AgentState

class TestViviAgentDesign(unittest.TestCase):

    def test_system_prompt_checks(self):
        # System prompt should be TTS compatible (no markdown structures)
        self.assertIn("Vivi", VIVI_SYSTEM_PROMPT)
        self.assertNotIn("```", VIVI_SYSTEM_PROMPT)
        self.assertIn("Celsius", VIVI_SYSTEM_PROMPT)

    def test_intent_classification_structure(self):
        self.assertIn("weather", INTENT_CLASSIFICATION_SYSTEM_PROMPT)
        self.assertIn("display_control", INTENT_CLASSIFICATION_SYSTEM_PROMPT)
        self.assertIn("Few-Shot Examples", INTENT_CLASSIFICATION_SYSTEM_PROMPT)

    def test_state_management(self):
        state = AgentState("test_ctx")
        self.assertEqual(state.context_id, "test_ctx")
        self.assertFalse(state.pending_confirmation)
        
        mock_tool = {"name": "open_sunroof", "kwargs": {}}
        state.set_pending_confirmation(mock_tool)
        self.assertTrue(state.pending_confirmation)
        self.assertEqual(state.pending_tool_call, mock_tool)
        
        # Serialize/Deserialize
        serialized = state.serialize()
        restored = AgentState.deserialize(serialized)
        self.assertEqual(restored.context_id, "test_ctx")
        self.assertTrue(restored.pending_confirmation)
        self.assertEqual(restored.pending_tool_call, mock_tool)

if __name__ == "__main__":
    unittest.main()
