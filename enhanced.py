"""Enhanced Banking Agent MVP - Demonstrating GenBot Banking Agent capabilities.

This enhanced version showcases:
- Transaction verification with SWIFT validation
- Entity resolution for counterparty verification
- Goal inference filtering for error detection
- Symbolic world model for financial entities
- User modeling and behavior analysis
- Anomaly detection and compliance monitoring

Run with:
    uv run enhanced.py
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import json

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext


class Transaction(BaseModel):
    id: str
    from_account: str
    to_account: str
    amount: float
    currency: str
    swift_code: str
    timestamp: datetime
    description: str
    status: str = "pending"


class UserProfile(BaseModel):
    customer_id: int
    name: str
    typical_transaction_amount: float
    frequent_recipients: List[str]
    risk_tolerance: str
    last_login: datetime
    transaction_history: List[Transaction]


class CounterpartyInfo(BaseModel):
    swift_code: str
    bank_name: str
    country: str
    verified: bool
    risk_level: int = Field(ge=0, le=10)


class EnhancedDatabaseConn:
    """Enhanced database with financial entities and transaction history."""
    
    def __init__(self):
        self.users = {
            123: UserProfile(
                customer_id=123,
                name="John Smith",
                typical_transaction_amount=500.0,
                frequent_recipients=["CHASUS33", "DEUTDEFF"],
                risk_tolerance="medium",
                last_login=datetime.now() - timedelta(hours=2),
                transaction_history=[
                    Transaction(
                        id="TXN001",
                        from_account="US123456789",
                        to_account="DE987654321",
                        amount=450.0,
                        currency="USD",
                        swift_code="DEUTDEFF",
                        timestamp=datetime.now() - timedelta(days=1),
                        description="Monthly rent payment",
                        status="completed"
                    ),
                    Transaction(
                        id="TXN002",
                        from_account="US123456789",
                        to_account="GB555666777",
                        amount=1200.0,
                        currency="USD",
                        swift_code="BARCGB22",
                        timestamp=datetime.now() - timedelta(days=3),
                        description="Business payment",
                        status="completed"
                    )
                ]
            ),
            456: UserProfile(
                customer_id=456,
                name="Alice Johnson",
                typical_transaction_amount=2000.0,
                frequent_recipients=["BARCGB22", "BNPAFRPP"],
                risk_tolerance="low",
                last_login=datetime.now() - timedelta(minutes=30),
                transaction_history=[]
            )
        }
        
        self.counterparties = {
            "CHASUS33": CounterpartyInfo(
                swift_code="CHASUS33",
                bank_name="JPMorgan Chase Bank",
                country="US",
                verified=True,
                risk_level=1
            ),
            "DEUTDEFF": CounterpartyInfo(
                swift_code="DEUTDEFF",
                bank_name="Deutsche Bank AG",
                country="DE",
                verified=True,
                risk_level=2
            ),
            "BARCGB22": CounterpartyInfo(
                swift_code="BARCGB22",
                bank_name="Barclays Bank PLC",
                country="GB",
                verified=True,
                risk_level=1
            ),
            "UNKNOWN1": CounterpartyInfo(
                swift_code="UNKNOWN1",
                bank_name="Unknown Bank",
                country="XX",
                verified=False,
                risk_level=9
            )
        }
        
        self.audit_log = []

    async def get_user_profile(self, customer_id: int) -> Optional[UserProfile]:
        return self.users.get(customer_id)

    async def get_counterparty_info(self, swift_code: str) -> Optional[CounterpartyInfo]:
        return self.counterparties.get(swift_code)

    async def validate_swift_code(self, swift_code: str) -> bool:
        """Validate SWIFT code format and existence."""
        # Basic SWIFT code format validation (8 or 11 characters)
        pattern = r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'
        if not re.match(pattern, swift_code):
            return False
        
        # Check if counterparty exists in our database
        return swift_code in self.counterparties

    async def analyze_transaction_risk(self, customer_id: int, transaction: Transaction) -> Dict:
        """Analyze transaction risk based on user patterns and counterparty info."""
        user = await self.get_user_profile(customer_id)
        if not user:
            return {"risk_score": 10, "reasons": ["Unknown customer"]}
        
        risk_factors = []
        risk_score = 0
        
        # Amount analysis
        if transaction.amount > user.typical_transaction_amount * 5:
            risk_factors.append("Transaction amount significantly higher than typical")
            risk_score += 3
        
        # Counterparty analysis
        counterparty = await self.get_counterparty_info(transaction.swift_code)
        if counterparty:
            if not counterparty.verified:
                risk_factors.append("Unverified counterparty")
                risk_score += 4
            risk_score += counterparty.risk_level
        else:
            risk_factors.append("Unknown counterparty")
            risk_score += 5
        
        # Frequency analysis
        if transaction.swift_code not in user.frequent_recipients:
            risk_factors.append("New recipient")
            risk_score += 1
        
        # Pattern analysis
        recent_transactions = [t for t in user.transaction_history 
                             if t.timestamp > datetime.now() - timedelta(days=7)]
        if len(recent_transactions) > 10:
            risk_factors.append("High transaction frequency")
            risk_score += 2
        
        return {
            "risk_score": min(risk_score, 10),
            "reasons": risk_factors,
            "counterparty_verified": counterparty.verified if counterparty else False
        }

    async def log_audit_event(self, event_type: str, customer_id: int, details: Dict):
        """Log audit events for compliance."""
        self.audit_log.append({
            "timestamp": datetime.now(),
            "event_type": event_type,
            "customer_id": customer_id,
            "details": details
        })


@dataclass
class EnhancedSupportDependencies:
    customer_id: int
    db: EnhancedDatabaseConn


class EnhancedSupportOutput(BaseModel):
    support_advice: str = Field(description='Detailed advice returned to the customer')
    block_card: bool = Field(description='Whether to block their card')
    approve_transaction: bool = Field(description='Whether to approve pending transaction')
    risk_score: int = Field(description='Overall risk assessment', ge=0, le=10)
    compliance_notes: str = Field(description='Notes for compliance and audit')
    recommended_actions: List[str] = Field(description='Recommended follow-up actions')


enhanced_support_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=EnhancedSupportDependencies,
    output_type=EnhancedSupportOutput,
    system_prompt=(
        'You are an advanced banking security agent with expertise in transaction verification, '
        'fraud detection, and compliance. You help customers while maintaining the highest '
        'security standards. Always verify transactions thoroughly, assess risk levels, '
        'and provide detailed compliance documentation. Use the customer\'s name and be '
        'professional yet helpful.'
    ),
)


@enhanced_support_agent.system_prompt
async def add_customer_context(ctx: RunContext[EnhancedSupportDependencies]) -> str:
    """Add customer context and profile information."""
    user = await ctx.deps.db.get_user_profile(ctx.deps.customer_id)
    if not user:
        return "Customer not found in database"
    
    return f"""
    Customer Profile:
    - Name: {user.name}
    - Risk Tolerance: {user.risk_tolerance}
    - Typical Transaction Amount: ${user.typical_transaction_amount:.2f}
    - Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M')}
    - Recent Transaction Count: {len(user.transaction_history)}
    """


@enhanced_support_agent.tool
async def validate_swift_transaction(
    ctx: RunContext[EnhancedSupportDependencies],
    swift_code: str,
    amount: float,
    currency: str = "USD",
    description: str = "Transfer"
) -> str:
    """Validate a SWIFT transaction for security and compliance."""
    
    # Validate SWIFT code format
    if not await ctx.deps.db.validate_swift_code(swift_code):
        return f"❌ Invalid SWIFT code: {swift_code}. Transaction cannot be processed."
    
    # Create transaction object for analysis
    transaction = Transaction(
        id=f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}",
        from_account=f"US{ctx.deps.customer_id:09d}",
        to_account="PENDING",
        amount=amount,
        currency=currency,
        swift_code=swift_code,
        timestamp=datetime.now(),
        description=description
    )
    
    # Analyze risk
    risk_analysis = await ctx.deps.db.analyze_transaction_risk(
        ctx.deps.customer_id, transaction
    )
    
    # Get counterparty information
    counterparty = await ctx.deps.db.get_counterparty_info(swift_code)
    
    # Log audit event
    await ctx.deps.db.log_audit_event(
        "TRANSACTION_VALIDATION",
        ctx.deps.customer_id,
        {
            "swift_code": swift_code,
            "amount": amount,
            "risk_score": risk_analysis["risk_score"],
            "approved": risk_analysis["risk_score"] <= 6
        }
    )
    
    result = f"""
    🏦 SWIFT Transaction Validation Report
    
    Transaction Details:
    - SWIFT Code: {swift_code}
    - Bank: {counterparty.bank_name if counterparty else 'Unknown'}
    - Country: {counterparty.country if counterparty else 'Unknown'}
    - Amount: {currency} {amount:,.2f}
    - Risk Score: {risk_analysis['risk_score']}/10
    
    Security Assessment:
    - Counterparty Verified: {'✅' if risk_analysis.get('counterparty_verified') else '❌'}
    - Risk Factors: {', '.join(risk_analysis['reasons']) if risk_analysis['reasons'] else 'None detected'}
    
    Recommendation: {'✅ APPROVED' if risk_analysis['risk_score'] <= 6 else '⚠️ REQUIRES REVIEW'}
    """
    
    return result


@enhanced_support_agent.tool
async def check_transaction_history(
    ctx: RunContext[EnhancedSupportDependencies],
    days: int = 30
) -> str:
    """Check customer's transaction history for patterns and anomalies."""
    
    user = await ctx.deps.db.get_user_profile(ctx.deps.customer_id)
    if not user:
        return "Customer profile not found"
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_transactions = [
        t for t in user.transaction_history 
        if t.timestamp > cutoff_date
    ]
    
    if not recent_transactions:
        return f"No transactions found in the last {days} days"
    
    # Analyze patterns
    total_amount = sum(t.amount for t in recent_transactions)
    avg_amount = total_amount / len(recent_transactions)
    recipients = set(t.swift_code for t in recent_transactions)
    
    # Detect anomalies
    anomalies = []
    for transaction in recent_transactions:
        if transaction.amount > avg_amount * 3:
            anomalies.append(f"High amount: ${transaction.amount:,.2f} on {transaction.timestamp.strftime('%Y-%m-%d')}")
    
    await ctx.deps.db.log_audit_event(
        "HISTORY_REVIEW",
        ctx.deps.customer_id,
        {
            "days_reviewed": days,
            "transaction_count": len(recent_transactions),
            "total_amount": total_amount,
            "anomalies_found": len(anomalies)
        }
    )
    
    return f"""
    📊 Transaction History Analysis ({days} days)
    
    Summary:
    - Total Transactions: {len(recent_transactions)}
    - Total Amount: ${total_amount:,.2f}
    - Average Amount: ${avg_amount:,.2f}
    - Unique Recipients: {len(recipients)}
    
    Recent Transactions:
    {chr(10).join([f"• {t.timestamp.strftime('%Y-%m-%d')}: ${t.amount:,.2f} to {t.swift_code} - {t.description}" for t in recent_transactions[-5:]])}
    
    Anomalies Detected:
    {chr(10).join([f"⚠️ {anomaly}" for anomaly in anomalies]) if anomalies else "✅ No anomalies detected"}
    """


