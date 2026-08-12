from typing import TypedDict, Optional, List, Dict, Any


class SupportState(TypedDict, total=False):
    # User information
    user_query: str
    customer_id: str
    order_id: Optional[str]

    # Classification
    intent: str
    confidence: float

    # Data collected from tools
    order_details: Dict[str, Any]
    policy_result: str

    #refund information
    refund_required: bool
    refund_eligible: bool
    requires_human_approval: bool
    refund_amount: float
    refund_reason: str
    refund_approved: bool

    
    # Conversation / workflow control
    messages: List[Dict[str, str]]
    error: Optional[str]

    resolution: str
    messages: list

   