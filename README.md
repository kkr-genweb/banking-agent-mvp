# GenBot Banking Agent MVP

## Vision

GenBot Banking Agent aims to improve financial transaction verification and security in GenAI apps. Unlike traditional AI agents that may hallucinate or make costly errors, GenBots are designed to be as logically steerable as traditional software. This enables reliability, safety, and accuracy in high-stakes financial environments.

## Core Capabilities

### Transaction Verification
- **SWIFT and Financial Transaction Validation**: Ensures accuracy and legitimacy of international transfers
- **PClean-like Entity Resolution**: Verifies counterparty identities to prevent fraud
- **Goal Inference Filtering**: Flags payment requests/trades that likely contain errors (e.g., wrong number of zeros)

### Symbolic World Model
- Maintains an accurate representation of financial entities and relationships
- Understands banking protocols and compliance requirements
- Models transaction patterns to detect anomalies

### User Modeling
- Adapts to individual user behavior patterns
- Recognizes authorized vs. unauthorized transaction requests
- Provides personalized support based on user history and preferences

## Economic Impact

This technology has the potential to prevent billions in fraudulent transactions and human errors in the financial sector annually. The agent operates with a focus on safety and auditability, making it suitable for regulated environments.

## Implementation

This MVP demonstrates core capabilities through a simulated banking environment. The implementation uses the pydantic-ai framework for type safety and reliability.

### Running the Demo

```bash
uv run mvp_bank_support.py
```

For development, make sure to set up your OpenAI API key:

```bash
cat set_openai_key.sh
#export OPENAI_API_KEY="sk-proj-..."

source set_openai_key.sh
```
