# Realistic Abuse Detection Dataset - Implementation Summary

## What Was Implemented

### 1. Difficulty Tiers for Fraud Detection

Each abuse type now has three difficulty levels:

**Easy to Detect (30% of abuse)**
- Clear, obvious fraud signals
- Confidence: 0.85-0.98
- Examples:
  - Fake accounts: 0-3 days old, temp email, no verification
  - Account takeover: 5+ failed logins, password reset, high-risk country
  - Payment fraud: Multiple geographic mismatches, failed CVV/AVS, many attempts

**Medium Difficulty (50% of abuse)**
- Mix of fraud and legitimate signals
- Confidence: 0.65-0.80
- Examples:
  - Fake accounts: 3-7 days old, mix of email types, partial verification
  - Account takeover: 2-6 failed logins, different location but low-risk country
  - Payment fraud: One or two mismatches, some verifications pass

**Hard to Detect (20% of abuse)**
- Sophisticated fraud, mostly looks legitimate
- Confidence: 0.45-0.65 → **HUMAN REVIEW ZONE**
- Examples:
  - Fake accounts: 7-30 days old, legitimate email, verified, patient behavior
  - Account takeover: Credential stuffing (no failed logins), same country
  - Payment fraud: Only shipping mismatch, all verifications pass

### 2. Suspicious But Legitimate Category (5% of dataset)

New transaction type that creates false positive scenarios:

- **VPN Users**: Privacy-conscious users (confidence: 0.45-0.65)
- **Travelers**: Geographic mismatches from travel (confidence: 0.40-0.60)
- **Gift Buyers**: Different shipping address (confidence: 0.35-0.55)
- **Power Shoppers**: High velocity but legitimate (confidence: 0.40-0.65)
- **Expats**: Living abroad, foreign shipping (confidence: 0.35-0.60)

These are `is_abuse = False` but have fraud-like signals → **HUMAN REVIEW NEEDED**

## Dataset Statistics (5K records)

### Distribution
- Legitimate: 3,500 (70%)
- Suspicious but legitimate: 250 (5%) 
- Fake accounts: 500 (10%)
- Account takeover: 400 (8%)
- Payment fraud: 350 (7%)

### Confidence Score Distribution
- Very Low (0.0-0.3): ~70% (mostly legitimate)
- Low (0.3-0.4): ~0.5%
- **HUMAN REVIEW (0.4-0.7): ~14-15%** ← Key improvement!
- High (0.7-0.85): ~8%
- Very High (0.85-1.0): ~7%

### By Difficulty Tier (Abuse Only)
| Tier | Proportion | Mean Confidence | Range |
|------|------------|----------------|-------|
| Easy | 30% | 0.91 | 0.85-0.97 |
| Medium | 50% | 0.73 | 0.65-0.80 |
| Hard | 20% | 0.55 | 0.45-0.65 |

## Changes Made

### Schema Changes (`schema.py`)
- Added `suspicious_but_legitimate` to `abuse_type` enum
- Added `difficulty_tier` field: `'easy'`, `'medium'`, `'hard'`, or `'n/a'`

### Pattern Generators (`data/patterns.py`)
- All abuse generators now accept `difficulty` parameter
- Adjusted feature distributions based on difficulty
- New `SuspiciousButLegitimatePatternGenerator` class with 5 behavior types

### Generation Script (`data/generate_synthetic_data.py`)
- Added `suspicious_but_legitimate_ratio` parameter (default: 0.05)
- Updated default `legitimate_ratio` to 0.70 (was 0.75)
- Difficulty tiers randomly assigned: 30% easy, 50% medium, 20% hard
- Updated validation to handle new category

## Model Performance Implications

### With 1K Dataset
- Model still achieves ~100% binary accuracy (abuse vs legitimate)
- **However:** Model is overconfident compared to true difficulty
  - Hard fraud: True confidence 0.45-0.65, Model confidence 0.70-0.85
  - Shows the patterns are still learnable but not trivial

### For Production API Use
The dataset now supports realistic scenarios:

**Auto-Approve (confidence < 0.3)**
- Clear legitimate transactions
- ~70% of traffic

**Human Review (confidence 0.4-0.7)**
- Hard-to-detect fraud
- Suspicious but legitimate users
- ~14-15% of traffic → **This is where human expertise adds value**

**Auto-Block (confidence > 0.7)**
- Clear fraud signals
- ~15% of traffic

### To Get Better Model Calibration
For the API to produce realistic 0.4-0.7 scores, you'll need:

1. **More data**: 50K-100K records for better patterns
2. **Probability calibration**: Use Platt scaling or isotonic regression
3. **Model tuning**: Adjust RandomForest depth/complexity or try other models
4. **Ensemble methods**: Combine multiple models for uncertainty estimates

## Usage

### Generate Dataset
```bash
# Default distribution (70% legit, 5% suspicious, 25% fraud)
uv run python -m data.generate_synthetic_data --size 50000

# Custom distribution
uv run python -m data.generate_synthetic_data \
    --size 100000 \
    --legitimate-ratio 0.65 \
    --suspicious-but-legitimate-ratio 0.10 \
    --fake-account-ratio 0.10 \
    --account-takeover-ratio 0.08 \
    --payment-fraud-ratio 0.07
```

### Analyze Confidence Scores
```python
import pandas as pd

df = pd.read_csv('abuse_dataset_5000_v2.csv')

# Check distribution
print(df.groupby('abuse_type')['abuse_confidence'].describe())

# Human review zone
human_review = df[(df['abuse_confidence'] >= 0.4) & (df['abuse_confidence'] < 0.7)]
print(f"Human review needed: {len(human_review)} ({len(human_review)/len(df)*100:.1f}%)")

# By difficulty
abuse_only = df[df['is_abuse'] == True]
print(abuse_only.groupby('difficulty_tier')['abuse_confidence'].mean())
```

## Key Achievements

✓ **More realistic fraud patterns** with varying sophistication  
✓ **False positive scenarios** (suspicious but legitimate)  
✓ **14-15% of data in human review zone** (0.4-0.7 confidence)  
✓ **Difficulty tiers** allow tracking which fraud is hardest to detect  
✓ **API-ready structure** with confidence scores suitable for thresholding  
✓ **Patterns are still learnable** (model can separate classes)  
✓ **More realistic for production** where not all fraud is obvious  

## Next Steps for Production API

1. **Train on larger dataset** (50K-100K records)
2. **Implement probability calibration** to match true difficulty
3. **Add model confidence intervals** for uncertainty
4. **A/B test thresholds** (e.g., 0.4 vs 0.5 for human review)
5. **Monitor false positive rate** in production
6. **Collect real labels** from human review to retrain
