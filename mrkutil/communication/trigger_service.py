from rabbitmqpubsub.rabbit_pubsub import Publisher
from mrkutil.responses import ServiceResponse
import logging
import uuid
import os

logger = logging.getLogger(__name__)


def trigger_service(request_data, destination, source, corr_id="none"):
    """
    Sends a message to a RabbitMQ queue using the provided request data, destination, source, and correlation ID.

    Args:
        request_data (any): The data to be sent in the message.
        destination (str): The destination queue name.
        source (str): The source of the message.
        corr_id (str, optional): The correlation ID for the message. Defaults to "none".

    Returns:
        bool: True if the message was successfully sent, False otherwise.
    """
    try:
        if not corr_id:
            corr_id = str(uuid.uuid4())
        Publisher(os.getenv("RABBIT_URL")).publish_message(
            data=request_data, destination=destination, source=source, corr_id=corr_id
        )
        return True
    except Exception as e:
        logger.error(
            "Issue sending message to rabbit. Error message: {}".format(str(e))
        )

    response = ServiceResponse(code=500, message="Service issue")
    Publisher(os.getenv("RABBIT_URL")).publish_message(
        data=response, destination=destination, source=source, corr_id=corr_id
    )
    return False
