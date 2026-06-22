import unittest
from unittest.mock import MagicMock, patch
from src.track_1_agent_under_test.car_bench_agent import CARBenchAgentExecutor

class TestViviAgentPipeline(unittest.IsolatedAsyncioTestCase):

    @patch('src.track_1_agent_under_test.car_bench_agent.completion')
    async def test_execute_pipeline_flow(self, mock_completion):
        # Setup mock responses for: 1) Intent classification, 2) Reasoning call
        mock_intent_response = MagicMock()
        mock_intent_msg = MagicMock()
        mock_intent_msg.content = '{"intent": "weather", "confidence": 1.0}'
        mock_intent_response.choices = [MagicMock(message=mock_intent_msg)]
        
        mock_action_response = MagicMock()
        mock_action_msg = MagicMock()
        mock_action_msg.content = "Hôm nay trời nắng đẹp nha bạn!"
        mock_action_msg.tool_calls = None
        mock_action_msg.thinking_blocks = None
        mock_action_msg.reasoning_content = None
        mock_action_response.choices = [MagicMock(message=mock_action_msg)]
        mock_action_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        mock_action_response._hidden_params = {"response_cost": 0.001}
        
        mock_completion.side_effect = [mock_intent_response, mock_action_response]

        executor = CARBenchAgentExecutor(model="gpt-4.1-mini")
        
        # Mock RequestContext & EventQueue
        context = MagicMock()
        context.context_id = "test_ctx_pipeline"
        part_text = MagicMock(text="Weather tomorrow?")
        part_text.WhichOneof.return_value = "text"
        part_text.text = "Thời tiết ngày mai thế nào?"
        
        context.message.parts = [part_text]
        event_queue = MagicMock()
        event_queue.enqueue_event = unittest.mock.AsyncMock()

        # Run execute pipeline
        await executor.execute(context, event_queue)
        
        # Verify intent classification was triggered
        self.assertEqual(mock_completion.call_count, 2)
        
        # Check messages stored correctly
        saved_messages = executor.ctx_id_to_messages["test_ctx_pipeline"]
        self.assertEqual(saved_messages[-1]["content"], "Hôm nay trời nắng đẹp nha bạn!")
        self.assertIn("Active User Intent: weather", saved_messages[0]["content"])

if __name__ == "__main__":
    unittest.main()
