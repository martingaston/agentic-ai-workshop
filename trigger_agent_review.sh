#!/usr/bin/env bash
# Trigger the agentic decision flow in the fraud detection system.
#
# This transaction (TXN_20260129_A7A863 from the seed dataset) produces a
# legitimacy_score of ~0.587, which falls squarely in the agent review zone
# (0.4 < score < 0.7). The ML model is deterministic (random_state=42), so
# this will always trigger the agent review path.
#
# Prerequisites:
#   - ML service running on port 8000:   uv run uvicorn api.main:app --port 8000
#   - Agent service running on port 8001: uv run uvicorn agent.main:app --port 8001

curl -s -X POST http://localhost:8001/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN_20260129_A7A863",
    "timestamp": "2026-01-29T18:01:26",
    "user_id": "USER_693052",
    "order_amount": 416.66,
    "currency": "USD",
    "account_created_date": "2025-11-26T18:01:26",
    "account_age_days": 64,
    "email_domain": "protonmail.com",
    "phone_verified": true,
    "email_verified": true,
    "profile_complete": true,
    "failed_login_attempts_24h": 0,
    "successful_logins_7d": 10,
    "password_reset_count_30d": 0,
    "device_id": "DEV_F0B1542D",
    "ip_address": "151.216.xxx.xxx",
    "ip_country": "JP",
    "user_agent": "Edge/120.0",
    "device_type": "tablet",
    "new_device": false,
    "vpn_proxy_detected": false,
    "payment_method": "debit_card",
    "card_bin": "510000",
    "card_country": "NL",
    "billing_country": "NL",
    "shipping_country": "CH",
    "billing_shipping_match": false,
    "cvv_check_result": "pass",
    "avs_result": "partial_match",
    "payment_processor_response": "approved",
    "days_since_account_first_purchase": 23,
    "total_orders_lifetime": 6,
    "orders_last_24h": 0,
    "orders_last_7d": 0,
    "avg_order_value": 379.55,
    "session_duration_seconds": 184,
    "cart_additions_session": 3,
    "high_risk_category": true
  }' | python3 -m json.tool
