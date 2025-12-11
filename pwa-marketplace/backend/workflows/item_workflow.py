# Item Workflow definition for Temporal
from temporalio import workflow
from datetime import timedelta
from temporalio.workflow import ExternalWorkflowHandle # New: Required for signaling external workflows
from typing import Optional # New: Required for type hinting the external handle

# ITEM_STATUS_CODES = [
#        'open', 'paid', 'pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
#        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
#        'refunded', 'partial_refunded', 'customer_accepted'
# ]

@workflow.defn
class ItemWorkflow:
    def __init__(self):
        self.item_id = None
        self.current_status = "open"
        self._parent_handle: Optional[ExternalWorkflowHandle] = None # New: Store the Parent's external handle

    @workflow.run
    async def run(self, item_id: int, parent_workflow_id: str): # New: Added parent_workflow_id
        self.item_id = item_id
        
        # New: Get a handle to the Parent Order Workflow using the ID passed from the parent
        self._parent_handle = workflow.get_external_workflow_handle(parent_workflow_id)

        workflow.logger.info(f"Item Workflow {item_id} started. Signaling status code changes to Parent ID: {parent_workflow_id}")
        
        # MOCK: Simulate item processing lifecycle for demonstration
        # In reality, this would wait for signals like "filled", "shipped", etc
        
        # New: Initial status change (eg: to 'paid') and signal the parent
        await self.set_status("paid") 
        # New: Simulate further processing
        await workflow.sleep(5)
        await self.set_status("shipped")

        # Wait until the item reaches the final state
        await workflow.wait_condition(lambda: self.current_status == "customer_accepted")
        
        workflow.logger.info(f"Item Workflow {item_id} finished with status: {self.current_status}")


    async def _signal_parent_status_change(self):
        """New Helper: Sends a Signal to the Parent Order Workflow."""
        if self._parent_handle and self.item_id is not None:
            # Signal the Parent's handler (e.g., 'update_child_status')
            await self._parent_handle.signal(
                "update_child_status", # This signal name must be defined in OrderWorkflow
                self.item_id,
                self.current_status
            )
            workflow.logger.info(f"Item {self.item_id} signaled parent with status: {self.current_status}")
        elif not self._parent_handle:
             workflow.logger.warn(f"Item {self.item_id} cannot signal parent, handle is missing.")


    # --- QUERIES (Parent calls these to check status) ---
    @workflow.query
    def get_status(self) -> str:
        return self.current_status

    # --- SIGNALS (Parent calls these to change state) ---
    @workflow.signal
    async def set_status(self, new_status: str):
        """New Generic Signal: Updates status and notifies the parent."""
        if self.current_status != new_status:
            self.current_status = new_status
            if self.item_id is not None:
                await self._signal_parent_status_change()
    
    @workflow.signal
    async def cancel_item(self):
        # Add logic here: e.g., if already shipped, cannot cancel easily
        if self.current_status not in ["shipped", "delivered"]:
            # Changed to use the new generic set_status which handles the parent signal
            await self.set_status("cancelled") 
            workflow.logger.info(f"Item {self.item_id} cancelled via signal.")
        else:
            workflow.logger.warn(f"Cannot cancel Item {self.item_id}, it is already {self.current_status}")

    # @workflow.signal
    # async def ... (self):
    #     pass