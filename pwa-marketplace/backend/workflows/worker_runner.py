import asyncio
import os
from temporalio.worker import Worker
from temporalio.client import Client

# Import Workflows
from .order_workflow import OrderWorkflow
from .item_workflow import ItemWorkflow

# Import Activities (Clean import thanks to __init__.py if desired, 
# but explicit module imports are safer for worker registration to avoid circular deps)
from . import order_activities
from . import item_activities

TASK_QUEUE_NAME = "order-task-queue"
TEMPORAL_HOST = os.environ.get('TEMPORAL_HOST', "localhost:7233")

async def run_worker():
    # Connect to the Temporal Server
    client = await Client.connect(TEMPORAL_HOST)
    print(f"Connected to Temporal at {TEMPORAL_HOST}")

    # Create the Worker and define what code it will run
    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        # Register all Workflow classes
        workflows=[OrderWorkflow, ItemWorkflow],
        # Register all Activity functions from both modules
        activities=[
            order_activities.update_order_status_in_db,
            order_activities.process_refund,
            item_activities.perform_item_shipment,
            item_activities.perform_item_fill,
            item_activities.perform_item_delivery, 
        ]
    )
    
    # Start the worker (it will poll the server continuously)
    print(f"Starting Worker for Task Queue: {TASK_QUEUE_NAME}")
    await worker.run()

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    # KeyboardInterrupt allows graceful shutdown on Ctrl+C, without it Python shows a stack trace
    except KeyboardInterrupt:
        print("Worker stopped")