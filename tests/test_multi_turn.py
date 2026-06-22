import unittest
from unittest.mock import MagicMock, patch
from src.track_1_agent_under_test.car_bench_agent import CARBenchAgentExecutor

class TestViviMultiTurnFlow(unittest.IsolatedAsyncioTestCase):

    @patch('src.track_1_agent_under_test.car_bench_agent.completion')
    async def test_multi_turn_state_confirmation(self, mock_completion):
        # 1st turn setup (Agent returns a confirmation request)
        mock_intent_1 = MagicMock()
        mock_intent_1.choices = [
            MagicMock(message=MagicMock(content='{"intent": "body_control", "confidence": 1.0}'))
        ]
        
        mock_action_1 = MagicMock()
        mock_action_1.choices = [
            MagicMock(message=MagicMock(content="Bạn có chắc chắn muốn mở cửa sổ trời không?", tool_calls=[]))
        ]
        mock_action_1.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        mock_action_1._hidden_params = {"response_cost": 0.001}
        
        # 2nd turn setup (User confirms, Agent executes action)
        mock_intent_2 = MagicMock()
        mock_intent_2.choices = [
            MagicMock(message=MagicMock(content='{"intent": "body_control", "confidence": 1.0}'))
        ]
        
        mock_action_2 = MagicMock()
        mock_action_2.choices = [
            MagicMock(message=MagicMock(content="Đã mở cửa sổ trời cho bạn!", tool_calls=[
                {"id": "tc_sunroof", "type": "function", "function": {"name": "open_close_sunroof", "arguments": "{}"}}
            ]))
        ]
        mock_action_2.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        mock_action_2._hidden_params = {"response_cost": 0.001}
        
        mock_completion.side_effect = [mock_intent_1, mock_action_1, mock_intent_2, mock_action_2]

        executor = CARBenchAgentExecutor(model="gpt-4.1-mini")
        
        # Turn 1 Execution
        context_1 = MagicMock()
        context_1.context_id = "test_ctx_multi_turn"
        part_1 = MagicMock(text="Mở cửa sổ trời")
        part_1.WhichOneof.return_value = "text"
        part_1.text = "Mở cửa sổ trời"
        context_1.message.parts = [part_1]
        
        event_queue = MagicMock()
        event_queue.enqueue_event = unittest.mock.AsyncMock()

        await executor.execute(context_1, event_queue)
        
        # Set pending confirmation manually in state to mock multi-turn logic flow
        state = executor.ctx_id_to_state["test_ctx_multi_turn"]
        state.set_pending_confirmation({"name": "open_close_sunroof", "kwargs": {}})
        
        # Turn 2 Execution
        context_2 = MagicMock()
        context_2.context_id = "test_ctx_multi_turn"
        part_2 = MagicMock(text="Đúng vậy")
        part_2.WhichOneof.return_value = "text"
        part_2.text = "Đúng vậy"
        context_2.message.parts = [part_2]
        
        await executor.execute(context_2, event_queue)
        
        # Verify calls count
        self.assertEqual(mock_completion.call_count, 4)
        
        saved_messages = executor.ctx_id_to_messages["test_ctx_multi_turn"]
        # Turn 2 LLM prompt includes active confirmation context
        self.assertIn("Pending User Confirmation: True", saved_messages[0]["content"])

if __name__ == "__main__":
    unittest.main()
