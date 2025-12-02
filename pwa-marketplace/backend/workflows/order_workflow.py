# Order Workflow definition for Temporal
from temporalio import workflow
from typing import List

ORDER_STATES = [
    "open", "pending", "paid", "filled", "partial_filled", "shipped", "partial_shipped",
    "delivered", "partial_delivered", "cancelled", "partial_cancelled", "returned", "partial_returned",
    "customer_accepted", "refunded"
]

@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: int, item_ids: List[int]):
        # TODO: Implement order workflow logic, spawn item workflows, aggregate item states
        pass

    # Add signal/query methods as needed for status updates, events, etc.
