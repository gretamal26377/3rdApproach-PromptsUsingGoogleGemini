import asyncio
from datetime import timedelta
from temporalio import workflow
from typing import List, Dict
from . import order_activities 
from .item_workflow import ItemWorkflow

# ORDER_STATUS_CODES = [
#    'open', 'paid', 'pending' (means Order's paused, needs manual intervention), 'filled', 'partial_filled', 'shipped', 'partial_shipped',
#    'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
#    'refunded', 'partial_refunded', 'customer_accepted'
# ]

# Declares a class as a Temporal Workflow
@workflow.defn
class OrderWorkflow:
    # init runs when a new instance of the workflow is created before @workflow.run
    # self refers to the specific class/object instance being created
    def __init__(self) -> None:
        # Initialize internal status variables
        self.order_id: int | None = None    # placeholder; real value always assigned in run()
        self.current_status_code = "open"
        # Stores item IDs and their corresponding ItemWorkflowHandles
        self.item_handles: Dict[int, workflow.ExternalWorkflowHandle[ItemWorkflow]] = {}
        # Control flag to prevent other phase signals (like cancellation) during a batch run
        self.is_busy = False 
        self._keep_running = True
        # Tracks the background refund timer task after a return is completed/requested
        self._refund_timer_task: asyncio.Task | None = None

    @workflow.run
    async def run(self, order_input: dict):
        """
        order_input: dict with keys:
            - customer_id
            - order_tot_quantity
            - order_tot_price
            - order_created_at
            - items: list of dicts (all OrderDetails fields)
        """
        # Issue: Order's Data missing to persists in DB such as Order's Current Status id
        # Persist Orders row and get order_id
        order_data = {k: v for k, v in order_input.items() if k != 'items'}
        self.order_id = await workflow.execute_activity(
            order_activities.create_order_in_db,
            order_data,
            start_to_close_timeout=timedelta(seconds=20),
        )
        workflow.logger.info(f"Order {self.order_id} created and persisted via activity")
        
        items = order_input.get('items', [])
        # Issue: Payment Processing phase should be triggered by signal through a Bulk Process, not here
        # Order Status Update to "paid", but Items remain "open" to be persisted in DB
        await self._update_db_status_if_changed("paid")

        # Spawn Child Workflows for each Item, passing item data and order_id
        # We start them asynchronously so they run in parallel
        for item in items:
            # Arg number matches ItemWorkflow.run's definition, because Temporal Python SDK can distinguish by position between args and kwargs (keyword args) that
            # are used to configure the Workflow execution (like id)
            # By default, child workflows run on the same task queue as the parent, which was defined in worker_runner.py
            item_id = item['store_product_service_id']
            child_handle = await workflow.start_child_workflow( # type: ignore[call-overload]    
                ItemWorkflow.run,
                item,
                self.order_id,
                # CRITICAL: Pass the Parent's Workflow ID so the Child can signal back
                workflow.info().workflow_id,
                # This is a Temporal Execution ID different from previous one, it ensures if parent restarts, it restarts the same child
                id=f"order-{self.order_id}-item-{item_id}",
                parent_close_policy=workflow.ParentClosePolicy.REQUEST_CANCEL, # If parent dies, cancel children
            )
            self.item_handles[item_id] = child_handle
        
        # Enter the continuous waiting loop for signals/cancellation
        # This keeps the workflow alive to receive signals that initiate batch phases
        # This line tells to Runtime "don't move past this line until condition inside lambda function evaluates to True"
        # Summary: this line is the "sentinel" that keeps workflow process alive, durable, and ready to receive signals
        # until order reaches a final, resolved status code
        await workflow.wait_condition(lambda: not self._keep_running)
        
        # Wait for all child workflows to confirm termination (optional but clean)
        # await asyncio.gather(*[handle.result() for handle in self.child_handles], return_exceptions=True)

        workflow.logger.info(f"Order {self.order_id} finished with final status code: {self.current_status_code}")
    
    # Helper function to trigger the Activity if the status has changed
    async def _update_db_status_if_changed(self, new_status_code: str):
        """
        Executes the atomic DB update Activity only if the aggregate status has actually changed
        """
        if self.current_status_code != new_status_code:
            workflow.logger.info(
                f"Order {self.order_id} status changed: {self.current_status_code} -> {new_status_code}. Triggering atomic DB update Activity."
            )
            self.current_status_code = new_status_code

            # Schedule the Activity to reliably synchronize/update the DB status code
            await workflow.execute_activity(  # type: ignore
                order_activities.update_order_status_in_db,
                self.order_id,
                self.current_status_code,
                start_to_close_timeout=timedelta(seconds=10),
            )
            
            # Check for terminal status to end the workflow's wait loop
            if new_status_code == "customer_accepted":
                self._keep_running = False # This ends the workflow loop in run()

            # When a return is completed/requested, arm a 7-day timer to auto-trigger refund
            if new_status_code in ["cancelled", "partial_cancelled", "returned", "partial_returned"] and not self._refund_timer_task:
                self._refund_timer_task = asyncio.create_task(self._auto_refund_after_return())


    # --- BATCH PHASE INITIATORS (Triggered by external systems) ---
    # This decorator is needed to register the signal with Temporal and it also allows defining overriding args such as retry_policy, etc.    
    @workflow.signal
    async def start_fill(self):
        """Initiates the Batch Filling Process for all Items"""
        if self.is_busy:
            workflow.logger.warning("Order's Workflow is busy processing another Order's Batch. Order's Filling Batch aborted")
            return

        if self.current_status_code == "paid":
            await self._run_batch_phase(
                item_signal_name="fill_item_batch"
            )
        else:
            workflow.logger.warning(f"Cannot start filling. Order is {self.current_status_code}")

    @workflow.signal
    async def start_shipping(self):
        """Initiates the Batch Shipping Process for all Items that are filled"""
        if self.is_busy:
            workflow.logger.warning("Order's Workflow is busy processing another Order's Batch. Order's Shipping Batch aborted")
            return

        # Allowed statuses include 'filled' or 'partial_filled' (which is the aggregate status)
        if self.current_status_code in ["filled", "partial_filled"]:
            await self._run_batch_phase(
                item_signal_name="ship_item_batch"
            )
        else:
            workflow.logger.warning(f"Cannot start shipping. Order is {self.current_status_code}")

    @workflow.signal
    async def start_delivery(self):
        """Initiates the Batch Delivery Process for all Items that are shipped"""
        if self.is_busy:
            workflow.logger.warning("Order's Workflow is busy processing another Order's Batch. Order's Delivery Batch aborted")
            return
            
        if self.current_status_code in ["shipped", "partial_shipped"]:
            await self._run_batch_phase(
                item_signal_name="deliver_item_batch"
            )
        else:
            workflow.logger.warning(f"Cannot start delivery. Order is {self.current_status_code}")

    @workflow.signal
    async def start_refund(self):
        """Initiates the Batch Refund Process for all Order's Items"""
        if self.is_busy:
            workflow.logger.warning("Order's Workflow is busy processing another Order's Batch. Order's Refund Batch aborted")
            return
        
        await self._run_batch_phase(item_signal_name="refund_item_batch")
        
    @workflow.signal
    async def start_acceptance(self):
        """Initiates the Batch Acceptance Process for all Order's Items"""
        if self.is_busy:
            workflow.logger.warning("Order's Workflow is busy processing another Order's Batch. Order's Acceptance Batch aborted")
            return

        if self.current_status_code in ["delivered", "refunded", "partial_delivered", "partial_refunded"]:
            #await self._run_batch_phase(
            #    item_signal_name="accept_item_batch"
            #)
            await self._query_and_aggregate_status()

        else:
            workflow.logger.warning(f"Cannot start acceptance. Order is {self.current_status_code}")

    
    # --- CORE BATCH EXECUTION LOGIC ---
    async def _run_batch_phase(self, item_signal_name: str):
        """
        Signals all Child Item Workflows to execute a phase activity concurrently,
        then waits for all to complete before aggregating the Order Status
        """
        self.is_busy = True
        workflow.logger.info(f"Starting BATCH Phase: {item_signal_name}")

        # 1. Signal all Item Workflows concurrently to start their phase
        signal_tasks = []
        for handle in self.item_handles.values():
            # Signal the Item Workflow. The Item Workflow then runs its Activity and updates its internal status
            signal_tasks.append(handle.signal(item_signal_name))
        
        # Wait for all signals to be acknowledged by the Item Workflows (this is fast)
        await asyncio.gather(*signal_tasks) 

        # 2. Wait for the Item Workflows to complete their phase activities/statuses changes
        # Note: In a true Temporal app, we'd use external services to notify us 
        # when all children are stable/finished their activities.
        # For this demonstration, we will rely on querying the status after a brief delay
        # to give time for the child workflow to execute its Activity and update its status
        await asyncio.sleep(2)

        # 3. Query the status of ALL children and aggregate
        await self._query_and_aggregate_status()

        self.is_busy = False
        workflow.logger.info(f"BATCH Phase {item_signal_name} Completed")

    async def _auto_refund_after_return(self):
        """
        Wait 7 days after an Order Return, then automatically trigger a Refund Batch
        if the order is still in a returned/partial_returned state
        """
        await workflow.sleep(timedelta(days=7))

        # If already refunded or accepted, skip
        if self.current_status_code in ["refunded", "partial_refunded", "customer_accepted"]:
            return

        # Only proceed if still returned/partial_returned
        if self.current_status_code not in ["returned", "partial_returned"]:
            return

        # Wait if a batch is in progress
        while self.is_busy:
            await workflow.sleep(timedelta(seconds=1))

        await self._run_batch_phase(item_signal_name="refund_item_batch")

    async def _query_item_statuses(self) -> Dict[int, str]:
        """Query all item child workflows for their current status"""
        item_ids = list(self.item_handles.keys())
        query_tasks = [handle.query(ItemWorkflow.get_status) for handle in self.item_handles.values()]  # type: ignore[attr-defined]
        results = await asyncio.gather(*query_tasks)
        # zip() pairs item IDs with their corresponding statuses
        return {item_id: status for item_id, status in zip(item_ids, results)}

    async def _query_and_aggregate_status(self):
        """
        Queries all Item Workflows for their current status and calls the aggregate update function
        """
        item_statuses = await self._query_item_statuses()

        # Compute the new Order Status
        # list(): Convert the dict_values to a list for processing
        new_aggregate_status_code = self.calculate_aggregate_status(list(item_statuses.values()))
        
        # Perform the single, atomic DB update
        await self._update_db_status_if_changed(new_aggregate_status_code)

    # --- AGGREGATION LOGIC (Used ONLY after a batch is complete) ---
    def calculate_aggregate_status(self, status_codes: List[str]) -> str:
        """
        Logic to determine Parent Status based on Child/Item Statuses after a batch finishes
        """
        total = len(status_codes)
        if total == 0:
            return "pending" # Needs manual review to understand why no items exist
        
        # Count occurrences of each Item Status Codes and counts is the type Dict[str, int] (eg: delivered: 3, shipped:2, open:1)
        counts = {s: status_codes.count(s) for s in set(status_codes)}
        
        # Define statuses based on their progress level (highest possible status first)
        accepted = counts.get("customer_accepted", 0)
        refunded = counts.get("refunded", 0)
        returned = counts.get("returned", 0)
        delivered = counts.get("delivered", 0)
        shipped = counts.get("shipped", 0)
        cancelled = counts.get("cancelled", 0)
        filled = counts.get("filled", 0)
        paid = counts.get("paid", 0)
        open = counts.get("open", 0)
        # pending = counts.get("pending", 0)
        
        # QUICK STATUSES TO COMPUTE
        # Full Successful Completion
        if accepted == total:
            return "customer_accepted"
        if refunded == total:
            return "refunded"
        if returned == total:
            return "returned"
        if delivered == total:
            return "delivered"
        if shipped == total:
            return "shipped"
        # Full Order Cancellation
        if cancelled == total:
            return "cancelled"
        if filled == total:
            return "filled"
        if paid == total:
            return "paid"
        if open == total:
            return "open"

        # MIXED/COMPLEX STATUSES
        # if delivered + refunded == total:
        #    return "customer_accepted"
            
        # PROGRESS/PARTIAL STATUSES (Order is in progress)
        if refunded > 0:
            return "partial_refunded"
        if returned > 0:
            return "partial_returned"
        if delivered > 0:
            return "partial_delivered"
        if shipped > 0:
            return "partial_shipped"
        if cancelled > 0:
            return "partial_cancelled"  # Issue?: I don't see when partial_cancelled would be reached/set in current logic
        if filled > 0:
            return "partial_filled"
        else:
            return "pending" # Fallback case that needs manual review

    
    # --- EXTERNAL SIGNALS (Must be guarded by self.is_busy) ---
    @workflow.signal
    async def cancel_order(self):
        """
        When Parent receives Order Cancellation, it propagates to ALL Children
        """
        if self.is_busy:
            # Temporal queues the signal to be processed later when the current busy batch processing completes
            workflow.logger.warning("Cancellation attempted during batch processing. Signal queued")
            return 
        
        workflow.logger.info("Propagating Cancel Signal to all Items...")
        cancel_tasks = []
        for handle in self.item_handles.values():
            cancel_tasks.append(handle.signal(ItemWorkflow.cancel_item))

        # Wait for all cancellation signals to complete
        await asyncio.gather(*cancel_tasks)
        
        # Rerun aggregation immediately after all items have attempted cancellation
        await self._query_and_aggregate_status()

    @workflow.signal
    async def start_return(self):
        """Initiates the Batch Return Process for all Order's Items"""
        if self.is_busy:
            workflow.logger.warning("Order's Workflow is busy processing another Order's Batch. Order's Return Batch aborted")
            return

        if self.current_status_code in ["delivered", "partial_delivered", "partial_returned"]:
            await self._run_batch_phase(
                item_signal_name="return_item_batch"
            )
        else:
            workflow.logger.warning(f"Cannot start return. Order is {self.current_status_code}")


    # --- QUERIES ---
    @workflow.query
    def get_status(self) -> str:
        """Public query to check the aggregated Order Status"""
        return self.current_status_code

    @workflow.query
    async def get_item_statuses(self) -> Dict[int, str]:
        """Public query to check the status of all component Items"""
        return await self._query_item_statuses()

    @workflow.query
    def is_currently_busy(self) -> bool:
        """Returns the current busy status of the workflow"""
        return self.is_busy