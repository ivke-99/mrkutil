from rabbitmqpubsub.rabbit_pubsub import RpcClient
from mrkutil.utilities import random_string
import logging
import os

logger = logging.getLogger(__name__)


def call_service(request_data, destination, source, corr_id=None):
    rpc = RpcClient(
        amqp_url=os.getenv("RABBIT_URL"),
        exchange=source,
        queue="temp_{}".format(random_string(6)),
    )
    response = rpc.call(
        data=request_data,
        recipient=destination,
        corr_id=corr_id
    )
    response_data = response
    return response_data['data']
