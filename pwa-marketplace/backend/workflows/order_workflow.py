import asyncio
from datetime import timedelta
from temporalio import workflow
from typing import List, Dict # Imported Dict for self.item_status_codes
from . import order_activities 
from . import item_workflow 

# ORDER_STATUS_CODES = [
#    'open', 'paid', 'pending', 'partial_pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
#    'delivered', 'partial_delivered', 'cancelled', 'partial_cancelled', 'returned', 'partial_returned',
#    'refunded', 'partial_refunded', 'customer_accepted'
# ]

# Declares a class as a Temporal Workflow
@workflow.defn
class OrderWorkflow:
    # init runs when a new instance of the workflow is created before @workflow.run
    # self refers to the specific class/object instance being created
    def __init__(self):
        # Initialize internal status variables
        self.order_id: int | None = None    # placeholder; real value always assigned in run()
        self.current_status_code = "open"
        # Stores item IDs and their corresponding ItemWorkflowHandles
        self.item_handles: Dict[int, workflow.ExternalWorkflowHandle] = {}
        # Dictionary to store item status codes (key: item_id, value: status_code)
        self.item_status_codes: Dict[int, str] = {}
        # Control flag to prevent other phase signals (like cancellation) during a batch run
        self.is_busy = False 
        self._keep_running = True

    @workflow.run
    async def run(self, order_id: int, item_ids: List[int], total_amount: float):
        self.order_id = order_id
        # assert self.order_id is not None

        workflow.logger.info(f"Order {order_id} started with {len(item_ids)} items")

        # Initialise the status code map based on the input item list, setting all to "open"
        self.item_status_codes = {item_id: "open" for item_id in item_ids}

        # Issue: To work in Payment Processing phase
        # Status update and DB sync
        await self._update_db_status_if_changed("paid")

        # Spawn Child Workflows for each Item
        # We start them asynchronously so they run in parallel
        for item_id in item_ids:
            # Arg number matches ItemWorkflow.run's definition, because Temporal Python SDK can distinguish by position between args and kwargs (keyword args) that
            # are used to configure the Workflow execution (like id)
            # By default, child workflows run on the same task queue as the parent, which was defined in worker_runner.py
            child_handle = await workflow.start_child_workflow(
                ItemWorkflow.run,
                item_id,
                # CRITICAL: Pass the Parent's Workflow ID so the Child can signal back
                workflow.info().workflow_id,
                # This is a Temporal Execution ID different from previous one, it ensures if parent restarts, it restarts the same child
                id=f"order-{order_id}-item-{item_id}",
                parent_close_policy=workflow.ParentClosePolicy.REQUEST_CANCEL, # If parent dies, cancel children
            )
            self.item_handles[item_id] = child_handle
            # If Order Status was moved to "paid", then move Item internal status map to "paid"
            self.item_status_codes[item_id] = "paid"
        
        # Enter the continuous waiting loop for signals/cancellation
        # This keeps the workflow alive to receive signals that initiate batch phases
        # This line tells to Runtime "don't move past this line until condition inside lambda function evaluates to True"
        # Summary: this line is the "sentinel" that keeps workflow process alive, durable, and ready to receive signals
        # until order reaches a final, resolved status code
        await workflow.wait_condition(lambda: not self._keep_running)
        workflow.logger.info(f"Order {order_id} finished with final status code: {self.current_status_code}")

        # Wait for all child workflows to confirm termination (optional but clean)
        # await asyncio.gather(*[handle.result() for handle in self.child_handles], return_exceptions=True)

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
            await workflow.execute_activity(
                order_activities.update_order_status_in_db,
                self.order_id,
                self.current_status_code,
                start_to_close_timeout=timedelta(seconds=10),
            )
            
            # Check for terminal status to end the workflow's wait loop
            if new_status_code == "customer_accepted":
                self._keep_running = False # This ends the workflow loop in run()


    # --- BATCH PHASE INITIATORS (Triggered by external systems) ---
    # This decorator is needed to register the signal with Temporal and it also allows defining overriding args such as retry_policy, etc.    
    @workflow.signal
    async def start_fill(self):
        """Initiates the Batch Filling Process for all Items"""
        if self.is_busy:
            workflow.logger.warning("Workflow is busy processing another batch. Filling aborted")
            return

        if self.current_status_code == "paid":
            await self._run_batch_phase(
                item_signal_name="fill_item_batch",
                target_status_code="filled"
            )
        else:
            workflow.logger.warning(f"Cannot start filling. Order is {self.current_status_code}")

    @workflow.signal
    async def start_shipping(self):
        """Initiates the Batch Shipping Process for all Items that are filled"""
        if self.is_busy:
            workflow.logger.warning("Workflow is busy processing a batch. Shipping skipped")
            return

        # Allowed statuses include 'filled' or 'partial_filled' (which is the aggregate status)
        if self.current_status_code in ["filled", "partial_filled"]:
            await self._run_batch_phase(
                item_signal_name="ship_item_batch",
                target_status_code="shipped"
            )
        else:
            workflow.logger.warning(f"Cannot start shipping. Order is {self.current_status_code}")

    @workflow.signal
    async def start_delivery(self):
        """Initiates the Batch Delivery Process for all Items that are shipped"""
        if self.is_busy:
            workflow.logger.warning("Workflow is busy processing a batch. Delivery skipped")
            return
            
        if self.current_status_code in ["shipped", "partial_shipped"]:
            await self._run_batch_phase(
                item_signal_name="deliver_item_batch",
                target_status_code="delivered"
            )
        else:
            workflow.logger.warning(f"Cannot start delivery. Order is {self.current_status_code}")

    
    # --- CORE BATCH EXECUTION LOGIC ---
    async def _run_batch_phase(self, item_signal_name: str, target_status_code: str):
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

        # 2. Wait for the Item Workflows to complete their phase activities/status changes
        # The Item Workflows DO NOT return from the signal handler. We must query their status 
        # until all have reached the expected target status or a terminal status.
        # Note: In a true Temporal app, we'd use external services to notify us 
        # when all children are stable, or simply wait for the child workflow to complete/continue.
        # For this demonstration, we will rely on querying the status after a brief delay
        # to give time for the child workflow to execute its Activity and update its status
        await asyncio.sleep(2)

        # 3. Query the status of ALL children and aggregate
        await self._query_and_aggregate_status()

        self.is_busy = False
        workflow.logger.info(f"BATCH Phase {item_signal_name} Completed")

    async def _query_and_aggregate_status(self):
        """
        Queries all Item Workflows for their current status and performs the aggregate update
        """
        new_status_codes = {}
        query_tasks = []
        item_ids = list(self.item_handles.keys())

        # Create tasks to query status concurrently
        # self.item_handles is a Dict then .items() returns (key, value) pairs, 
        # where item_id gets the key and handle gets the value
        for item_id, handle in self.item_handles.items():
            query_tasks.append(handle.query(ItemWorkflow.get_status))

        # Gather all query results
        results = await asyncio.gather(*query_tasks)

        # Map results back to item IDs and update internal state
        # zip() pairs item_ids with results, so we can update the status codes
        for item_id, status in zip(item_ids, results):
            new_status_codes[item_id] = status
            self.item_status_codes[item_id] = status

        # 4. Compute the new Order status
        # list(): Convert the dict_values to a list for processing
        new_aggregate_status_code = self.calculate_aggregate_status(
            list(self.item_status_codes.values())
        )
        
        # 5. Perform the single, atomic DB update
        await self._update_db_status_if_changed(new_aggregate_status_code)

    # --- AGGREGATION LOGIC (Used ONLY after a batch is complete) ---
    def calculate_aggregate_status(self, status_codes: List[str]) -> str:
        """
        Logic to determine Parent Status based on Child/Item Statuses after a batch finishes
        """
        total = len(status_codes)
        if total == 0:
            return "open"
        
        # Count occurrences of each item status codes and counts is the type Dict[str, int] (eg: delivered: 3, shipped:2, open:1)
        counts = {s: status_codes.count(s) for s in set(status_codes)}
        
        # Define statuses based on their progress level (highest possible status first)
        accepted = counts.get("customer_accepted", 0)
        delivered = counts.get("delivered", 0)
        shipped = counts.get("shipped", 0)
        filled = counts.get("filled", 0)
        paid = counts.get("paid", 0)
        cancelled = counts.get("cancelled", 0)
        
        # Issue: 'pending', 'partial_pending', 'returned', 'partial_returned', 'refunded', 'partial_refunded' are missing

        # TERMINAL STATUSES (Order is done)
        if accepted + delivered + shipped + filled + paid + cancelled == total:
            # Full Successful Completion
            if accepted == total:
                return "customer_accepted"
            if delivered + accepted == total:
                return "delivered"
            # Full Failure
            if cancelled == total:
                return "cancelled"

        # PROGRESS/PARTIAL STATUSES (Order is in progress)
        # Is anything in the Shipping or Delivery phase?
        in_shipping_or_further = accepted + delivered + shipped
        if in_shipping_or_further > 0:
            # Issue: "partial_delivered" status missing
            if in_shipping_or_further == total - cancelled: # All non-cancelled items are shipped/delivered
                return "shipped" # All shipped (or delivered but not yet accepted)
            else:
                # Some are shipped others are still being processed (paid/filled)
                return "partial_shipped"

        # Issue: "partial_cancelled" status missing
        
        # Is anything in Filling phase?
        in_filling = filled
        if in_filling > 0:
            if in_filling == total:
                 return "filled"
            else:
                # Some are filled, others are still paid/pending
                return "partial_filled"

        # Is anything in Paid phase?
        if paid > 0:
             return "paid"

        # Fallback to current or "open" if aggregation fails to find a higher status
        # if self.current_status_code is falsy (None or empty), return "open"
        return self.current_status_code or "open"


    # --- EXTERNAL SIGNALS (Must be guarded by self.is_busy) ---
    @workflow.signal
    async def cancel_order(self):
        """
        When Parent receives Order Cancellation, it propagates to ALL Children
        """
        if self.is_busy:
            workflow.logger.warning("Cancellation attempted during batch processing. Signal queued.")
            # Temporal handles the queuing, but we log the attempt.
            return 
        
        workflow.logger.info("Propagating Cancel Signal to all Items...")
        
        # Signal all children to cancel
        cancel_tasks = []
        for handle in self.item_handles.values():
            cancel_tasks.append(handle.signal(ItemWorkflow.cancel_item))
        
        await asyncio.gather(*cancel_tasks)
        
        # Rerun aggregation immediately after all items have attempted cancellation
        await self._query_and_aggregate_status()


    # --- QUERIES ---
    @workflow.query
    def get_status(self) -> str:
        """Public query to check the aggregated Order Status"""
        return self.current_status_code

    @workflow.query
    def get_item_statuses(self) -> Dict[int, str]:
        """Public query to check the status of all component Items"""
        return self.item_status_codes

    @workflow.query
    def is_currently_busy(self) -> bool:
        """Returns the current busy status of the workflow."""
        return self.is_busy