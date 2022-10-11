from rabbitmqpubsub import rabbit_pubsub
from mrkutil.base import BaseHandler
from .trigger_service import trigger_service
import logging
import os

logger = logging.getLogger(__name__)


class Subscriber():
    def __init__(self, exchange):
        self.exchange = exchange

    def handle(self, body=None):
        response = None
        try:
            response = BaseHandler.process_data(body['data'], body['meta']['correlationId'])

            trigger_service(
                request_data=response,
                destination=body['meta']['source'],
                source=self.exchange,
                corr_id=body['meta']['correlationId']
            )
            return True

        except Exception as e:
            logger.exception("error parsing received message {}".format(str(e)))

        return False


def listen(exchange, exchange_type, queue, async_processing=True):
    subscriber = rabbit_pubsub.Subscriber(
        amqp_url=os.getenv("RABBIT_URL"),
        exchange=exchange,
        exchange_type=exchange_type,
        queue=queue,
        async_processing=async_processing
    )
    subscriber.subscribe(Subscriber(exchange))
    subscriber.start()
    subscriber.join()
