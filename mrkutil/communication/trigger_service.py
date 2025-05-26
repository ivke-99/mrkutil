from rabbitmqpubsub.rabbit_pubsub import Publisher, AsyncRpcClient
from mrkutil.utilities import random_string, RequestData
import logging
import uuid
import os

logger = logging.getLogger(__name__)


def trigger_service(
    request_data: RequestData,
    destination: str,
    source: str,
    corr_id: str | None = None,
    rabbit_url: str = os.getenv("RABBIT_URL"),
):
    """
    Sends a message to a RabbitMQ queue using the provided
    request data, destination, source, and correlation ID.

    Args:
        request_data (any): The data to be sent in the message.
        destination (str): The destination queue name.
        source (str): The source of the message.
        corr_id (str, optional): The correlation ID for the message. Defaults to "none".
        rabbit_url (str, optional): The RabbitMQ URL. Defaults to the value of the RABBIT_URL environment variable.

    Returns:
        bool: True if the message was successfully sent, False otherwise.
    """
    if not corr_id:
        corr_id = str(uuid.uuid4())
    Publisher(rabbit_url).publish_message(
        data=request_data, destination=destination, source=source, corr_id=corr_id
    )


async def atrigger_service(
    request_data: RequestData,
    destination: str,
    source: str,
    corr_id: str | None = None,
    rabbit_url: str = os.getenv("RABBIT_URL"),
):
    if not corr_id:
        corr_id = str(uuid.uuid4())
    rpc = AsyncRpcClient(
        amqp_url=rabbit_url,
        exchange=source,
        queue="temp_{}".format(random_string(6)),
    )
    await rpc.call(
        data=request_data,
        recipient=destination,
        corr_id=corr_id,
        wait_response=False,
    )
