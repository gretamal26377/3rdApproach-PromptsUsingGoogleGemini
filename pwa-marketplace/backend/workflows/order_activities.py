
# --- Imports ---
from typing import Dict
from temporalio import activity, exceptions
from pydantic import BaseModel
from ..app.shared.database import db
from ..app.shared.models import Orders, OrderStatuses
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
async def create_order_in_db(order_data: Dict) -> int:
    """
    Persists a new Order in DB using all provided fields.
    Returns the new order_id
    """
    try:
        new_order = Orders()
        for k, v in order_data.items():
            setattr(new_order, k, v)
        db.session.add(new_order)
        db.session.commit()
        logging.info(f"Order Activity: Created Order {new_order.order_id} in DB")
        return new_order.order_id
    except Exception as e:
        db.session.rollback()
        logging.error(f"Order Activity: Failed to create Order: {e}")
        raise exceptions.ApplicationError(f"Failed to create Order: {e}", non_retryable=False)

@activity.defn
async def update_order_status_in_db(order_id: int, new_status_code: str) -> UpdateOrderStatusResult:
    """
    Updates the Order status in the database
    This activity is triggered by the Parent Workflow ONLY after all Item Workflows
    have completed a specific batch phase (e.g., filling) and the new 
    Order Aggregate Status has been calculated
    (Mocked logic here)
    """
    
    logging.info(f"DB Activity: Updating Order {order_id} status to {new_status_code}")

    try:
        status = OrderStatuses.query.filter_by(status_code=new_status_code).first()
        if not status:
            raise exceptions.ApplicationError(
                f"Order Status '{new_status_code}' not found",
                type="INVALID_STATUS",
                non_retryable=True,
            )

        order = Orders.query.filter_by(order_id=order_id).first()
        if not order:
            raise exceptions.ApplicationError(
                f"Order {order_id} not found",
                type="ORDER_NOT_FOUND",
                non_retryable=True,
            )

        order.order_status_id = status.status_id
        db.session.commit()

        activity.logger.info(f"DB Activity: Order {order_id} Status updated successfully in the Database")
        return UpdateOrderStatusResult(order_id=order_id, new_status_code=new_status_code)

    except exceptions.ApplicationError:
        # rollback put here just in case DB session is dirty, if it's clean and rollback is called, nothing happens
        db.session.rollback()
        raise
    except Exception as e:
        # DB/commit/connection errors → retryable failure
        db.session.rollback()
        logging.error(f"DB error updating Order {order_id} to {new_status_code}: {e}")
        raise

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
         raise exceptions.ApplicationError("Payment Gateway rejected refund.", type="GATEWAY_REJECTION", non_retryable=True)

    transaction_id = f"REF-{order_id}-{random.randint(1000, 9999)}"
    activity.logger.info(f"Refund successful for Order {order_id}. Txn ID: {transaction_id}")
    
    return ProcessRefundResult(
        order_id=order_id,
        amount=refund_amount,
        transaction_id=transaction_id
    )