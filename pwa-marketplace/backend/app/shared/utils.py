import os
from temporalio.client import Client

TEMPORAL_HOST = os.environ.get('TEMPORAL_HOST', "localhost:7233")

# Temporal Client connection helper
async def get_temporal_client():
    return await Client.connect(TEMPORAL_HOST)
