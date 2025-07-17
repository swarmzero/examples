import os
import uuid

from swarmzero.agent import Agent
from swarmzero.sdk_context import SDKContext
from swarmzero.workflow import Workflow, WorkflowStep, StepMode

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "swarmzero_config.toml")
sdk_context = SDKContext(CONFIG_PATH)

# Agent 1: Greeting Agent
greeting_agent = Agent(
    name="greeting_agent",
    functions=[],  # no tools needed for simple greeting
    instruction="You are a friendly customer service representative. Greet customers warmly and ask how you can help them.",
    sdk_context=sdk_context,
    agent_id=str(uuid.uuid4()),
    role="Customer Service Greeter",
    description="Handles initial customer greetings and introductions"
)

# Agent 2: Issue Classification Agent
def classify_issue_type(issue_description: str) -> str:
    """Classify the type of customer issue based on description."""
    # this could be a more sophisticated classification function
    if any(word in issue_description.lower() for word in ["bill", "payment", "charge", "invoice"]):
        return "billing"
    elif any(word in issue_description.lower() for word in ["broken", "error", "not working", "technical"]):
        return "technical"
    elif any(word in issue_description.lower() for word in ["refund", "return", "cancel"]):
        return "refund"
    else:
        return "general"

classification_agent = Agent(
    name="classification_agent",
    functions=[classify_issue_type],
    instruction="You are an expert at analyzing customer issues and classifying them into appropriate categories. Use the classify_issue_type function to categorize the issue.",
    agent_id=str(uuid.uuid4()),
    role="Issue Classifier",
    sdk_context=sdk_context,
    description="Analyzes and categorizes customer issues"
)

# Agent 3: Billing Support Agent
def check_billing_status(account_id: str) -> dict:
    """Check customer's billing status and recent charges."""
    # simulate billing system check
    return {
        "account_id": account_id,
        "balance": "$150.00",
        "last_payment": "2024-01-15",
        "next_bill": "2024-02-15",
        "status": "current"
    }

def process_payment(amount: float, payment_method: str) -> dict:
    """Process a payment for the customer."""
    # simulate payment processing
    return {
        "transaction_id": "txn_12345",
        "amount": amount,
        "status": "completed",
        "payment_method": payment_method
    }

billing_agent = Agent(
    name="billing_agent",
    functions=[check_billing_status, process_payment],
    instruction="You are a billing specialist. Help customers with payment issues, check their account status, and process payments when needed.",
    agent_id=str(uuid.uuid4()),
    sdk_context=sdk_context,
    role="Billing Specialist",
    description="Handles all billing-related customer inquiries and transactions"
)

# Agent 4: Technical Support Agent
def check_system_status(system_name: str) -> dict:
    """Check the status of various systems."""
    # simulate system status check
    return {
        "system": system_name,
        "status": "operational",
        "last_updated": "2024-01-20T10:30:00Z"
    }

def create_support_ticket(issue_description: str, priority: str = "medium") -> dict:
    """Create a technical support ticket."""
    # simulate ticket creation
    return {
        "ticket_id": "TKT-2024-001",
        "description": issue_description,
        "priority": priority,
        "status": "open",
        "created_at": "2024-01-20T10:30:00Z"
    }

technical_agent = Agent(
    name="technical_agent",
    functions=[check_system_status, create_support_ticket],
    instruction="You are a technical support specialist. Help customers with technical issues, check system status, and create support tickets when needed.",
    agent_id=str(uuid.uuid4()),
    sdk_context=sdk_context,
    role="Technical Support Specialist",
    description="Handles technical issues and system troubleshooting"
)

# Define condition functions for conditional routing
def is_billing_issue(result):
    """Check if the classified issue is billing-related."""
    return isinstance(result, str) and "billing" in result.lower()

def is_technical_issue(result):
    """Check if the classified issue is technical-related."""
    return isinstance(result, str) and "technical" in result.lower()

# Create workflow steps
steps = [
    # Step 1: Greet the customer
    WorkflowStep(
        runner=greeting_agent,
        name="Greet Customer",
        mode=StepMode.SEQUENTIAL
    ),
    
    # Step 2: Classify the issue
    WorkflowStep(
        runner=classification_agent,
        name="Classify Issue",
        mode=StepMode.SEQUENTIAL
    ),
    
    # Step 3: Route to appropriate specialist (conditional)
    WorkflowStep(
        runner=billing_agent,
        name="Handle Billing Issue",
        mode=StepMode.CONDITIONAL,
        condition=is_billing_issue
    ),
    
    WorkflowStep(
        runner=technical_agent,
        name="Handle Technical Issue", 
        mode=StepMode.CONDITIONAL,
        condition=is_technical_issue
    )
]

# Main workflow
customer_service_workflow = Workflow(
    name="Customer Service Workflow",
    steps=steps,
    instruction="Handle customer service requests from initial greeting through issue resolution",
    description="A comprehensive customer service workflow that routes customers to appropriate specialists"
)

# Run the workflow
async def handle_customer_request(customer_message: str):
    result = await customer_service_workflow.run(initial_prompt=customer_message)
    return result

# Example usage
import asyncio

async def main():
    # simulate a customer message
    customer_message = "Hi, I'm having trouble with my bill. I was charged twice this month."
    
    result = await handle_customer_request(customer_message)
    print("Workflow result:", result)

# Run the workflow
if __name__ == "__main__":
    asyncio.run(main())
