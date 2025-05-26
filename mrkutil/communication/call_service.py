from rabbitmqpubsub.rabbit_pubsub import RpcClient, AsyncRpcClient
from mrkutil.utilities import random_string, RequestData
import logging
import os

logger = logging.getLogger(__name__)


def call_service(
    request_data: RequestData,
    destination: str,
    source: str,
    corr_id: str | None = None,
    timeout: int = 30,
    rabbit_url: str = os.getenv("RABBIT_URL"),
):
    """
    Calls a service using RPC (Remote Procedure Call) and returns the response data.

    Args:
        request_data (dict): The data to be sent as the request to the service.
        destination (str): The name of the service to call.
        source (str): The name of the source service making the call.
        corr_id (str, optional): The correlation ID for the RPC call.
        timeout (int, optional): Timeout for the RPC call.
        rabbit_url (str, optional): The RabbitMQ URL. Defaults to the value of the RABBIT_URL environment variable.

    Returns:
        dict: The response data received from the service.

    """
    rpc = RpcClient(
        amqp_url=rabbit_url,
        exchange=source,
        queue="temp_{}".format(random_string(6)),
        timeout=timeout,
    )
    response = rpc.call(data=request_data, recipient=destination, corr_id=corr_id)
    logger.info(f"Received response from {destination}. Response {response}")
    return response["data"]


async def acall_service(
    request_data: RequestData,
    destination: str,
    source: str,
    corr_id: str | None = None,
    timeout: int = 30,
    rabbit_url: str = os.getenv("RABBIT_URL"),
):
    rpc = AsyncRpcClient(
        amqp_url=rabbit_url,
        exchange=source,
        queue="temp_{}".format(random_string(6)),
        timeout=timeout,
    )
    response = await rpc.call(data=request_data, recipient=destination, corr_id=corr_id)
    logger.info(f"Received response from {destination}. Response {response}")
    return response["data"]
