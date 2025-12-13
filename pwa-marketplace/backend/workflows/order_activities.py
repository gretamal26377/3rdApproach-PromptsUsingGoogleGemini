from temporalio import activity
from temporalio.exceptions import ApplicationError
from pydantic import BaseModel
# from ..app.shared.database import db
# from ..app.shared.models import Orders, OrderStatuses
import logging
import asyncio
import random
from datetime import datetime


# --- Data Models ---
class UpdateOrderStatusResult(BaseModel):
    order_id: int
    new_status_code: str
    success: bool = True

class ProcessRefundResult(BaseModel):
    order_id: int
    amount: float
    transaction_id: str
    success: bool = True

# --- Activities ---

@activity.defn
async def update_order_status_in_db(order_id: int, new_status_code: str) -> UpdateOrderStatusResult:
    """
    Updates the Order status in the database
    This activity is triggered by the Parent Workflow upon receiving a status signal
    (Mocked logic here to avoid dependency errors if DB models aren't present in this context)
    """
    # In a real app, you would use the db session code provided earlier:
    # order = Orders.query.get(order_id)
    # ... logic ...
    # db.session.commit()
    
    logging.info(f"DB Activity: Updating Order {order_id} status to {new_status_code}")

    # Mocking successful DB update
    if order_id <= 0:
        raise ApplicationError("Invalid Order ID provided", type="INVALID_INPUT", non_retryable=True)
        
    activity.logger.info(f"DB Activity: Order {order_id} Status updated successfully in the Database")

    
    return UpdateOrderStatusResult(
        order_id=order_id,
        new_status_code=new_status_code
    )

@activity.defn
async def process_refund(order_id: int, refund_amount: float) -> ProcessRefundResult:
    """
    Mock Activity to handle external payment processing for a refund
    """
    activity.logger.info(f"Initiating refund for Order {order_id} for ${refund_amount}...")

    # Simulate API latency
    await asyncio.sleep(random.uniform(0.5, 2.0)) 
    
    # Simulate a non-retryable failure (rare)
    if random.random() < 0.05:
         raise ApplicationError("Payment Gateway rejected refund.", type="GATEWAY_REJECTION", non_retryable=True)

    transaction_id = f"REF-{order_id}-{random.randint(1000, 9999)}"
    activity.logger.info(f"Refund successful for Order {order_id}. Txn ID: {transaction_id}")
    
    return ProcessRefundResult(
        order_id=order_id,
        amount=refund_amount,
        transaction_id=transaction_id
    )