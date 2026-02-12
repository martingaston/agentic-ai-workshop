# Synthetic Ecommerce Abuse Detection Dataset

A Python-based generator for creating realistic synthetic datasets to train ML models for detecting account abuse and payment fraud in ecommerce platforms.

## Overview

This tool generates CSV datasets with realistic patterns for:
- **Legitimate transactions** (~75% of data)
- **Fake account abuse** (~10% of data) - New accounts with temporary emails, unverified profiles
- **Account takeover** (~8% of data) - Established accounts with suspicious device/location changes
- **Payment fraud** (~7% of data) - Geographic mismatches, failed verification, high-risk items

## Features

- **40+ realistic features** including account, device, network, payment, and behavioral signals
- **Pattern-based generation** with characteristic distributions for each abuse type
- **Configurable class distributions** to match your training needs
- **Reproducible** with random seed support
- **Validation** with built-in quality checks
- **Scalable** - generate 10K to 100K+ records

## Quick Start

This workshop includes two API services that work together:

1. **ML Service** (Port 8000) - Basic fraud detection using the trained ML model
2. **Agent Service** (Port 8001) - Intelligent decision-making with auto-approve/deny and agent review

### Architecture

```
Transaction → Agent Service (8001) → ML Service (8000) → Model Prediction
                     ↓
              Decision Engine
                     ↓
         approve / deny / review
```

### 1. Start the ML Service (Port 8000)

The ML service provides the core fraud detection model API.

```bash
# Start the ML service
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Agent Service (Port 8001)

The agent service wraps the ML service with intelligent decision-making.

```bash
# In a new terminal, start the agent service
uv run uvicorn agent.main:app --host 0.0.0.0 --port 8001
```

**Decision Logic:**
- `legitimacy_score >= 0.7` → **Auto-approve** (low fraud risk)
- `legitimacy_score <= 0.4` → **Auto-deny** (high fraud risk)
- `0.4 < legitimacy_score < 0.7` → **Agent review** (uncertain, needs human review)

**Endpoints:**
- `GET /api/v1/health` - Health check (includes ML service status)
- `GET /api/v1/agent/info` - Agent configuration and thresholds
- `POST /api/v1/review` - Review transaction and make decision

**Test it:**
```bash
curl http://localhost:8001/api/v1/health
```

### 3. Test the Services

`./trigger_agent_review.sh`