@enhanced_support_agent.tool
async def verify_counterparty_identity(
    ctx: RunContext[EnhancedSupportDependencies],
    swift_code: str
) -> str:
    """Verify counterparty identity and assess risk level."""
    
    counterparty = await ctx.deps.db.get_counterparty_info(swift_code)
    
    if not counterparty:
        await ctx.deps.db.log_audit_event(
            "COUNTERPARTY_VERIFICATION",
            ctx.deps.customer_id,
            {"swift_code": swift_code, "result": "NOT_FOUND"}
        )
        return f"❌ Counterparty {swift_code} not found in verified database. HIGH RISK - Manual verification required."
    
    await ctx.deps.db.log_audit_event(
        "COUNTERPARTY_VERIFICATION",
        ctx.deps.customer_id,
        {
            "swift_code": swift_code,
            "verified": counterparty.verified,
            "risk_level": counterparty.risk_level
        }
    )
    
    risk_description = {
        1: "Very Low Risk",
        2: "Low Risk", 
        3: "Medium Risk",
        4: "Medium-High Risk",
        5: "High Risk"
    }.get(counterparty.risk_level, "Critical Risk")
    
    return f"""
    🔍 Counterparty Identity Verification
    
    SWIFT Code: {swift_code}
    Bank Name: {counterparty.bank_name}
    Country: {counterparty.country}
    Verification Status: {'✅ VERIFIED' if counterparty.verified else '❌ UNVERIFIED'}
    Risk Level: {counterparty.risk_level}/10 ({risk_description})
    
    {'✅ Safe to proceed with transaction' if counterparty.verified and counterparty.risk_level <= 3 else '⚠️ Additional verification recommended'}
    """


