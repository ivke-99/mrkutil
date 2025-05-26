import os
import time
import threading
import pytest
from mrkutil.communication import listen, call_service, acall_service
from mrkutil.base import BaseHandler

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://rabbit:rabbit@localhost:5672/rabbit")


# Simple echo handler for testing
class EchoHandler(BaseHandler):
    @staticmethod
    def name():
        return "echo"

    def process(self, data, corr_id):
        print(f"EchoHandler processing: data={data}, corr_id={corr_id}")
        return {"echoed": data, "corr_id": corr_id}


def start_listener(exchange, queue):
    BaseHandler.sub_classes = {}
    BaseHandler.sub_classes["echo"] = EchoHandler

    def _listen():
        print(f"[Listener] Starting listen on exchange={exchange}, queue={queue}")
        listen(
            exchange=exchange,
            exchange_type="direct",
            queue=queue,
            max_threads=1,
            rabbit_url=RABBIT_URL,
        )
        print(f"[Listener] Exiting listen on exchange={exchange}, queue={queue}")

    thread = threading.Thread(target=_listen, daemon=True)
    thread.start()
    time.sleep(2)  # Give listener time to start
    return thread


def test_call_service_integration():
    exchange = f"test_exchange_{os.getpid()}"
    queue = f"test_queue_{os.getpid()}"
    print("Starting listener...")
    start_listener(exchange, queue)
    req = {"method": "echo", "request": {"message": "Hello, world!"}}
    print("Calling service...")
    resp = call_service(
        req, destination=exchange, source=exchange, rabbit_url=RABBIT_URL
    )
    print("Got response:", resp)
    assert resp == req


@pytest.mark.asyncio
async def test_acall_service_integration():
    exchange = f"test_exchange_async_{os.getpid()}"
    queue = f"test_queue_async_{os.getpid()}"
    print("Starting listener (async)...")
    start_listener(exchange, queue)
    req = {"method": "echo", "request": {"message": "Hello, world!"}}
    print("Calling async service...")
    resp = await acall_service(
        req, destination=exchange, source=exchange, rabbit_url=RABBIT_URL
    )
    print("Got async response:", resp)
    assert resp == req
