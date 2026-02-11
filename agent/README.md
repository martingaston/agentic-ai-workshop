# Fraud Detection Agent Service

Intelligent fraud detection service that wraps the ML fraud detection model with agent-based decision-making using Langchain.

## Overview

The agent service implements a three-tier decision strategy:

- **Auto-approve** (score >= 0.7): Low fraud risk transactions approved automatically
- **Auto-deny** (score <= 0.4): High fraud risk transactions denied automatically
- **Agent review** (0.4 < score < 0.7): Uncertain cases that require intelligent analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Service (Port 8001)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Application                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │                  Decision Engine                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Auto-Approve │  │  Auto-Deny   │  │Agent Review  │  │   │
│  │  │  (>= 0.7)    │  │  (<= 0.4)    │  │ (0.4 - 0.7)  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │                   ML Service Client                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   ML Service     │
                    │   (Port 8000)    │
                    └──────────────────┘
```

## Directory Structure

```
agent/
├── main.py                    # FastAPI application
├── models.py                  # Pydantic request/response models
├── decision_engine.py         # Decision orchestration logic
├── ml_client.py              # HTTP client for ML service
├── langchain_agent.py        # Langchain agent setup (PLACEHOLDER)
├── config.py                 # Configuration settings
├── test_agent.py             # Testing tool with synthetic data
└── tools/
    ├── __init__.py
    └── fraud_review_tool.py  # Fraud analysis tool (PLACEHOLDER)
```

## Installation

Dependencies are managed with `uv`:

```bash
# Install required packages
uv add langchain langchain-core langchain-openai langchain-community
```

## Running the Services

### 1. Start ML Service (Terminal 1)
```bash
uv run uvicorn api.main:app --port 8000
```

### 2. Start Agent Service (Terminal 2)
```bash
uv run uvicorn agent.main:app --port 8001
```

### 3. Test Agent Service (Terminal 3)
```bash
# Basic test
uv run python -m agent.test_agent --num-transactions 50 --fraud-ratio 0.5

# Show detailed samples
uv run python -m agent.test_agent --show-details

# Export review cases for analysis
uv run python -m agent.test_agent --num-transactions 200 --export-reviews
```

## API Endpoints

### GET /
Service information and available endpoints

### GET /api/v1/health
Health check - verifies agent service and ML service availability

**Response:**
```json
{
  "status": "healthy",
  "ml_service_available": true,
  "agent_service_version": "1.0.0"
}
```

### GET /api/v1/agent/info
Agent configuration and decision thresholds

**Response:**
```json
{
  "service_name": "Fraud Detection Agent",
  "version": "1.0.0",
  "auto_approve_threshold": 0.7,
  "auto_deny_threshold": 0.4,
  "agent_status": "placeholder"
}
```

### POST /api/v1/review
Review transaction and make fraud decision

**Request:** TransactionRequest (same schema as ML service)

**Response:**
```json
{
  "transaction_id": "TXN_12345",
  "decision": "review",
  "legitimacy_score": 0.55,
  "decision_maker": "review_required",
  "reasoning": "Uncertain case: legitimacy score (0.550) falls in uncertain range...",
  "ml_prediction": {
    "transaction_id": "TXN_12345",
    "legitimacy_score": 0.55,
    "prediction": "fraud",
    "confidence": 0.55,
    "model_version": "1.0.0"
  },
  "agent_analysis": "PLACEHOLDER: Agent review not yet implemented..."
}
```

## Testing Tool

The `test_agent.py` script provides comprehensive testing with synthetic data:

```bash
# Generate and test 100 transactions with 30% fraud
uv run python -m agent.test_agent --num-transactions 100 --fraud-ratio 0.3

# Show detailed transaction samples
uv run python -m agent.test_agent --show-details

# Export review cases to JSON
uv run python -m agent.test_agent --export-reviews
```

**Example Output:**
```
======================================================================
TEST RESULTS SUMMARY
======================================================================

Total transactions tested: 100
  ✅ Approved: 45
  ❌ Denied: 40
  🔍 Needs Review: 15
  ⚠️  Errors: 0

