# Item Workflow definition for Temporal
import asyncio
from temporalio import workflow
from datetime import timedelta
from temporalio.workflow import ExternalWorkflowHandle # New: Required for signaling external workflows
from typing import Optional # New: Required for type hinting the external handle
from . import item_activities # Import the new activities file

# ITEM_STATUS_CODES = [
#        'open', 'paid', 'pending', 'partial_pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
#        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
#        'refunded', 'partial_refunded', 'customer_accepted'
# ]

@workflow.defn
class ItemWorkflow:
    def __init__(self):
        self.item_id = None
        self.current_status_code = "open"
        self._parent_handle: Optional[ExternalWorkflowHandle] = None # New: Store the Parent's external handle

    @workflow.run
    async def run(self, item_id: int, parent_workflow_id: str): # New: Added parent_workflow_id
        self.item_id = item_id
        self.parent_workflow_id = parent_workflow_id

        workflow.logger.info(f"Item Workflow {item_id} started. Signaling status code changes to Parent ID: {parent_workflow_id}")
        
        # 1. Initial Signal: Let Parent know the Item exists and is "pending"
        await self._signal_parent_status_change()

        # --- STAGE 1: Fulfillment ---
        # The workflow waits until an external system (or Parent) sends a signal to start/cancel.
        await workflow.wait_condition(lambda: self.current_status_code in ["filled", "cancelled"])
        await self._signal_parent_status_change() # Signal Parent after status transition

        if self.current_status_code == "filled":
            # Execute Activity for fulfillment
            activity_input = item_activities.ItemActivityInput(item_id=self.item_id, status=self.current_status_code)
            await workflow.execute_activity(
                self.activities.perform_item_fulfillment,
                activity_input,
                schedule_to_close_timeout=timedelta(seconds=60),
            )
        else:
            return # Workflow completes if cancelled early

        # --- STAGE 2: Shipping Handoff ---
        # Waits again for an external event (e.g., Warehouse confirms packaging is done)
        await workflow.wait_condition(lambda: self.current_status_code in ["shipped", "cancelled"])
        await self._signal_parent_status_change() # Signal Parent after status transition

        if self.current_status_code == "shipped":
            # Execute Activity for shipping label/handoff
            activity_input = item_activities.ItemActivityInput(item_id=self.item_id, status=self.current_status_code)
            await workflow.execute_activity(
                self.activities.handle_shipment_handoff,
                activity_input,
                schedule_to_close_timeout=timedelta(seconds=60),
            )
        else:
            return # Workflow completes if cancelled or not shipped

        # --- STAGE 3: Delivery ---
        # Waits for delivery confirmation event
        await workflow.wait_condition(lambda: self.current_status_code in ["delivered", "returned", "cancelled"])
        await self._signal_parent_status_change() # Signal Parent after final status transition

        # Wait until the item reaches the final status
        await workflow.wait_condition(lambda: self.current_status_code == "customer_accepted")

        workflow.logger.info(f"Item Workflow {item_id} finished with status code: {self.current_status_code}")

    async def _signal_parent_status_change(self):
        """Helper: Sends a Signal to the Parent Order Workflow."""
        if self._parent_handle and self.item_id is not None:
            # Get a handle to the Parent Workflow using its ID
            parent_handle = workflow.get_external_workflow_handle(self.parent_workflow_id)
            
            # Signal the Parent's dedicated signal handler (e.g., 'update_child_status')
            # The Parent will immediately react to this event
            await self._parent_handle.signal(
                "update_child_status", # This signal name must be defined in OrderWorkflow
                self.item_id,
                self.current_status_code
            )
            workflow.logger.info(f"Item {self.item_id} signaled Parent {self.parent_workflow_id} with new status code: {self.current_status_code}")

        elif not self._parent_handle:
             workflow.logger.warn(f"Item {self.item_id} cannot signal Parent, handle is missing")


    # --- QUERIES (Parent calls these to check status) ---
    @workflow.query
    def get_status(self) -> str:
        return self.current_status_code

    # --- SIGNALS (Received from external systems or Parent to PUSH status changes) ---
    @workflow.signal
    async def set_status(self, new_status_code: str):
        """Generic Signal: Updates status and notifies the Parent"""
        if self.current_status_code != new_status_code:
            self.current_status_code = new_status_code
            if self.item_id is not None:
                await self._signal_parent_status_change()
    
    @workflow.signal
    async def fulfill_item(self):
        """External signal to mark item as fulfilled/picked."""
        if self.current_status_code == "pending":
            self.current_status_code = "filled"
            # Note: _signal_parent_status_change is called in the run method after wait_condition is lifted

    @workflow.signal
    async def ship_item(self):
        """External signal to mark item as shipped."""
        if self.current_status_code == "filled":
            self.current_status_code = "shipped"

    @workflow.signal
    async def deliver_item(self):
        """External signal to mark item as delivered."""
        if self.current_status_code == "shipped":
            self.current_status_code = "delivered"

    @workflow.signal
    async def cancel_item(self):
        """Signal from Parent or external system to cancel this Item"""
        # Add logic here: e.g., if already shipped, cannot cancel easily
        if self.current_status_code not in ["shipped", "delivered"]:
            # Changed to use the new generic set_status which handles the parent signal
            await self.set_status("cancelled") 
            workflow.logger.info(f"Item {self.item_id} cancelled via signal")
        else:
            workflow.logger.warn(f"Cannot cancel Item {self.item_id}, it is already {self.current_status_code}")
