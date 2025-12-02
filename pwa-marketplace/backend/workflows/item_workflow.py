# Item (Medicine) Workflow definition for Temporal
from temporalio import workflow

ITEM_STATES = [
    "open", "pending", "paid", "filled", "partial_filled", "shipped", "partial_shipped",
    "delivered", "partial_delivered", "cancelled", "partial_cancelled", "returned", "partial_returned",
    "customer_accepted", "refunded"
]

@workflow.defn
class ItemWorkflow:
    @workflow.run
    async def run(self, item_id: int):
        # TODO: Implement item workflow logic, handle delivery, return, etc.
        pass

    # Add signal/query methods as needed for status updates, events, etc.
