# Item (Medicine) Workflow definition for Temporal
from temporalio import workflow
from datetime import timedelta

ITEM_STATUS_CODES = [
        'open', 'paid', 'pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
        'refunded', 'partial_refunded', 'customer_accepted'
]
@workflow.defn
class ItemWorkflow:
    def __init__(self):
        self.item_id = None
        self.current_status = "open"

    @workflow.run
    async def run(self, item_id: int):
        self.item_id = item_id
        workflow.logger.info(f"Item Workflow {item_id} started")
        
        # MOCK: Simulate item processing lifecycle for demonstration
        # In reality, this would wait for signals like "picked", "shipped", etc.
        
        # Wait until the item reaches a final status
        await workflow.wait_condition(lambda: self.current_status in ["delivered", "cancelled", "returned", "refunded"])
        
        workflow.logger.info(f"Item Workflow {item_id} finished with status: {self.current_status}")

    # --- QUERIES (Parent calls these to check status) ---
    @workflow.query
    def get_status(self) -> str:
        return self.current_status

    # --- SIGNALS (Parent calls these to change status) ---
    @workflow.signal
    async def cancel_item(self):
        # Add logic here: e.g., if already shipped, cannot cancel easily
        if self.current_status not in ["shipped", "delivered"]:
            self.current_status = "cancelled"
            workflow.logger.info(f"Item {self.item_id} cancelled via signal.")
        else:
            workflow.logger.warn(f"Cannot cancel Item {self.item_id}, it is already {self.current_status}")

    @workflow.signal
    async def mark_shipped(self):
        self.current_status = "shipped"
        
    @workflow.signal
    async def mark_delivered(self):
        self.current_status = "delivered"