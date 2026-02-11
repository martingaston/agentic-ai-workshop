"""Langchain agent setup for fraud review.

PLACEHOLDER: This is a workshop exercise for attendees to implement.
"""

from typing import List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)


# PLACEHOLDER - Workshop participants will customize this prompt
FRAUD_REVIEW_PROMPT_TEMPLATE = """You are a fraud detection specialist analyzing uncertain transactions.

You have access to tools that can analyze fraud indicators. Your job is to:
1. Analyze the transaction data thoroughly
2. Consider multiple fraud risk factors
3. Make a clear approve/deny decision with strong reasoning

Available tools:
{tools}

Tool names: {tool_names}

Transaction to review:
{input}

ML Model Score: {ml_score}

WORKSHOP TODO: Customize this prompt to:
- Define clear decision criteria
- Specify how to weigh different risk factors
- Provide examples of fraud patterns
- Set threshold for approve vs deny

Thought: {agent_scratchpad}
"""


def create_fraud_review_agent(
    tools: List[Tool],
    model: str = "gpt-4",
    temperature: float = 0.0,
    api_key: Optional[str] = None
) -> Optional[AgentExecutor]:
    """Create a ReAct agent for fraud review.

    PLACEHOLDER: Workshop participants will implement the full agent configuration.

    Workshop TODO:
    1. Configure LLM with proper API key
    2. Customize the prompt template for fraud detection
    3. Add reasoning strategies (few-shot examples, chain-of-thought)
    4. Configure agent parameters (max_iterations, handle_parsing_errors)
    5. Add memory/context management if needed

    Args:
        tools: List of langchain tools available to the agent
        model: LLM model name (default: gpt-4)
        temperature: LLM temperature (0.0 for deterministic)
        api_key: OpenAI API key (if None, reads from environment)

    Returns:
        Configured AgentExecutor or None if API key is not configured
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
            openai_api_key=api_key
        )

        # Create prompt template
        prompt = PromptTemplate(
            template=FRAUD_REVIEW_PROMPT_TEMPLATE,
            input_variables=["input", "ml_score", "tools", "tool_names", "agent_scratchpad"]
        )

        # PLACEHOLDER - Create ReAct agent
        # WORKSHOP TODO: Configure the agent properly
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )

        # Create agent executor
        # WORKSHOP TODO: Add proper error handling, max_iterations, etc.
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # Set to True for debugging during workshop
            max_iterations=5,
            handle_parsing_errors=True
        )

        logger.info(f"Fraud review agent created with model {model}")
        return agent_executor

    except Exception as e:
        logger.error(f"Failed to create fraud review agent: {e}")
        return None


def invoke_fraud_agent(
    agent_executor: Optional[AgentExecutor],
    transaction_data: dict,
    ml_score: float
) -> dict:
    """Invoke the fraud review agent for a transaction.

    PLACEHOLDER: Workshop participants will enhance this to handle agent responses properly.

    Args:
        agent_executor: Configured agent executor (or None if not configured)
        transaction_data: Transaction attributes
        ml_score: ML model's legitimacy score

    Returns:
        Dict with 'decision' (approve/deny) and 'reasoning' (explanation)
    """
    if not agent_executor:
        # PLACEHOLDER - no agent configured
        return {
            "decision": "review",
            "reasoning": "Agent not configured. Set OPENAI_API_KEY to enable agent review."
        }

    try:
        # WORKSHOP TODO: Format input properly for the agent
        # Consider what information the agent needs to make a decision

        input_text = f"Transaction data: {transaction_data}"

        # Invoke the agent
        result = agent_executor.invoke({
            "input": input_text,
            "ml_score": ml_score
        })

        # WORKSHOP TODO: Parse agent output to extract decision and reasoning
        # The agent should return a structured response that you can parse

        # PLACEHOLDER - parse agent output
        agent_output = result.get("output", "")

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
            "reasoning": agent_output
        }

    except Exception as e:
        logger.error(f"Error invoking fraud agent: {e}")
        return {
            "decision": "review",
            "reasoning": f"Agent invocation failed: {str(e)}"
        }
