import threading
import time
import os
import pytest
from mrkutil.communication import trigger_service, atrigger_service
from mrkutil.responses import ServiceResponse

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://rabbit:rabbit@localhost:5672/rabbit")


def test_trigger_service_sends_message():
    # Set up threading event to coordinate
    message_received = threading.Event()
    received_data = None

    def message_callback():
        nonlocal received_data
        received_data = True
        message_received.set()

    # Start listener in separate thread
    from mrkutil.communication import listen

    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": False,
            "on_message_process_complete": message_callback,
            "exchange": "test_trigger_exchange",
            "exchange_type": "direct",
            "queue": "test_trigger_queue",
            "max_threads": 1,
            "rabbit_url": RABBIT_URL,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()

    # Give listener time to initialize
    time.sleep(1)

    # Trigger test message
    test_message = ServiceResponse(code=200, message="test trigger message")
    trigger_service(
        request_data=test_message,
        destination="test_trigger_exchange",
        source="test_source",
        rabbit_url=RABBIT_URL,
    )

    # Wait for message to be received
    assert message_received.wait(timeout=5), "Message was not received within timeout"
    assert received_data


@pytest.mark.asyncio
async def test_atrigger_service_sends_message():
    message_received = threading.Event()
    received_data = None

    def message_callback():
        nonlocal received_data
        received_data = True
        message_received.set()

    # Start listener
    from mrkutil.communication import listen

    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": False,
            "on_message_process_complete": message_callback,
            "exchange": "test_atrigger_exchange",
            "exchange_type": "direct",
            "queue": "test_atrigger_queue",
            "max_threads": 1,
            "rabbit_url": RABBIT_URL,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()

    time.sleep(1)

    # Trigger async test message
    test_message = ServiceResponse(code=200, message="test async trigger message")
    await atrigger_service(
        request_data=test_message,
        destination="test_atrigger_exchange",
        source="test_source",
        rabbit_url=RABBIT_URL,
    )

    assert message_received.wait(timeout=5), (
        "Async message was not received within timeout"
    )
    assert received_data
