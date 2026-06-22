"""
CAR-bench Agent - Agent under test that solves CAR-bench tasks.

This is the agent being tested. It:
1. Receives task descriptions with available tools from the evaluator
2. Decides which tool to call or how to respond
3. Returns responses in the expected JSON format wrapped in <json>...</json> tags
"""
import json
import time
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.helpers.proto_helpers import new_message, new_text_part, new_data_part
from a2a.types import Role
from google.protobuf.json_format import MessageToDict
from litellm import completion
from src.track_1_agent_under_test.vivi_prompts import VIVI_SYSTEM_PROMPT, INTENT_CLASSIFICATION_SYSTEM_PROMPT

sys.path.insert(0, str(Path(__file__).parent.parent))
from logging_utils import configure_logger
from tool_call_types import ToolCall, ToolCallsData
from turn_metrics import TURN_METRICS_KEY, PROMPT_TOKENS, COMPLETION_TOKENS, COST, MODEL, THINKING_TOKENS, NUM_LLM_CALLS, AVG_LLM_CALL_TIME_MS, NUM_PASSES
sys.path.pop(0)

logger = configure_logger(role="agent_under_test", context="-")

SYSTEM_PROMPT = """You are a helpful car voice assistant. Follow the policy and tool instructions provided."""


from src.track_1_agent_under_test.agent_state import AgentState

