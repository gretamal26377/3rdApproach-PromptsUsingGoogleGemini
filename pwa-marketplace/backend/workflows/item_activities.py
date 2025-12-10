from temporalio import activity
from pydantic import BaseModel
import asyncio
import random

class ItemShipmentResult(BaseModel):
    item_id: int
    tracking_number: str
    success: bool = True

@activity.defn
async def process_item_shipment(item_id: int) -> ItemShipmentResult:
    """
    Mock activity to simulate shipping a single item.
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