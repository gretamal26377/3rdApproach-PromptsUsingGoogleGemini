# Order Workflow definition for Temporal
from datetime import timedelta
from temporalio import workflow
from typing import List
# Relative import to pull in the activities file in the same directory
from . import order_activities

ORDER_STATES = [
    "open", "pending", "paid", "filled", "partial_filled", "shipped", "partial_shipped",
    "delivered", "partial_delivered", "cancelled", "partial_cancelled", "returned", "partial_returned",
    "customer_accepted", "refunded"
]

@workflow.defn
class OrderWorkflow:
    def __init__(self):
        # This registers the activities with the workflow
        self.activities = workflow.get_external_activities(order_activities)
        # Initialize internal state variables
        self.order_id = None
        self.current_status = "open"
    @workflow.run
    async def run(self, order_id: int, item_ids: List[int]):
        # TODO: Implement order workflow logic, spawn item workflows, aggregate item states
        self.order_id = order_id
        # ... (other initial setup) ...
        # Keep the workflow alive until signalled to cancel/complete
        await workflow.wait_condition(lambda: self.current_status in ["cancelled", "refunded", "delivered"])
        pass

    # Add signal/query methods as needed for status updates, events, etc.
    @workflow.signal
    async def cancel_order(self):
        # 1. Update the internal workflow state
        self.current_status = 'cancelled'
        
        # 2. Schedule the Activity to reliably synchronize the DB status
        result = await workflow.execute_activity(
            self.activities.update_order_status_in_db,
            self.order_id,
            'cancelled',
            schedule_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Updated order: {result.order_id} → {result.new_status}")
        # 3. Add compensation/inventory logic here...

    async def ship_order(self):
        self.current_status = 'shipped'
        await workflow.execute_activity(
            self.activities.update_order_status_in_db,
            self.order_id,
            'shipped',
            schedule_to_close_timeout=timedelta(seconds=10),
    )

