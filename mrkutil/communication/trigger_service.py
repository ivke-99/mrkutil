from rabbitmqpubsub.rabbit_pubsub import Publisher
import logging
import uuid
import os

logger = logging.getLogger(__name__)


def trigger_service(request_data, destination, source, corr_id='none'):
    try:
        if not corr_id:
            corr_id = str(uuid.uuid4())
        Publisher(os.getenv("RABBIT_URL")).publish_message(
            data=request_data,
            destination=destination,
            source=source,
            corr_id=corr_id
        )
        return True
    except Exception as e:
        logger.error("Issue sending message to rabbit. Error message: {}".format(str(e)))

    response = {
        "response": {
            "message": "Service issue"
        },
        "code": 500
    }
    Publisher(os.getenv("RABBIT_URL")).publish_message(
        data=response,
        destination=destination,
        source=source,
        corr_id=corr_id
    )
    return False
