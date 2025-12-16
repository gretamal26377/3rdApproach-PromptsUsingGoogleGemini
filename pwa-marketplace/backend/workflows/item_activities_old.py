from temporalio import activity
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

class ItemShipmentResult(BaseModel):
    item_id: int
    tracking_number: str
    success: bool = True

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
def perform_item_fulfillment(item_data: ItemActivityInput) -> ItemActivityOutput:
    """Activity to handle physical item fulfillment tasks (e.g., picking, packing)"""
    activity.logger.info(f"Activity: Starting fulfillment for Item {item_data.item_id}")
    # Simulate external system interaction
    # time.sleep(5) 
    activity.logger.info(f"Activity: Item {item_data.item_id} successfully packaged")
    
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} packaged and ready for shipment"
    )

@activity.defn
def handle_shipment_handoff(item_data: ItemActivityInput) -> ItemActivityOutput:
    """Activity to handle generating a shipping label and handing off to the carrier"""
    activity.logger.info(f"Activity: Generating label and handoff for Item {item_data.item_id}")
    # Simulate API call to UPS/FedEx/etc.
    # time.sleep(5) 
    activity.logger.info(f"Activity: Shipment handoff complete for Item {item_data.item_id}")
    
    return ItemActivityOutput(
        item_id=item_data.item_id,
        success=True,
        message=f"Item {item_data.item_id} is now with the carrier"
    )