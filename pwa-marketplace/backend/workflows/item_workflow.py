# Item Workflow definition for Temporal
import asyncio
from temporalio import workflow
from datetime import timedelta
# from temporalio.workflow import ExternalWorkflowHandle # Required for signaling external workflows
from typing import Optional # Required for type hinting the external handle
from . import item_activities # Import the activities file

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
        # The parent handle is now only used for emergency signals (like full cancellation), 
        # NOT for real-time status updates after every step
        self._parent_handle: Optional[workflow.ExternalWorkflowHandle] = None # Store the Parent's external handle
        # This keeps the workflow alive indefinitely until Order Completion or Cancellation
        self._keep_running = True

    @workflow.run
    async def run(self, item_id: int, parent_workflow_id: str): # New: Added parent_workflow_id
        self.item_id = item_id
        # self.parent_workflow_id = parent_workflow_id
        
        # Get the external handle of the Parent Workflow (needed for the cancel signal)
        self._parent_handle = workflow.get_external_workflow_handle(parent_workflow_id)

        # Initial status set: OrderWorkflow handles the initial status transition
        await self.set_status("paid")
        workflow.logger.info(f"Item Workflow {item_id} started with status: {self.current_status_code}")

        # The workflow now waits indefinitely for signals to start a Batch Process 
        # or for a final cancellation
        await workflow.wait_condition(lambda: not self._keep_running)
        
        workflow.logger.info(
            f"Item Workflow {item_id} finished with status: {self.current_status_code}"
        )

    # Centralized method for internal and external status changes
    async def set_status(self, new_status_code: str):
        """Updates the internal status"""
        if self.current_status_code != new_status_code:
            workflow.logger.info(f"Item {self.item_id} status internally changed to: {new_status_code}")
            self.current_status_code = new_status_code
            
            # Note: We do NOT signal the parent here. The Parent will QUERY or receive 
            # the status after the Batch Process is complete


    # --- BATCH PHASE HANDLERS (Called by Parent in the batch) ---
    @workflow.signal
    async def fill_item_batch(self):
        """
        Triggered by the Parent Order Workflow to perform the filling batch.
        This runs the Filling Activity and updates its internal status
        """
        if self.current_status_code == "paid":
            workflow.logger.info(f"Item {self.item_id} executing fulfillment Activity")

            # Execute the Activity for filling
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_fill,
                item_activities.ItemActivityInput(item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (filled or former status if not processable)
            await self.set_status(result.new_item_status_code)
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped fulfillment, Status Code is {self.current_status_code}"
            )

    @workflow.signal
    async def ship_item_batch(self):
        """
        Triggered by the Parent Order Workflow to perform the shipping batch
        """
        if self.current_status_code == "filled":
            workflow.logger.info(f"Item {self.item_id} executing shipment Activity")

            # Execute the Activity for shipment
            await workflow.execute_activity(
                item_activities.process_item_shipment,
                self.item_id,
                start_to_close_timeout=timedelta(minutes=5),
            )
            # Shipment activity is assumed successful if it returns. Update status
            await self.set_status("shipped")
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped shipping, status is {self.current_status_code}"
            )

    @workflow.signal
    async def deliver_item_batch(self):
        """
        Triggered by the Parent Order Workflow to perform the delivery batch
        """
        if self.current_status_code == "shipped":
            workflow.logger.info(f"Item {self.item_id} executing delivery Activity")

            # Execute the Activity for delivery
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_delivery,
                item_activities.ItemActivityInput(item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (delivered or former status if not processable)
            await self.set_status(result.new_item_status_code)
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped delivery, status is {self.current_status_code}"
            )

    # --- CANCEL STATUS ---
    @workflow.signal
    async def cancel_item(self):
        """Signal from Parent or external system to cancel this Item"""
        if self.current_status_code not in ["open", "paid", "filled", "partial_filled", "pending", "partial_pending"]:
            await self.set_status("cancelled") 
            self._keep_running = False # End the Item workflow
        else:
            workflow.logger.warn(
                f"Cannot cancel Item {self.item_id}, it is already {self.current_status_code}"
            )

    # --- QUERIES (Parent calls these to check status) ---
    @workflow.query
    def get_status(self) -> str:
        return self.current_status_code
