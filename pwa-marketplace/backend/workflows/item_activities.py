
# --- Imports ---
from typing import Dict, Tuple
from temporalio import activity, exceptions
from pydantic import BaseModel
from ..app.shared.database import db
from ..app.shared.models import OrderDetails, OrderStatuses
import asyncio
import random
import logging

class ItemActivityInput(BaseModel):
    order_id: int
    item_id: int
    status_code: str

class ItemActivityOutput(BaseModel):
    item_id: int
    success: bool
    message: str
    # Add a potential new_item_status_code field if an item activity fails/partially succeeds
    new_item_status_code: str

class ItemShipmentResult(BaseModel):
    item_id: int
    tracking_number: str
    success: bool = True
    new_item_status_code: str

# --- Activity to persist OrderDetails row and return composite key ---
@activity.defn
async def create_order_detail_in_db(detail_data: Dict) -> Tuple[int, int]:
    """
    Persists a new OrderDetails row in DB using all provided fields.
    Returns the composite primary key (order_id, store_product_service_id)
    """
    try:
        new_detail = OrderDetails()
        for k, v in detail_data.items():
            setattr(new_detail, k, v)
        db.session.add(new_detail)
        db.session.commit()
        logging.info(f"Item Activity: Created OrderDetail (order_id={new_detail.order_id}, store_product_service_id={new_detail.store_product_service_id}) in DB")
        return (new_detail.order_id, new_detail.store_product_service_id)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Item Activity: Failed to create OrderDetail: {e}")
        raise exceptions.ApplicationError(f"Failed to create OrderDetail: {e}", non_retryable=False)

@activity.defn
async def perform_item_fill(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Simulates an external integration for physical Item Filling (e.g., warehouse picking/packing).
    This activity does NOT call a real external service; it simulates latency and random failure.
    Replace with a real API call to a warehouse management system for production use
    """
    activity.logger.info(f"Activity: Starting Filling for Item {item_data.item_id}")

    # Simulate external system interaction and latency
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # 20% chance of failure (e.g., out of stock)
    if random.random() < 0.2 and item_data.status_code == "paid":
        failure_status = "paid" # Item status remains 'paid'
        activity.logger.warning(f"Activity: Filling failed for Item {item_data.item_id}. Item remains status paid")
        return ItemActivityOutput(
            item_id=item_data.item_id,
            success=False,
            message=f"Item {item_data.item_id} filling failed (out of stock)",
            new_item_status_code=failure_status
        )
    
    success_status_code = "filled"
    _update_item_status(item_data.order_id, item_data.item_id, success_status_code)
    activity.logger.info(f"Activity: Item {item_data.item_id} successfully filled")
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} filled and ready for shipment",
        new_item_status_code=success_status_code
    )

@activity.defn
async def perform_item_shipment(item_data: ItemActivityInput) -> ItemShipmentResult:
    """
    Simulates an external integration for Item Shipping (e.g., carrier handoff, label generation).
    This activity does NOT call a real shipping API; it simulates latency and generates a fake tracking number.
    Replace with a real carrier/shipping API call for production use
    """
    activity.logger.info(f"Activity: Starting shipment for Item {item_data.item_id}")
    
    # Simulate external API call
    await asyncio.sleep(1) 

    tracking_number = f"TRK-{item_data.item_id}-{random.randint(10000, 99999)}"

    activity.logger.info(f"Item {item_data.item_id} shipped. Tracking: {tracking_number}")

    _update_item_status(item_data.order_id, item_data.item_id, "shipped")

    return ItemShipmentResult(
        item_id=item_data.item_id,
        tracking_number=tracking_number,
        success=True,
        new_item_status_code="shipped"
    )

@activity.defn
async def perform_item_delivery(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Simulates an external integration for final delivery to the customer.
    This activity does NOT call a real delivery service; it simulates delivery time and random failure.
    Replace with a real delivery confirmation API call for production use
    """
    activity.logger.info(f"Activity: Attempting delivery for Item {item_data.item_id}")
    await asyncio.sleep(random.uniform(1.0, 3.0)) # Simulate delivery time
    
    # 10% chance of delivery failure (e.g., customer unavailable)
    if random.random() < 0.1 and item_data.status_code == "shipped":
        failure_status = "shipped" # Item status remains 'shipped' for re-attempt
        activity.logger.warning(f"Activity: Delivery failed for Item {item_data.item_id}. Item remains shipped.")
        return ItemActivityOutput(
            item_id=item_data.item_id,
            success=False,
            message=f"Item {item_data.item_id} delivery failed",
            new_item_status_code=failure_status 
        )

    success_status_code = "delivered"
    activity.logger.info(f"Activity: Item {item_data.item_id} successfully delivered")
    _update_item_status(item_data.order_id, item_data.item_id, success_status_code)
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} delivered",
        new_item_status_code=success_status_code
    )

@activity.defn
async def perform_item_return(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Simulates processing a return (eg: Return Material Authorization --RMA-- generation). Marks returned in DB
    """
    activity.logger.info(f"Activity: Starting return for Item {item_data.item_id}")

    await asyncio.sleep(0.5)

    success_status_code = "returned"
    _update_DB_item_status(item_data.order_id, item_data.item_id, success_status_code)
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} returned",
        new_item_status_code=success_status_code,
    )

@activity.defn
async def perform_item_refund(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Simulates processing a refund. Marks refunded in DB
    """
    activity.logger.info(f"Activity: Starting refund for Item {item_data.item_id}")

    await asyncio.sleep(0.5)

    success_status_code = "refunded"
    _update_DB_item_status(item_data.order_id, item_data.item_id, success_status_code)
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} refunded",
        new_item_status_code=success_status_code,
    )

@activity.defn
async def perform_item_acceptance(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Records Item Customer Acceptance after delivery/refund (Item Status Terminal)
    """
    activity.logger.info(f"Activity: Recording acceptance for Item {item_data.item_id}")

    await asyncio.sleep(0.2)

    success_status_code = "customer_accepted"
    _update_DB_item_status(item_data.order_id, item_data.item_id, success_status_code)
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} accepted by Customer",
        new_item_status_code=success_status_code,
    )

def _update_DB_item_status(order_id: int, item_id: int, new_status_code: str) -> None:
    """Update OrderDetails status with retry semantics and Temporal Best Practices"""
    try:
        status = OrderStatuses.query.filter_by(status_code=new_status_code).first()
        if not status:
            raise exceptions.ApplicationError(
                f"Order Status '{new_status_code}' not found",
                type="INVALID_STATUS",
                non_retryable=True,
            )

        detail = OrderDetails.query.filter_by(order_id=order_id, store_product_service_id=item_id).first()
        if not detail:
            raise exceptions.ApplicationError(
                f"OrderDetail not found for order_id={order_id}, item_id={item_id}",
                type="DETAIL_NOT_FOUND",
                non_retryable=True,
            )

        detail.product_service_status_id = status.status_id
        db.session.commit()
    except exceptions.ApplicationError:
        # rollback put here just in case DB session is dirty, if it's clean and rollback is called, nothing happens
        db.session.rollback()
        raise
    except Exception as e:
        # DB/commit/connection errors → retryable failure
        db.session.rollback()
        logging.error(f"DB error updating item status for order_id={order_id}, item_id={item_id}: {e}")
        raise