class CARBenchAgentExecutor(AgentExecutor):
    """Executor for the CAR-bench agent under test using native tool calling."""

    def __init__(self, model: str, temperature: float = 0.0, thinking: bool = False, reasoning_effort: str = "medium", interleaved_thinking: bool = False):
        self.model = model
        self.temperature = temperature
        self.thinking = thinking
        self.reasoning_effort = reasoning_effort  # Can be 'none', 'disable', 'low', 'medium', 'high', or integer token budget
        self.interleaved_thinking = interleaved_thinking  # Whether to use interleaved thinking
        self.ctx_id_to_messages: dict[str, list[dict]] = {}
        self.ctx_id_to_tools: dict[str, list[dict]] = {}
        self.ctx_id_to_state: dict[str, AgentState] = {}
        # Per-context turn metrics accumulation (reset when final response is sent)
        self.ctx_id_to_turn_metrics: dict[str, dict] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        inbound_message = context.message
        ctx_logger = logger.bind(role="agent_under_test", context=f"ctx:{context.context_id[:8]}")

        # Initialize or get conversation history
        if context.context_id not in self.ctx_id_to_messages:
            self.ctx_id_to_messages[context.context_id] = []

        messages = self.ctx_id_to_messages[context.context_id]
        tools = self.ctx_id_to_tools.get(context.context_id, [])

        # Parse the incoming A2A Message with Parts (now protobuf)
        user_message_text = None
        incoming_tool_results = None  # Structured tool results from evaluator

        try:
            for part in inbound_message.parts:
                content_type = part.WhichOneof("content")
                if content_type == "text":
                    text = part.text
                    # Parse system prompt and user message from formatted text
                    if "System:" in text and "\n\nUser:" in text:
                        # First message with system prompt
                        parts_split = text.split("\n\nUser:", 1)
                        system_prompt = parts_split[0].replace("System:", "").strip()
                        user_message_text = parts_split[1].strip()
                        if not messages:  # Only add system prompt once
                            messages.append({"role": "system", "content": system_prompt})
                    else:
                        # Regular user message
                        user_message_text = text

                elif content_type == "data":
                    # Extract tools or tool results from data Part
                    data = MessageToDict(part.data)
                    if "tools" in data:
                        tools = data["tools"]
                        self.ctx_id_to_tools[context.context_id] = tools
                    elif "tool_results" in data:
                        # Structured tool results from the evaluator
                        incoming_tool_results = data["tool_results"]

            # Fallback if no text part and no structured tool results found
            if not user_message_text and not incoming_tool_results:
                user_message_text = context.get_user_input()

            ctx_logger.info(
                "Received user message",
                context_id=context.context_id[:8],
                turn=len(messages) + 1,
                message_preview=(user_message_text[:100] if user_message_text else
                                 f"[{len(incoming_tool_results)} tool results]" if incoming_tool_results else "")
            )
            ctx_logger.debug(
                "Message details",
                context_id=context.context_id[:8],
                message=user_message_text,
                num_parts=len(inbound_message.parts),
                has_tools=bool(tools),
                num_tools=len(tools) if tools else 0,
                has_tool_results=bool(incoming_tool_results),
                num_tool_results=len(incoming_tool_results) if incoming_tool_results else 0
            )

        except Exception as e:
            logger.warning(f"Failed to parse message parts: {e}, using fallback")
            user_message_text = context.get_user_input()

        # Check if previous message had tool calls - if so, format as tool results
        if messages and messages[-1].get("role") == "assistant" and messages[-1].get("tool_calls"):
            prev_tool_calls = messages[-1]["tool_calls"]

            if incoming_tool_results:
                # Structured tool results from evaluator — match each result
                # to its corresponding tool_call_id by tool name
                tool_call_by_name = {}
                for tc in prev_tool_calls:
                    name = tc["function"]["name"]
                    # If multiple calls to the same tool, use a list
                    tool_call_by_name.setdefault(name, []).append(tc)

                tool_results = []
                for tr in incoming_tool_results:
                    tr_name = tr.get("tool_name", "") if isinstance(tr, dict) else tr.get("toolName", "")
                    matching_calls = tool_call_by_name.get(tr_name, [])
                    if matching_calls:
                        # Pop the first matching call to handle duplicate tool names
                        matched_tc = matching_calls.pop(0)
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": matched_tc["id"],
                            "content": tr.get("content", ""),
                        })
                    else:
                        # Fallback: no matching tool_call found, use first unmatched
                        ctx_logger.warning(
                            "No matching tool_call_id for tool result",
                            tool_name=tr_name,
                        )
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tr.get("tool_call_id", tr.get("toolCallId", f"unknown_{tr_name}")),
                            "content": tr.get("content", ""),
                        })
            else:
                # Fallback: no structured tool results, use the text message
                # for all tool calls (legacy behavior)
                tool_results = []
                for tc in prev_tool_calls:
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": user_message_text or "",
                    })

            # Add all tool result messages
            messages.extend(tool_results)

            ctx_logger.debug(
                "Formatted tool results",
                num_tools=len(tool_results),
                tool_call_ids=[tr["tool_call_id"] for tr in tool_results]
            )
        else:
            # Regular user message
            messages.append({"role": "user", "content": user_message_text})

        # Call LLM with native tool calling
        try:
            # Setup API key and base if using NVIDIA/Z-AI models
            api_key = None
            api_base = None
            import os
            if "z-ai" in self.model or "nvidia" in self.model:
                api_key = os.environ.get("NVIDIA_API_KEY")
                api_base = os.environ.get("NVIDIA_API_BASE")

            # Classify Intent (Query Classification Phase)
            intent_classification_messages = [
                {"role": "system", "content": INTENT_CLASSIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_message_text or ""}
            ]
            
            try:
                classified_intent = "web_search"
                # Direct class call to LiteLLM with fallback logic
                classification_res = completion(
                    model=self.model,
                    messages=intent_classification_messages,
                    temperature=0.0,
                    api_key=api_key,
                    api_base=api_base,
                )
                res_text = str(classification_res.choices[0].message.content or "")
                # Simple parsing of returned JSON
                import re
                match = re.search(r"\{.*?\}", res_text, re.DOTALL)
                if match:
                    parsed_json = json.loads(match.group(0))
                    classified_intent = parsed_json.get("intent", "web_search")
            except Exception as ex:
                ctx_logger.warning(f"Failed to classify intent: {ex}")
                
            # Load or initialize AgentState
            if context.context_id not in self.ctx_id_to_state:
                self.ctx_id_to_state[context.context_id] = AgentState(context.context_id)
            state = self.ctx_id_to_state[context.context_id]
            state.current_intent = classified_intent

            # Setup custom system instruction with classified intent and active state contexts
            updated_system_prompt = (
                VIVI_SYSTEM_PROMPT + 
                f"\nActive User Intent: {classified_intent}" +
                f"\nPending User Confirmation: {state.pending_confirmation}"
            )
            
            # Re-evaluate messages system context if necessary
            if not messages:
                messages.append({"role": "system", "content": updated_system_prompt})
            elif messages[0].get("role") == "system":
                messages[0]["content"] = updated_system_prompt
            else:
                messages.insert(0, {"role": "system", "content": updated_system_prompt})

            completion_kwargs = {
                "model": self.model,
                "tools": tools if tools else None,
                "api_key": api_key,
                "api_base": api_base,
            }

            if self.temperature is not None:
                completion_kwargs["temperature"] = self.temperature

            # Configure reasoning effort / thinking
            if self.thinking:
                    if self.model == "claude-opus-4-6":
                        completion_kwargs["thinking"] = {
                            "type": "adaptive"
                        }
                    else:
                        if self.reasoning_effort in [
                            "none",
                            "disable",
                            "low",
                            "medium",
                            "high",
                        ]:
                            completion_kwargs["reasoning_effort"] = self.reasoning_effort
                        else:
                            try:
                                thinking_budget = int(self.reasoning_effort)
                            except ValueError:
                                raise ValueError(
                                    "reasoning_effort must be 'none', 'disable', 'low', 'medium', 'high', or an integer value"
                                )
                            completion_kwargs["thinking"] = {
                                "type": "enabled",
                                "budget_tokens": thinking_budget,
                            }
                    if self.interleaved_thinking:
                        completion_kwargs["extra_headers"] = {
                                "anthropic-beta": "interleaved-thinking-2025-05-14"
                            }


            # Retry with exponential backoff for rate limiting resiliency
            max_retries = 3
            backoff_factor = 2.0
            response = None
            for attempt in range(max_retries):
                try:
                    call_start_time = time.perf_counter()
                    response = completion(
                        messages=messages,
                        **completion_kwargs
                    )
                    break
                except Exception as ex:
                    # Check for rate limit or similar retryable errors
                    if "rate_limit" in str(ex).lower() or attempt < max_retries - 1:
                        sleep_time = backoff_factor ** attempt
                        ctx_logger.warning(f"LLM call failed (attempt {attempt + 1}/{max_retries}). Retrying in {sleep_time}s... Error: {ex}")
                        time.sleep(sleep_time)
                    else:
                        raise ex

            # Accumulate turn metrics for this LLM call
            call_end_time = time.perf_counter()
            call_elapsed_ms = (call_end_time - call_start_time) * 1000.0

            if context.context_id not in self.ctx_id_to_turn_metrics:
                self.ctx_id_to_turn_metrics[context.context_id] = {
                    PROMPT_TOKENS: 0,
                    COMPLETION_TOKENS: 0,
                    THINKING_TOKENS: 0,
                    COST: 0.0,
                    NUM_LLM_CALLS: 0,
                    "_total_llm_time_ms": 0.0,
                }

            turn_m = self.ctx_id_to_turn_metrics[context.context_id]
            usage = getattr(response, "usage", None)
            if usage:
                try:
                    p_tok = int(getattr(usage, "prompt_tokens", 0) or 0)
                except Exception:
                    p_tok = 0
                try:
                    c_tok = int(getattr(usage, "completion_tokens", 0) or 0)
                except Exception:
                    c_tok = 0
                
                turn_m[PROMPT_TOKENS] += p_tok
                turn_m[COMPLETION_TOKENS] += c_tok
                
                # Some providers report thinking/reasoning tokens in completion_tokens_details
                details = getattr(usage, "completion_tokens_details", None)
                if details:
                    try:
                        r_tok = int(getattr(details, "reasoning_tokens", 0) or 0)
                    except Exception:
                        r_tok = 0
                    turn_m[THINKING_TOKENS] += r_tok
            
            try:
                hidden_p = getattr(response, "_hidden_params", {})
                if isinstance(hidden_p, dict):
                    raw_cost = hidden_p.get("response_cost", 0.0) or 0.0
                    cost_val = float(raw_cost)
                else:
                    cost_val = 0.0
            except Exception:
                cost_val = 0.0
            turn_m[COST] += cost_val
            turn_m[NUM_LLM_CALLS] += 1
            turn_m["_total_llm_time_ms"] += call_elapsed_ms

            # Get the message from LLM
            llm_message = response.choices[0].message
            is_mock = hasattr(llm_message, "_mock_name") or "Mock" in str(type(llm_message))
            if hasattr(llm_message, "model_dump") and not is_mock:
                assistant_content = llm_message.model_dump(exclude_unset=True)
            elif isinstance(llm_message, dict):
                assistant_content = llm_message
            else:
                # Handle MagicMock or other raw message objects
                assistant_content = {
                    "content": getattr(llm_message, "content", ""),
                    "tool_calls": getattr(llm_message, "tool_calls", None),
                    "reasoning_content": getattr(llm_message, "reasoning_content", None),
                    "thinking_blocks": getattr(llm_message, "thinking_blocks", None),
                }
                
                # Prevent MagicMock defaults from polluting the dictionary values
                for key in ["content", "tool_calls", "reasoning_content", "thinking_blocks"]:
                    val = assistant_content[key]
                    if hasattr(val, "_mock_name") or "MagicMock" in str(type(val)):
                        if key == "content":
                            assistant_content[key] = ""
                        else:
                            assistant_content[key] = None

            # Extract tool calls from assistant content
            tool_calls = assistant_content.get("tool_calls")

            ctx_logger.info(
                "LLM response received",
                has_tool_calls=bool(tool_calls),
                num_tool_calls=len(tool_calls) if tool_calls else 0,
                has_content=bool(assistant_content.get("content")),
                content_length=len(assistant_content.get("content") or ""),
                has_thinking=bool(assistant_content.get("thinking_blocks") or assistant_content.get("reasoning_content"))
            )
            ctx_logger.debug(
                "LLM response details",
                context_id=context.context_id[:8],
                content=assistant_content.get("content"),
                tool_calls=[{"name": tc["function"]["name"], "args": tc["function"]["arguments"]} for tc in tool_calls] if tool_calls else None,
                reasoning_content=assistant_content.get("reasoning_content")
            )

            # Build proper A2A Message with Parts (protobuf)
            parts = []

            # Add text Part if there's content
            if assistant_content.get("content"):
                parts.append(new_text_part(assistant_content["content"]))

            if assistant_content.get("tool_calls"):
                tool_calls_list = []
                for tc in assistant_content["tool_calls"]:
                    args_raw = tc["function"].get("arguments", {})
                    if isinstance(args_raw, str):
                        try:
                            args_parsed = json.loads(args_raw)
                        except Exception:
                            args_parsed = {}
                    elif isinstance(args_raw, dict):
                        args_parsed = args_raw
                    else:
                        args_parsed = {}
                    
                    tool_calls_list.append(
                        ToolCall(
                            tool_name=tc["function"]["name"],
                            arguments=args_parsed,
                        )
                    )
                tool_calls_data = ToolCallsData(tool_calls=tool_calls_list)
                parts.append(new_data_part(tool_calls_data.model_dump()))

            # Add reasoning_content as data Part for debugging (if present)
            if assistant_content.get("reasoning_content"):
                parts.append(new_data_part({"reasoning_content": assistant_content["reasoning_content"]}))

            # If no parts, add empty text
            if not parts:
                parts.append(new_text_part(assistant_content.get("content", "")))

            ctx_logger.debug(
                "Sending response",
                context_id=context.context_id[:8],
                num_parts=len(parts),
            )

        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            logger.error(f"LLM error: {e}\nTraceback: {tb_str}")
            # Error response as Parts
            parts = [new_text_part(f"Error processing request: {str(e)}")]
            # Create a simple assistant_content for error case
            assistant_content = {"content": f"Error processing request: {str(e)}"}

        # Add to history - preserve complete assistant message including thinking blocks
        # Store the full assistant_content to preserve thinking blocks and reasoning_content
        assistant_message_for_history = {
            "role": "assistant",
            "content": assistant_content.get("content"),
        }

        # Preserve tool calls in proper format for LLM API
        if assistant_content.get("tool_calls"):
            assistant_message_for_history["tool_calls"] = assistant_content["tool_calls"]

        # Preserve thinking blocks and reasoning content for Claude extended thinking
        if assistant_content.get("thinking_blocks"):
            assistant_message_for_history["thinking_blocks"] = assistant_content["thinking_blocks"]
        if assistant_content.get("reasoning_content"):
            assistant_message_for_history["reasoning_content"] = assistant_content["reasoning_content"]

        messages.append(assistant_message_for_history)

        # Always return a Message — the agent under test is a conversational participant
        # in a multi-turn exchange. The evaluator decides when the task is done.
        response_message = new_message(
            parts=parts,
            context_id=context.context_id,
            role=Role.ROLE_AGENT,
        )

        # Attach turn_metrics on final response (no tool calls = turn complete)
        has_tool_calls = bool(assistant_content.get("tool_calls"))
        if not has_tool_calls and context.context_id in self.ctx_id_to_turn_metrics:
            turn_m = self.ctx_id_to_turn_metrics.pop(context.context_id)
            num_calls = turn_m[NUM_LLM_CALLS]
            avg_time = (turn_m["_total_llm_time_ms"] / num_calls) if num_calls > 0 else 0.0
            metrics_data = {
                PROMPT_TOKENS: turn_m[PROMPT_TOKENS],
                COMPLETION_TOKENS: turn_m[COMPLETION_TOKENS],
                COST: turn_m[COST],
                MODEL: self.model,
                THINKING_TOKENS: turn_m[THINKING_TOKENS],
                NUM_LLM_CALLS: num_calls,
                AVG_LLM_CALL_TIME_MS: round(avg_time, 1),
                NUM_PASSES: 1,
            }
            response_message.metadata.update({TURN_METRICS_KEY: metrics_data})
            ctx_logger.info(
                "Attached turn_metrics to final response",
                num_llm_calls=num_calls,
                avg_llm_call_time_ms=round(avg_time, 1),
                prompt_tokens=turn_m[PROMPT_TOKENS],
                completion_tokens=turn_m[COMPLETION_TOKENS],
            )

        await event_queue.enqueue_event(response_message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the current execution."""
        logger.bind(role="agent_under_test", context=f"ctx:{context.context_id[:8]}").info(
            "Canceling context",
            context_id=context.context_id[:8]
        )
        if context.context_id in self.ctx_id_to_messages:
            del self.ctx_id_to_messages[context.context_id]
        if context.context_id in self.ctx_id_to_tools:
            del self.ctx_id_to_tools[context.context_id]
        if context.context_id in self.ctx_id_to_turn_metrics:
            del self.ctx_id_to_turn_metrics[context.context_id]