Approved transactions (n=45):
  Score range: 0.712 - 0.985
  Average score: 0.847

Denied transactions (n=40):
  Score range: 0.045 - 0.398
  Average score: 0.221

Review required transactions (n=15):
  Score range: 0.412 - 0.687
  Average score: 0.549
  📝 Workshop Task: Implement agent logic for these!
======================================================================
```

## Workshop Implementation Tasks

The following components are **PLACEHOLDERS** for workshop participants to implement:

### 1. Langchain Agent Configuration (`langchain_agent.py`)

**TODO:**
- Configure LLM with OpenAI API key
- Customize prompt template for fraud detection
- Add few-shot examples of fraud analysis
- Implement proper error handling
- Add agent memory/context management

### 2. Fraud Review Tool (`tools/fraud_review_tool.py`)

**TODO:**
- Implement fraud indicator analysis logic
- Consider these risk factors:
  - Account age vs. order value
  - Failed login attempts and velocity
  - Geographic mismatches (billing/shipping)
  - Payment verification failures (CVV/AVS)
  - New device from new location
  - Email/phone verification status
- Return structured risk assessment

### 3. Agent Review Method (`decision_engine.py:_agent_review`)

**TODO:**
- Invoke the langchain agent with transaction data
- Parse agent's decision and reasoning
- Return FraudDecisionResponse with:
  - `decision`: "approve" or "deny"
  - `decision_maker`: "agent"
  - `agent_analysis`: Detailed reasoning

## Configuration

Settings can be configured via environment variables or `.env` file:

```bash
# Service configuration
AGENT_SERVICE_PORT=8001
ML_SERVICE_URL=http://localhost:8000

# Decision thresholds
AUTO_APPROVE_THRESHOLD=0.7
AUTO_DENY_THRESHOLD=0.4

# LLM configuration (for workshop)
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.0
```

## Example Usage

```python
import httpx
from datetime import datetime

async def review_transaction():
    transaction = {
        "transaction_id": "TXN_12345",
        "timestamp": "2024-01-15T14:30:00",
        "user_id": "user_123",
        "order_amount": 150.0,
        # ... other fields
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/review",
            json=transaction
        )
        decision = response.json()
        print(f"Decision: {decision['decision']}")
        print(f"Score: {decision['legitimacy_score']}")
        print(f"Reasoning: {decision['reasoning']}")
```

## Development

### Running Tests
```bash
# Run the agent tester
uv run python -m agent.test_agent

# Run with different parameters
uv run python -m agent.test_agent --num-transactions 200 --fraud-ratio 0.3
```

### Checking Service Health
```bash
# Agent service health
curl http://localhost:8001/api/v1/health

# ML service health
curl http://localhost:8000/api/v1/health
```

### Viewing Logs
The agent service logs all decisions with timestamps, transaction IDs, and reasoning.

## Success Criteria

### Implemented ✅
- Agent service runs on port 8001
- Auto-approve for scores >= 0.7
- Auto-deny for scores <= 0.4
- Health check endpoint works
- ML service integration complete
- Test tool generates synthetic transactions
- Results categorized by decision type

### Workshop Tasks (PLACEHOLDER) 🚧
- Langchain agent configuration
- Fraud review tool implementation
- Agent review decision logic
- OpenAI API integration

## Troubleshooting

### Service won't start
- Ensure ML service is running on port 8000
- Check that port 8001 is not in use
- Verify all dependencies are installed

### 503 errors
- ML service may be down - check `http://localhost:8000/api/v1/health`
- Check agent service logs for specific errors

### No review cases in tests
- The ML model is very confident in most predictions
- Try adjusting fraud_ratio or running more transactions
- Review cases typically have scores between 0.4-0.7

## Next Steps

1. Implement the langchain agent configuration
2. Build the fraud review tool logic
3. Test with the provided synthetic data
4. Iterate on prompt engineering for better decisions
5. Add monitoring and metrics

## License

Part of the abuse-workshop project.