@enhanced_support_agent.tool
async def detect_transaction_errors(
    ctx: RunContext[EnhancedSupportDependencies],
    amount: float,
    description: str
) -> str:
    """Detect potential errors in transaction requests using goal inference."""
    
    user = await ctx.deps.db.get_user_profile(ctx.deps.customer_id)
    if not user:
        return "Cannot analyze - customer profile not found"
    
    errors_detected = []
    
    # Check for decimal point errors (too many or too few zeros)
    if amount > user.typical_transaction_amount * 10:
        errors_detected.append(f"Amount ${amount:,.2f} is {amount/user.typical_transaction_amount:.1f}x your typical transaction")
    
    # Check for round number patterns that might indicate errors
    if amount >= 1000 and amount % 1000 == 0:
        errors_detected.append("Round thousand amount - verify this is intentional")
    
    # Check for description/amount mismatch
    description_lower = description.lower()
    if any(word in description_lower for word in ['coffee', 'lunch', 'snack']) and amount > 50:
        errors_detected.append("Description suggests small purchase but amount is large")
    
    # Check for extra zeros
    amount_str = str(amount)
    if amount_str.count('0') >= 3:
        errors_detected.append("Multiple zeros detected - verify amount is correct")
    
    await ctx.deps.db.log_audit_event(
        "ERROR_DETECTION",
        ctx.deps.customer_id,
        {
            "amount": amount,
            "description": description,
            "errors_found": len(errors_detected)
        }
    )
    
    if not errors_detected:
        return f"✅ No errors detected in transaction: ${amount:,.2f} for '{description}'"
    
    return f"""
    ⚠️ Potential Transaction Errors Detected
    
    Amount: ${amount:,.2f}
    Description: {description}
    
    Issues Found:
    {chr(10).join([f"• {error}" for error in errors_detected])}
    
    Recommendation: Please verify these details before proceeding.
    """


