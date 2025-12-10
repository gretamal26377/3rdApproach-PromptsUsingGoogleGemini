# Order Workflow definition for Temporal
from datetime import timedelta
from temporalio import workflow
from typing import List
from . import order_activities 

ORDER_STATES = [
    "open", "pending", "paid", "filled", "partial_filled", "shipped", "partial_shipped",
    "delivered", "partial_delivered", "cancelled", "partial_cancelled", "returned", "partial_returned",
    "customer_accepted", "refunded"
]

# FIX 4: Removed unnecessary ActivityCallable definition

@workflow.defn
class OrderWorkflow:
    def __init__(self):
        # Temporal best practice: Use the external activities stub
        self.activities = workflow.get_external_activities(order_activities)
        # Initialize internal state variables
        self.order_id = None
        self.current_status = "open"
    # Purpose: Main entry point for the order workflow
    @workflow.run
    async def run(self, order_id: int, item_ids: List[int]):
        # TODO: Implement order workflow logic, spawn item workflows, aggregate item states
        self.order_id = order_id
        # ... (other initial setup) ...

        # This line tells to Runtime "don't move past this line until condition inside lambda function evaluates to True."
        # Summary: this line is the "sentinel" that keeps workflow process alive, durable, and ready to receive signals
        # until order reaches a final, resolved state
        await workflow.wait_condition(lambda: self.current_status in ["cancelled", "refunded", "delivered"])
        pass

    # Add signal/query methods as needed for status updates, events, etc
    @workflow.signal
    async def cancel_order(self):
        # 1. Update the internal workflow state
        self.current_status = 'cancelled'
        
        # Check self.order_id is set
        if self.order_id is None:
            workflow.logger.warn("Cancel signal received before order_id was set!")
            return

        # 2. Schedule the Activity to reliably synchronize the DB status
        # Reverting to the Stub call (correct for Temporal runtime) and adding type ignore for Pylance
        result = await workflow.execute_activity(
            self.activities.update_order_status_in_db,
            self.order_id,                     # <-- Argument 1: order_id (int)
            'cancelled',                       # <-- Argument 2: new_status_code (str)
            schedule_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info(f"Updated order: {result.order_id} → {result.new_status}")
        # 3. Add compensation/inventory logic here...

    async def ship_order(self):
        # Check self.order_id is set
        if self.order_id is None:
            workflow.logger.warn("Ship order called before order_id was set!")
            return
            
        result = await workflow.execute_activity(
            self.activities.update_order_status_in_db,
            self.order_id, 
            'shipped',
            schedule_to_close_timeout=timedelta(seconds=10),
        ) # type: ignore[call-overload]
        
        workflow.logger.info(f"Updated order: {result.order_id} → {result.new_status}")