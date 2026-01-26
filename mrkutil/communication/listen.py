from typing import Callable
from rabbitmqpubsub import rabbit_pubsub
from mrkutil.base import BaseHandler
from .trigger_service import trigger_service
from mrkutil.responses import ServiceResponse
from mrkutil.exception import ServiceException
from mrkutil.enum import JobStatusEnum
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
        on_message_process_complete (Callable): The callback function to be called when a message is processed.
        base_handler (type[BaseHandler]): The base handler class to use for processing messages.
        use_job_cache (bool): Whether to use the job cache.
        rabbit_url (str): The RabbitMQ URL.

    Methods:
        handle: Handles the incoming message.

    """

    def __init__(
        self,
        exchange: str,
        on_message_process_complete: Callable | None = None,
        base_handler: type[BaseHandler] | None = None,
        use_job_cache: bool = True,
        rabbit_url: str = os.getenv("RABBIT_URL"),
    ):
        if base_handler:
            if not isinstance(base_handler, type):
                raise Exception("Service handler must be a class")
            if not issubclass(base_handler, BaseHandler):
                raise Exception("Service handler must be a derivate of BaseHandler")
        self.base_handler = base_handler if base_handler else BaseHandler
        self.exchange = exchange
        self.on_message_process_complete = on_message_process_complete
        self.use_job_cache = use_job_cache
        self.rabbit_url = rabbit_url

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
                response = self.base_handler.process_data(
                    body["data"], body["meta"]["correlationId"]
                )
                if response:
                    trigger_service(
                        request_data=response,
                        destination=body["meta"]["source"],
                        source=self.exchange,
                        corr_id=body["meta"]["correlationId"],
                        rabbit_url=self.rabbit_url,
                    )
                return True
        except ServiceException as e:
            data = body.get("data", {})
            logger.error(
                f"Error occured with job, message {e.message} errors {e.errors}"
            )
            if (
                data
                and isinstance(data, dict)
                and isinstance(data.get("request", {}), dict)
                and data.get("request", {}).get("job_key")
                and self.use_job_cache
            ):
                from mrkutil.cache import JobCache

                JobCache().set_progress(
                    data.get("request", {}).get("job_key"),
                    JobStatusEnum.FAILED,
                    {"message": e.message, "errors": e.errors},
                )
            else:
                return ServiceResponse(code=e.code, message=e.message, errors=e.errors)
        except Exception as e:
            logger.exception("error parsing received message {}".format(str(e)))
            if method_exists:
                destination = body.get("meta", {}).get("source")
                if destination:
                    if (
                        data
                        and isinstance(data, dict)
                        and isinstance(data.get("request", {}), dict)
                        and data.get("request", {}).get("job_key")
                        and self.use_job_cache
                    ):
                        from mrkutil.cache import JobCache

                        JobCache().set_progress(
                            data.get("request", {}).get("job_key"),
                            JobStatusEnum.FAILED,
                            {
                                "message": f"Unexpected error occured with job {data.get('request', {}).get('job_key')}"
                            },
                        )
                    else:
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
                            rabbit_url=self.rabbit_url,
                        )
        finally:
            try:
                if self.on_message_process_complete:
                    self.on_message_process_complete()
            except Exception as e:
                logger.error(f"On message complete failed. Error {e}")
        return False


def listen(
    exchange: str,
    exchange_type: str,
    queue: str,
    async_processing: bool = True,
    max_threads: int = 10,
    on_message_process_complete: Callable | None = None,
    base_handler: type[BaseHandler] | None = None,
    use_job_cache: bool = True,
    rabbit_url: str = os.getenv("RABBIT_URL"),
):
    """
    Listens for messages on a RabbitMQ exchange and processes them asynchronously if wanted.

    Args:
        exchange (str): The name of the RabbitMQ exchange to listen on.
        exchange_type (str): The type of the RabbitMQ exchange.
        queue (str): The name of the RabbitMQ queue to bind to the exchange.
        async_processing (bool, optional): Whether to process messages asynchronously. Defaults to True.
        max_threads (int, optional): The maximum number of threads to use for processing messages. Defaults to 10.
        on_message_process_complete (Callable, optional): A callback function to be called when a message is processed. Defaults to None.
        base_handler (type[BaseHandler], optional): The base handler class to use for processing messages. Defaults to None.
        use_job_cache (bool, optional): Whether to use the job cache. Defaults to True.
        rabbit_url (str, optional): The RabbitMQ URL. Defaults to the value of the RABBIT_URL environment variable.
    """
    subscriber = rabbit_pubsub.Subscriber(
        amqp_url=rabbit_url,
        exchange=exchange,
        exchange_type=exchange_type,
        queue=queue,
        async_processing=async_processing,
        max_threads=max_threads,
    )
    subscriber.subscribe(
        Subscriber(
            exchange,
            on_message_process_complete,
            base_handler=base_handler,
            use_job_cache=use_job_cache,
            rabbit_url=rabbit_url,
        )
    )
    subscriber.start()
    subscriber.join()