if __name__ == '__main__':
    # Initialize enhanced database
    db = EnhancedDatabaseConn()
    deps = EnhancedSupportDependencies(customer_id=123, db=db)
    
    print("=== Enhanced Banking Agent MVP Demo ===\n")
    
    # Demo 1: Basic support inquiry
    print("1. Basic Account Status and Activity Inquiry:")
    result = enhanced_support_agent.run_sync(
        "Hi, I need to check my account status and recent activity", 
        deps=deps
    )
    print(f"Response: {result.output.support_advice}")
    print(f"Risk Score: {result.output.risk_score}/10")
    print(f"Compliance Notes: {result.output.compliance_notes}\n")
    
    # Demo 2: SWIFT transaction validation
    print("2. SWIFT Transaction Validation:")
    result = enhanced_support_agent.run_sync(
        "I want to transfer $15000 to SWIFT code DEUTDEFF for business payment", 
        deps=deps
    )
    print(f"Response: {result.output.support_advice}")
    print(f"Approve Transaction: {result.output.approve_transaction}")
    print(f"Risk Score: {result.output.risk_score}/10")
    print(f"Recommended Actions: {result.output.recommended_actions}\n")
    
    # Demo 3: Suspicious transaction detection
    print("3. Suspicious Transaction Detection:")
    result = enhanced_support_agent.run_sync(
        "I need to send $50000 to UNKNOWN1 bank for urgent business matter", 
        deps=deps
    )
    print(f"Response: {result.output.support_advice}")
    print(f"Block Card: {result.output.block_card}")
    print(f"Risk Score: {result.output.risk_score}/10")
    print(f"Compliance Notes: {result.output.compliance_notes}\n")
    
    # Demo 4: Error detection
    print("4. Transaction Error Detection:")
    result = enhanced_support_agent.run_sync(
        "I want to pay $10000 for coffee with my friend", 
        deps=deps
    )
    print(f"Response: {result.output.support_advice}")
    print(f"Risk Score: {result.output.risk_score}/10")
    print(f"Recommended Actions: {result.output.recommended_actions}\n")
    
    print("=== Demo Complete ===")