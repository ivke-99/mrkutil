from rabbitmqpubsub import rabbit_pubsub
from mrkutil.base import BaseHandler
from .trigger_service import trigger_service
from mrkutil.responses import ServiceResponse
import logging
import os

logger = logging.getLogger(__name__)


class Subscriber:
    """
    Represents a subscriber that handles incoming messages.

    Args:
        exchange (str): The exchange name.

    Attributes:
        exchange (str): The exchange name.

    Methods:
        handle: Handles the incoming message.

    """

    def __init__(self, exchange, on_message_process_complete=None):
        self.exchange = exchange
        self.on_message_process_complete = on_message_process_complete

    def handle(self, body=None):
        """
        Handles the incoming message.

        Args:
            body (dict): The message body.

        Returns:
            bool: True if the message was successfully handled, False otherwise.

        """
        response = None
        method_exists = isinstance(body.get("data", False), dict) and body.get(
            "data", {}
        ).get("method")
        try:
            if method_exists:
                response = BaseHandler.process_data(
                    body["data"], body["meta"]["correlationId"]
                )
                if response:
                    trigger_service(
                        request_data=response,
                        destination=body["meta"]["source"],
                        source=self.exchange,
                        corr_id=body["meta"]["correlationId"],
                    )
                return True
        except Exception as e:
            logger.exception("error parsing received message {}".format(str(e)))
            if method_exists:
                destination = body.get("meta", {}).get("source")
                if destination:
                    corr_id = body.get("meta", {}).get("correlationId")
                    method = body.get("data", {}).get("method")
                    trigger_service(
                        request_data=ServiceResponse(
                            code=500,
                            message=f"Service issue with corr id: {corr_id}, method {method} and service {self.exchange}, called by {destination}",
                        ),
                        destination=destination,
                        source=self.exchange,
                        corr_id=corr_id,
                    )
        finally:
            try:
                if self.on_message_process_complete:
                    self.on_message_process_complete()
            except Exception as e:
                logger.error(f"On message complete failed. Error {e}")
        return False


def listen(
    exchange,
    exchange_type,
    queue,
    async_processing=True,
    max_threads=10,
    on_message_process_complete=None,
):
    """
    Listens for messages on a RabbitMQ exchange and processes them asynchronously if wanted.

    Args:
        exchange (str): The name of the RabbitMQ exchange to listen on.
        exchange_type (str): The type of the RabbitMQ exchange.
        queue (str): The name of the RabbitMQ queue to bind to the exchange.
        async_processing (bool, optional): Whether to process messages asynchronously. Defaults to True.
    """
    subscriber = rabbit_pubsub.Subscriber(
        amqp_url=os.getenv("RABBIT_URL"),
        exchange=exchange,
        exchange_type=exchange_type,
        queue=queue,
        async_processing=async_processing,
        max_threads=max_threads,
    )
    subscriber.subscribe(Subscriber(exchange, on_message_process_complete))
    subscriber.start()
    subscriber.join()
