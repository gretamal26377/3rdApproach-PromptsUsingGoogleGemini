# Item Workflow definition for Temporal
import asyncio
from temporalio import workflow
from datetime import timedelta
# from temporalio.workflow import ExternalWorkflowHandle # Required for signaling external workflows
from typing import Optional # Required for type hinting the external handle
from . import item_activities # Import the activities file

# ITEM_STATUS_CODES = [
#        'open', 'paid', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
#        'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
#        'refunded', 'partial_refunded', 'customer_accepted'
# ]

@workflow.defn
class ItemWorkflow:
    def __init__(self) -> None:
        self.item_id: int | None = None
        self.order_id: int | None = None
        self.current_status_code = "open"
        # The parent handle is now only used for emergency signals (like full cancellation),
        # NOT for real-time status updates after every step
        self._parent_handle: Optional[workflow.ExternalWorkflowHandle] = None # Store the Parent's external handle
        # This keeps the workflow alive indefinitely until Order Completion or Cancellation
        self._keep_running = True
        # Acceptance timer tracking
        self._acceptance_timer_started = False

    @workflow.run
    async def run(self, item_data: dict, order_id: int, parent_workflow_id: str):
        """
        item_data: dict with all OrderDetails fields except order_id (which is provided separately)
        order_id: int, parent_workflow_id: str
        """
        self.order_id = order_id
        self.item_id = item_data.get('store_product_service_id')
        
        # Get the external handle of the Parent Workflow (needed for the cancel signal)
        self._parent_handle = workflow.get_external_workflow_handle(parent_workflow_id)

        # Persist OrderDetails row via Item Activity
        detail_data = dict(item_data)
        detail_data['order_id'] = order_id
        await workflow.execute_activity(
            item_activities.create_order_detail_in_db,
            detail_data,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Item Workflow {self.item_id} started with status: {self.current_status_code}")
        workflow.logger.info(f"ItemWorkflow: Created OrderDetail for item {self.item_id} in DB")

        # Paid Status Set: OrderWorkflow handles this status transition
        await self.set_status("paid")
        workflow.logger.info(f"Item Workflow {self.item_id} moved to status: {self.current_status_code}")

        # The workflow now waits indefinitely for signals to start a Batch Process 
        # or for a final cancellation
        await workflow.wait_condition(lambda: not self._keep_running)
        
        workflow.logger.info(
            f"Item Workflow {self.item_id} finished with status: {self.current_status_code}"
        )

    # Centralized method for internal and external status changes
    async def set_status(self, new_status_code: str):
        """Updates the internal status"""
        if self.current_status_code != new_status_code:
            workflow.logger.info(f"Item {self.item_id} status internally changed to: {new_status_code}")
            self.current_status_code = new_status_code
            await self._maybe_schedule_acceptance_timer(new_status_code)
            
            # Note: We do NOT signal the parent here. The Parent will QUERY or receive 
            # the status after the Batch Process is complete


    # --- BATCH PHASE HANDLERS (Called by Parent in the batch) ---
    @workflow.signal
    async def fill_item_batch(self) -> None:
        """
        Triggered by the Parent Order Workflow to perform the Filling Batch.
        This runs the Filling Activity and updates its internal status
        """
        if self.current_status_code == "paid":
            workflow.logger.info(f"Item {self.item_id} queuing Filling Activity to be executed")
            assert self.order_id is not None and self.item_id is not None

            # Execute the Activity for filling
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_fill,
                item_activities.ItemActivityInput(order_id=self.order_id, item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (filled or keeps the same paid if it couldn't be processed)
            await self.set_status(result.new_item_status_code)
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped filling, Status Code is {self.current_status_code}"
            )

    @workflow.signal
    async def cancel_item(self):
        """Signal from Parent or external system to cancel this Item"""
        if self.current_status_code in ["open", "paid", "filled", "partial_filled"]:
            await self.set_status("cancelled") 
            self._keep_running = False # End the Item workflow
        else:
            workflow.logger.warn(
                f"Cannot cancel Item {self.item_id}, it is already {self.current_status_code}"
            )

    @workflow.signal
    async def ship_item_batch(self) -> None:
        """
        Triggered by the Parent Order Workflow to perform the Shipping Batch
        """
        if self.current_status_code == "filled":
            workflow.logger.info(f"Item {self.item_id} queuing Shipping Activity to be executed")
            assert self.order_id is not None and self.item_id is not None

            # Execute the Activity for shipment
            result: item_activities.ItemShipmentResult = await workflow.execute_activity(
                item_activities.perform_item_shipment,
                item_activities.ItemActivityInput(order_id=self.order_id, item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )
            # The result contains the new status (filled or keeps the same filled if it couldn't be processed)
            await self.set_status(result.new_item_status_code)
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped shipping, Status Code is {self.current_status_code}"
            )

    @workflow.signal
    async def deliver_item_batch(self) -> None:
        """
        Triggered by the Parent Order Workflow to perform the Delivery Batch
        """
        if self.current_status_code == "shipped":
            workflow.logger.info(f"Item {self.item_id} queuing Delivery Activity to be executed")
            assert self.order_id is not None and self.item_id is not None

            # Execute the Activity for delivery
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_delivery,
                item_activities.ItemActivityInput(order_id=self.order_id, item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (delivered or keeps the same shipped if it couldn't be processed)
            await self.set_status(result.new_item_status_code)
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped delivery, status is {self.current_status_code}"
            )

    @workflow.signal
    async def return_item_batch(self) -> None:
        """Triggered by the Parent Order Workflow to perform the Return Batch"""
        if self.current_status_code == "delivered":
            workflow.logger.info(f"Item {self.item_id} queuing Return Activity to be executed")
            assert self.order_id is not None and self.item_id is not None

            # Execute the Activity for return
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_return,
                item_activities.ItemActivityInput(order_id=self.order_id, item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (returned or keeps the same if it couldn't be processed)
            await self.set_status(result.new_item_status_code)
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped return, status is {self.current_status_code}"
            )

    @workflow.signal
    async def refund_item_batch(self) -> None:
        """Triggered by the Parent Order Workflow to perform the Refund Batch"""
        if self.current_status_code in ["returned", "cancelled"]:
            workflow.logger.info(f"Item {self.item_id} queuing Refund Activity to be executed")
            assert self.order_id is not None and self.item_id is not None

             # Execute the Activity for refund
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_refund,
                item_activities.ItemActivityInput(order_id=self.order_id, item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (delivered or keeps the same if it couldn't be processed)
            await self.set_status(result.new_item_status_code)           # Refund is terminal for the item
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped refund, status is {self.current_status_code}"
            )

    @workflow.signal
    async def accept_item_batch(self) -> None:
        """Triggered by the Parent Order Workflow to perform the Acceptance Batch"""
        if self.current_status_code in ["delivered", "refunded"]:
            workflow.logger.info(f"Item {self.item_id} queuing Acceptance Activity to be executed")
            assert self.order_id is not None and self.item_id is not None

            # Execute the Activity for acceptance
            result: item_activities.ItemActivityOutput = await workflow.execute_activity(
                item_activities.perform_item_acceptance,
                item_activities.ItemActivityInput(order_id=self.order_id, item_id=self.item_id, status_code=self.current_status_code),
                start_to_close_timeout=timedelta(minutes=5),
            )

            # The result contains the new status (customer_accepted or keeps the same if it couldn't be processed)
            await self.set_status(result.new_item_status_code)

            # Acceptance is terminal for the Item
            self._keep_running = False
        else:
            workflow.logger.warning(
                f"Item {self.item_id} skipped acceptance, status is {self.current_status_code}"
            )

    # --- INTERNAL: Schedule Acceptance after 10 days of Delivered/Refunded ---
    async def _maybe_schedule_acceptance_timer(self, status_code: str):
        """
        When the Item reaches delivered/refunded status code, start a one-time 10-day timer.
        After it fires, if still eligible and workflow alive, signal Parent start_acceptance
        """
        if status_code not in ["delivered", "refunded"]:
            return
        if self._acceptance_timer_started:
            return
        if not self._parent_handle:
            workflow.logger.warning(f"Item {self.item_id} cannot schedule Acceptance Timer: Missing Parent Handle")
            return

        self._acceptance_timer_started = True
        deadline = workflow.now() + timedelta(days=10)
        handle = self._parent_handle

        async def _timer_task():
            # Sleep until deadline; Temporal timers are durable
            delay = (deadline - workflow.now()).total_seconds()
            if delay > 0:
                await workflow.sleep(delay)
            # Re-check eligibility and liveness
            if not self._keep_running:
                return
            if self.current_status_code not in ["delivered", "refunded"]:
                return
            try:
                workflow.logger.info(f"Item {self.item_id} timer elapsed; signaling Parent for Acceptance")
                await handle.signal("start_acceptance")
            except Exception as e:
                workflow.logger.warning(f"Item {self.item_id} Acceptance Signal failed after Timer reached deadline: {e}")

        # Fire-and-forget timer task
        asyncio.create_task(_timer_task())  # type: ignore[attr-defined]


    # --- QUERIES (Parent calls these to check status) ---
    @workflow.query
    def get_status(self) -> str:
        return self.current_status_code
