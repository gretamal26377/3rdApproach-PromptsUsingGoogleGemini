import asyncio
import os
from temporalio.worker import Worker
from temporalio.client import Client

# 1. Import all Workflows and Activities that this Worker will execute
from .order_workflow import OrderWorkflow
from .item_workflow import ItemWorkflow
from .order_activities import update_order_status_in_db  # Example Activity
# from .item_activities import ... # Add Item Activities here later

TASK_QUEUE_NAME = "order-task-queue"
TEMPORAL_HOST = os.environ.get('TEMPORAL_HOST') # Use the service name from docker-compose env var

async def run_worker():
    # Connect to the Temporal Server
    if TEMPORAL_HOST:
        client = await Client.connect(TEMPORAL_HOST)
    else:
        client = await Client.connect("temporal-server:7233")
    # Create the Worker and define what code it will run
    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        # Register all Workflow classes
        workflows=[OrderWorkflow, ItemWorkflow],
        # Register all Activity functions
        activities=[update_order_status_in_db] 
    )
    
    # Start the worker (it will poll the server continuously)
    print(f"Starting Worker for Task Queue: {TASK_QUEUE_NAME}")
    await worker.run()

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("Worker stopped")