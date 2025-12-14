import asyncio
from datetime import timedelta
from temporalio import workflow
from typing import List, Dict # Imported Dict for self.item_status_codes
from . import order_activities 
from .item_workflow import ItemWorkflow 

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
        # Initialize self.child_handles
        self.child_handles = [] # Keep track of child workflow handles
        self.item_status_codes: Dict[int, str] = {} # New: Dictionary to store item status codes (key: item_id, value: status_code)

    @workflow.run
    async def run(self, order_id: int, item_ids: List[int], total_amount: float):
        self.order_id = order_id
        # assert self.order_id is not None

        workflow.logger.info(f"Order {order_id} started with {len(item_ids)} items")

        # Initialise the status code map based on the input item list, setting all to "open"
        self.item_status_codes = {item_id: "open" for item_id in item_ids}

        # Spawn Child Workflows for each Item
        # We start them asynchronously so they run in parallel
        for item_id in item_ids:
            # Arg number matches ItemWorkflow.run's definition, because Temporal Python SDK can distinguish by position between args and kwargs (keyword args) that
            # are used to configure the Workflow execution (like id)
            # By default, child workflows run on the same task queue as the parent, which was defined in worker_runner.py
            handle = await workflow.start_child_workflow(
                ItemWorkflow.run,
                item_id,
                # CRITICAL: Pass the Parent's Workflow ID so the Child can signal back
                workflow.info().workflow_id,
                # This is a Temporal Execution ID different from previous one, it ensures if parent restarts, it restarts the same child
                id=f"order-{order_id}-item-{item_id}",
                parent_close_policy=workflow.ParentClosePolicy.REQUEST_CANCEL, # If parent dies, cancel children
            )
            self.child_handles.append(handle) # Added appending of handle
        
        # Passive wait for final status code, woken up only by external Signals/Queries
        # This line tells to Runtime "don't move past this line until condition inside lambda function evaluates to True"
        # Summary: this line is the "sentinel" that keeps workflow process alive, durable, and ready to receive signals
        # until order reaches a final, resolved status code
        await workflow.wait_condition(lambda: self.current_status_code == "customer_accepted")

        workflow.logger.info(f"Order {order_id} finished with final status code: {self.current_status_code}")

        # Wait for all child workflows to confirm termination (optional but clean)
        await asyncio.gather(*[handle.result() for handle in self.child_handles], return_exceptions=True)


    # --- QUERIES
    @workflow.query
    def get_status(self) -> str:
        """Public query to check the aggregated Order Status"""
        return self.current_status_code

    @workflow.query
    def get_item_statuses(self) -> Dict[int, str]:
        """Public query to check the status of all component Items"""
        return self.item_status_codes
    

    # --- SIGNAL HANDLER (Push Model) ---
    # This decorator is needed to register the signal with Temporal and it also allows defining overriding args such as retry_policy, etc.
    @workflow.signal
    async def update_child_status(self, item_id: int, new_status_code: str):
        """
        Receives status code updates from a Child Item Workflow and immediately
        triggers a recalculation of the aggregate Order Status Code
        """
        if item_id in self.item_status_codes and self.item_status_codes[item_id] != new_status_code:
            workflow.logger.info(f"SIGNAL RECEIVED for Item {item_id}: {new_status_code}")

            # 1. Update the internal status code map instantly
            self.item_status_codes[item_id] = new_status_code

            # 2. Immediately recalculate and update DB if the aggregate status code changed
            await self._recalculate_and_update_db()
        elif item_id not in self.item_status_codes:
            workflow.logger.warn(f"Received signal for unknown item ID: {item_id}")

    async def _recalculate_and_update_db(self):
        """Calculates the new aggregate Order Status Code and updates the DB if necessary"""

        new_aggregate_status_code = self.calculate_aggregate_status(list(self.item_status_codes.values()))

        # If the aggregate status code changed, update DB and internal status code
        if new_aggregate_status_code != self.current_status_code:
            workflow.logger.info(f"Aggregate status code changed: {self.current_status_code} -> {new_aggregate_status_code}")
            self.current_status_code = new_aggregate_status_code
            
            # Schedule the Activity to reliably synchronize/update the DB status code
            await workflow.execute_activity(
                order_activities.update_order_status_in_db,
                self.order_id,
                self.current_status_code,
                schedule_to_close_timeout=timedelta(seconds=10),
            ) # type: ignore[call-overload]

    def calculate_aggregate_status(self, status_codes: List[str]) -> str:
        """
        Logic to determine Parent Status Code based on Child Status Codes
        """
        total = len(status_codes)
        if total == 0: return "open"

        # Count occurrences of each item status codes and counts is the type Dict[str, int] (eg: delivered: 3, shipped:2, open:1)
        counts = {s: status_codes.count(s) for s in set(status_codes)}

        # Quick check Order Status Codes where all Items are in the same status code
        if counts.get("paid", 0) == total:
            return "paid"
        if counts.get("pending", 0) == total:
            return "pending"
        if counts.get("filled", 0) == total:
            return "filled"
        if counts.get("shipped", 0) == total:
            return "shipped"
        if counts.get("delivered", 0) == total:
            return "delivered"
        if counts.get("cancelled", 0) == total:
            return "cancelled"
        if counts.get("returned", 0) == total:
            return "returned"
        if counts.get("refunded", 0) == total:
            return "refunded"

        # Terminal/Final Status Code (All Items must be in this status code to consider Order in this same status code)
        if counts.get("customer_accepted", 0) == total:
            return "customer_accepted"

        # Partial/Mixed Status Codes
        if any(s == "partial_shipped" for s in status_codes):
            return "partial_shipped"
        if any(s == "partial_cancelled" for s in status_codes):
            return "partial_cancelled"
         
        return "open" # Default fallback

    # Add signal/query methods as needed for status code updates, events, etc
    @workflow.signal
    async def cancel_order(self):
        """
        When Parent receives Order Cancellation, it propagates to ALL Children
        """
        workflow.logger.info("Propagating Cancel Signal to all Items...")
        for handle in self.child_handles:
            # We use the existing ItemWorkflow.cancel_item signal, which is now updated 
            # in item_workflow.py to signal the parent back upon status code change
            await handle.signal(ItemWorkflow.cancel_item)

        # The Order Status Code will be updated via the incoming signals from the children