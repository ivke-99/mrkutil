from rabbitmqpubsub.rabbit_pubsub import RpcClient
from mrkutil.utilities import random_string
import logging
import os

logger = logging.getLogger(__name__)


def call_service(request_data, destination, source, corr_id=None):
    """
    Calls a service using RPC (Remote Procedure Call) and returns the response data.

    Args:
        request_data (dict): The data to be sent as the request to the service.
        destination (str): The name of the service to call.
        source (str): The name of the source service making the call.
        corr_id (str, optional): The correlation ID for the RPC call.

    Returns:
        dict: The response data received from the service.

    """
    rpc = RpcClient(
        amqp_url=os.getenv("RABBIT_URL"),
        exchange=source,
        queue="temp_{}".format(random_string(6)),
    )
    response = rpc.call(data=request_data, recipient=destination, corr_id=corr_id)
    response_data = response
    return response_data["data"]
