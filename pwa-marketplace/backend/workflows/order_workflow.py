import asyncio
from datetime import timedelta
from temporalio import workflow
from typing import List, Dict
from . import order_activities 
from .item_workflow import ItemWorkflow 

# Declares a class as a Temporal Workflow
@workflow.defn
class OrderWorkflow:
    # init runs when a new instance of the workflow is created before @workflow.run
    # self refers to the specific class/object instance being created
    def __init__(self):
        # self.order_id: int = 0  # placeholder; real value always assigned in run()
        self.current_status = "open"
        # Initialize self.child_handles
        self.child_handles = [] # Keep track of child workflow handles

    @workflow.run
    async def run(self, order_id: int, item_ids: List[int], total_amount: float):
        self.order_id = order_id
        # assert self.order_id is not None

        workflow.logger.info(f"Order {order_id} started with {len(item_ids)} items")

        # 1. Spawn Child Workflows for each Item
        # We start them asynchronously so they run in parallel
        for item_id in item_ids:
            handle = await workflow.start_child_workflow(
                ItemWorkflow.run,
                item_id,
                id=f"order-{order_id}-item-{item_id}", # Unique Workflow ID
                task_queue="order-task-queue", # Run on same or different queue
                parent_close_policy=workflow.ParentClosePolicy.REQUEST_CANCEL, # If parent dies, cancel children
            )
            self.child_handles.append(handle)

        # 2. Start the Status Aggregation Loop
        # This runs in the background to update the Parent Order status
        asyncio.create_task(self.aggregate_item_statuses())

        # 3. Wait for final state
        await workflow.wait_condition(lambda: self.current_status in ["cancelled", "refunded", "delivered", "returned"])
        
        workflow.logger.info(f"Order {self.order_id} finished.")

    async def aggregate_item_statuses(self):
        """
        Continuously checks the status of all child items and updates the 
        Parent Order status accordingly.
        """
        try:
            while self.current_status not in ["cancelled", "refunded", "delivered", "returned"]:
                item_statuses = []
                
                # Query every child workflow for its status
                for handle in self.child_handles:
                    status = await handle.query(ItemWorkflow.get_status)
                    item_statuses.append(status)
                
                new_aggregate_status = self.calculate_aggregate_status(item_statuses)
                
                # If status changed, update DB and internal state
                if new_aggregate_status != self.current_status:
                    self.current_status = new_aggregate_status
                    
                    # Update DB using Activity (Optimized: only on change)
                    await workflow.execute_activity(
                        order_activities.update_order_status_in_db,
                        self.order_id,
                        self.current_status,
                        schedule_to_close_timeout=timedelta(seconds=10),
                    )

                # Wait a bit before checking again to avoid hot-looping
                await asyncio.sleep(2) 
        except asyncio.CancelledError:
            # Handle cancellation of this loop if workflow finishes
            pass

    def calculate_aggregate_status(self, statuses: List[str]) -> str:
        """
        Logic to determine Parent Status based on Child Statuses.
        """
        total = len(statuses)
        if total == 0:
            return "open"
        
        counts = {s: statuses.count(s) for s in set(statuses)}
        
        # Example Logic (Expand based on your exact requirements):
        if counts.get("cancelled", 0) == total:
            return "cancelled"
        if counts.get("delivered", 0) == total:
            return "delivered"
        if counts.get("shipped", 0) == total:
            return "shipped"
            
        # Partial logic
        if counts.get("shipped", 0) > 0 or counts.get("partial_shipped", 0) > 0:
            return "partial_shipped"
        if counts.get("cancelled", 0) > 0:
            return "partial_cancelled"
            
        return "open" # Default fallback

    @workflow.signal
    async def cancel_order(self):
        """
        When Parent receives cancel, it propagates it to ALL children.
        """
        workflow.logger.info("Propagating cancel signal to all items...")
        for handle in self.child_handles:
            await handle.signal(ItemWorkflow.cancel_item)
            
        # The aggregation loop will detect the children changing to 'cancelled'
        # and automatically update the Parent status to 'cancelled' or 'partial_cancelled'