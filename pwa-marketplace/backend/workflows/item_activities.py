from temporalio import activity, exceptions
from pydantic import BaseModel
import asyncio
import random

class ItemActivityInput(BaseModel):
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

@activity.defn
async def perform_item_fill(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Activity to handle physical Item Filling tasks (e.g., picking, packing)
    Simulates a chance of failure (e.g., lack of stock)
    """
    activity.logger.info(f"Activity: Starting fulfillment for Item {item_data.item_id}")

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
    
    success_status = "filled"
    activity.logger.info(f"Activity: Item {item_data.item_id} successfully filled")
    # Issue: Item Status Update never performed in DB (same for other activities)
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} filled and ready for shipment",
        new_item_status_code=success_status
    )

@activity.defn
async def process_item_shipment(item_id: int) -> ItemShipmentResult:
    """
    Mock activity to simulate shipping a single Item
    """
    activity.logger.info(f"Processing shipment for Item {item_id}...")
    
    # Simulate external API call
    await asyncio.sleep(1) 
    
    tracking_number = f"TRK-{item_id}-{random.randint(10000, 99999)}"
    
    activity.logger.info(f"Item {item_id} shipped. Tracking: {tracking_number}")
    
    return ItemShipmentResult(
        item_id=item_id,
        tracking_number=tracking_number
    )

@activity.defn
async def perform_item_delivery(item_data: ItemActivityInput) -> ItemActivityOutput:
    """
    Activity to simulate final delivery to Customer
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

    success_status = "delivered"
    activity.logger.info(f"Activity: Item {item_data.item_id} successfully delivered")
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} delivered",
        new_item_status_code=success_status
    )