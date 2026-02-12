"""Langchain agent setup for fraud review.

PLACEHOLDER: This is a workshop exercise for attendees to implement.
"""

import logging
from collections.abc import Callable
from typing import Optional, Sequence

from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)


# PLACEHOLDER - Workshop participants will customize this prompt
FRAUD_REVIEW_SYSTEM_PROMPT = """You are a fraud detection specialist analyzing uncertain transactions.

Your job is to:
1. Analyze the transaction data thoroughly
2. Consider multiple fraud risk factors
3. Make a clear approve/deny decision with strong reasoning

WORKSHOP TODO: Customize this prompt to:
- Define clear decision criteria
- Specify how to weigh different risk factors
- Provide examples of fraud patterns
- Set threshold for approve vs deny
"""


def create_fraud_review_agent(
    tools: Sequence[BaseTool | Callable[..., object]],
    model: str = "openai:gpt-4",
    temperature: float = 0.0,
    api_key: Optional[str] = None,
) -> Optional[CompiledStateGraph]:
    """Create an agent for fraud review.

    PLACEHOLDER: Workshop participants will implement the full agent configuration.

    Workshop TODO:
    1. Configure LLM with proper API key
    2. Customize the system prompt for fraud detection
    3. Add reasoning strategies (few-shot examples, chain-of-thought)
    4. Add memory/context management if needed

    Args:
        tools: Sequence of langchain tools available to the agent
        model: LLM model identifier using provider:model format (default: openai:gpt-4)
        temperature: LLM temperature (0.0 for deterministic)
        api_key: OpenAI API key (if None, reads from environment)

    Returns:
        Compiled agent graph or None if API key is not configured
    """
    # PLACEHOLDER - needs API key configuration
    if not api_key:
        logger.warning(
            "No API key provided for langchain agent. "
            "Agent review will return placeholder responses."
        )
        return None

    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )

        # PLACEHOLDER - Create agent
        # WORKSHOP TODO: Configure the agent properly
        agent = create_agent(
            model=llm,
            tools=list(tools),
            system_prompt=FRAUD_REVIEW_SYSTEM_PROMPT,
            debug=True,  # Set to True for debugging during workshop
        )

        logger.info(f"Fraud review agent created with model {model}")
        return agent

    except Exception as e:
        logger.error(f"Failed to create fraud review agent: {e}")
        return None


def invoke_fraud_agent(
    agent: Optional[CompiledStateGraph],
    transaction_data: dict,
    ml_score: float,
) -> dict:
    """Invoke the fraud review agent for a transaction.

    PLACEHOLDER: Workshop participants will enhance this to handle agent responses properly.

    Args:
        agent: Compiled agent graph (or None if not configured)
        transaction_data: Transaction attributes
        ml_score: ML model's legitimacy score

    Returns:
        Dict with 'decision' (approve/deny) and 'reasoning' (explanation)
    """
    if not agent:
        # PLACEHOLDER - no agent configured
        return {
            "decision": "review",
            "reasoning": "Agent not configured. Set OPENAI_API_KEY to enable agent review.",
        }

    try:
        # WORKSHOP TODO: Format input properly for the agent
        # Consider what information the agent needs to make a decision
        input_text = f"Transaction data: {transaction_data}\nML Model Score: {ml_score}"

        # Invoke the agent via the messages-based interface
        result = agent.invoke({"messages": [{"role": "user", "content": input_text}]})

        # WORKSHOP TODO: Parse agent output to extract decision and reasoning
        # The agent should return a structured response that you can parse

        # PLACEHOLDER - extract the final assistant message
        messages = result.get("messages", [])
        agent_output = messages[-1].content if messages else ""

        # WORKSHOP TODO: Implement proper parsing logic
        # For now, this is a placeholder that looks for keywords
        if "approve" in agent_output.lower():
            decision = "approve"
        elif "deny" in agent_output.lower():
            decision = "deny"
        else:
            decision = "review"

        return {
            "decision": decision,
            "reasoning": agent_output,
        }

    except Exception as e:
        logger.error(f"Error invoking fraud agent: {e}")
        return {
            "decision": "review",
            "reasoning": f"Agent invocation failed: {str(e)}",
        }
