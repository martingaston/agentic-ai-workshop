# Fraud Review Endpoint - Sequence Diagram

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI<br/>/api/v1/review
    participant Engine as FraudDecisionEngine<br/>make_decision()
    participant ML as MLServiceClient<br/>predict()
    participant Agent as LangGraph Agent<br/>invoke_fraud_review()
    participant Tool as analyze_fraud_indicators()
    participant LLM as GPT-4

    Client->>+API: POST /api/v1/review<br/>(TransactionRequest)
    API->>+Engine: make_decision(transaction)
    Engine->>+ML: predict(transaction)
    ML-->>-Engine: FraudPredictionResponse<br/>{legitimacy_score: 0.0–1.0}

    alt Auto Approve (score >= 0.7)
        Engine->>Engine: _auto_approve_decision()
        Engine-->>API: decision="approve"<br/>decision_maker="ml_model"
        API-->>Client: 200 OK — Approved

    else Auto Deny (score <= 0.4)
        Engine->>Engine: _auto_deny_decision()
        Engine-->>API: decision="deny"<br/>decision_maker="ml_model"
        API-->>Client: 200 OK — Denied

    else Manual Review (0.4 < score < 0.7)
        Engine->>+Agent: _agent_review(transaction, ml_prediction)
        Agent->>Agent: Build system prompt +<br/>human message with transaction data
        Agent->>+LLM: Invoke LangGraph with tools
        LLM->>+Tool: Call analyze_fraud_indicators()
        Tool->>Tool: _evaluate_account_risk()
        Tool->>Tool: _evaluate_authentication_risk()
        Tool->>Tool: _evaluate_payment_risk()
        Tool->>Tool: _evaluate_behavioral_risk()
        Tool->>Tool: _evaluate_network_risk()
        Tool-->>-LLM: Composite risk score (0–100)<br/>+ per-category breakdown
        LLM-->>-Agent: "DECISION: APPROVE|DENY"<br/>+ reasoning
        Agent->>Agent: _parse_agent_decision()

        alt Agent approves
            Agent-->>Engine: decision="approve"
            Engine-->>API: decision="approve"<br/>decision_maker="agent"
            API-->>Client: 200 OK — Approved (agent)
        else Agent denies
            Agent-->>Engine: decision="deny"
            Engine-->>API: decision="deny"<br/>decision_maker="agent"
            API-->>Client: 200 OK — Denied (agent)
        else Agent inconclusive
            Agent-->>-Engine: decision="review"
            Engine-->>-API: decision="review"<br/>decision_maker="review_required"
            API-->>Client: 200 OK — Escalated to human review
        end
    end
```

## Decision Thresholds

| ML Legitimacy Score | Path            | Decision Maker     |
|--------------------:|:----------------|:-------------------|
| **>= 0.7**         | Auto Approve    | `ml_model`         |
| **0.4 – 0.7**      | Agent Review    | `agent` or `review_required` |
| **<= 0.4**         | Auto Deny       | `ml_model`         |

## Agent Risk Analysis Categories

When the ML score falls in the uncertain range, the LangGraph agent calls `analyze_fraud_indicators()` which evaluates five risk categories:

| Category           | Key Signals                                              |
|:-------------------|:---------------------------------------------------------|
| Account Risk       | Account age, order amount, verification status           |
| Authentication Risk| Failed logins, password resets, new device/location      |
| Payment Risk       | CVV/AVS results, billing/shipping mismatch               |
| Behavioral Risk    | Transaction velocity, order amount vs average            |
| Network Risk       | VPN/proxy detection, IP country mismatches               |

The composite risk score (0–100) guides the agent's final decision:
- **< 30** → Recommend APPROVE
- **30–49** → Needs careful review
- **>= 50** → Recommend DENY
