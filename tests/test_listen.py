import threading
import time
from mrkutil.communication import listen, trigger_service
from mrkutil.responses import ServiceResponse
from mrkutil.base import BaseHandler
import os
from mrkutil.exception import ServiceException

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://rabbit:rabbit@localhost:5672/rabbit")


def test_listen_receives_message():
    """Test that listen() can receive a triggered message"""

    # Set up a threading event to coordinate between publisher and subscriber
    message_received = threading.Event()

    def message_callback():
        message_received.set()

    # Start listener in a separate thread
    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": False,
            "on_message_process_complete": message_callback,
            "exchange": "test_exchange",
            "exchange_type": "direct",
            "queue": "test_queue",
            "max_threads": 1,
            "rabbit_url": RABBIT_URL,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()

    # Give the listener time to initialize
    time.sleep(1)

    # Trigger a test message
    test_message = ServiceResponse(code=200, message="test message")
    trigger_service(
        request_data=test_message,
        destination="test_exchange",
        source="test_source",
        rabbit_url=RABBIT_URL,
    )

    # Wait for message to be received
    assert message_received.wait(timeout=5), "Message was not received within timeout"


def test_listen_multiple_messages():
    """Test that listen() can handle multiple messages"""

    received_count = 0
    message_received = threading.Event()

    def message_callback():
        nonlocal received_count
        received_count += 1
        if received_count == 3:
            message_received.set()

    # Start listener
    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": True,
            "max_threads": 3,
            "on_message_process_complete": message_callback,
            "exchange": "test_exchange2",
            "exchange_type": "direct",
            "queue": "test_queue2",
            "rabbit_url": RABBIT_URL,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()

    time.sleep(1)

    # Send multiple messages
    test_message = ServiceResponse(code=200, message="test message")
    for _ in range(3):
        trigger_service(
            request_data=test_message,
            destination="test_exchange2",
            source="test_source",
            rabbit_url=RABBIT_URL,
        )
        time.sleep(0.1)

    # Wait for all messages to be received
    assert message_received.wait(timeout=5), (
        "Not all messages were received within timeout"
    )
    assert received_count == 3, f"Expected 3 messages, but received {received_count}"


def test_listen_error_handling():
    """Test that listen() handles handler exceptions and still calls the completion callback."""
    message_received = threading.Event()
    error_logged = threading.Event()

    class ErrorHandler(BaseHandler):
        @staticmethod
        def name():
            return "error_method"

        def process(self, data, corr_id):
            raise Exception("Intentional error for testing")

    def message_callback():
        message_received.set()

    # Patch logger to set event on error
    import logging

    ErrorHandler.sub_classes = {"error_method": ErrorHandler}

    logger = logging.getLogger("mrkutil.communication.listen")
    orig_exception = logger.exception

    def fake_exception(msg):
        error_logged.set()
        orig_exception(msg)

    logger.exception = fake_exception

    # Start listener with error handler
    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": False,
            "on_message_process_complete": message_callback,
            "exchange": "test_exchange_err",
            "exchange_type": "direct",
            "queue": "test_queue_err",
            "max_threads": 1,
            "rabbit_url": RABBIT_URL,
            "base_handler": ErrorHandler,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()
    time.sleep(1)

    # Trigger a message that will cause an error
    test_message = {"method": "error_method"}
    trigger_service(
        request_data=test_message,
        destination="test_exchange_err",
        source="test_source",
        rabbit_url=RABBIT_URL,
    )

    # Wait for error to be logged and callback to be called
    assert message_received.wait(timeout=5), (
        "Completion callback was not called after error"
    )
    assert error_logged.wait(timeout=5), "Error was not logged by listen handler"

    # Restore logger
    logger.exception = orig_exception


def test_listen_service_exception():
    """Test that listen() handles ServiceException and returns ServiceResponse."""
    message_received = threading.Event()
    error_logged = threading.Event()

    class ServiceExceptionHandler(BaseHandler):
        @staticmethod
        def name():
            return "service_exception_method"

        def process(self, data, corr_id):
            raise ServiceException(400, "Service error", errors=["err1"])

    def message_callback():
        message_received.set()

    ServiceExceptionHandler.sub_classes = {
        "service_exception_method": ServiceExceptionHandler
    }

    import logging

    logger = logging.getLogger("mrkutil.communication.listen")
    orig_exception = logger.exception

    def fake_exception(msg):
        error_logged.set()
        orig_exception(msg)

    logger.exception = fake_exception

    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": False,
            "on_message_process_complete": message_callback,
            "exchange": "test_exchange_se",
            "exchange_type": "direct",
            "queue": "test_queue_se",
            "max_threads": 1,
            "rabbit_url": RABBIT_URL,
            "base_handler": ServiceExceptionHandler,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()
    time.sleep(1)

    test_message = {"method": "service_exception_method"}
    trigger_service(
        request_data=test_message,
        destination="test_exchange_se",
        source="test_source",
        rabbit_url=RABBIT_URL,
    )

    assert message_received.wait(timeout=5), (
        "Completion callback was not called after ServiceException"
    )
    assert error_logged.wait(timeout=5), "Error was not logged by listen handler"
    logger.exception = orig_exception


def test_listen_service_exception_jobcache():
    """Test that listen() handles ServiceException and sets JobCache status to FAILED if job_key is present and use_job_cache is True."""
    message_received = threading.Event()
    job_key = f"job_{os.getpid()}"

    class ServiceExceptionHandler(BaseHandler):
        @staticmethod
        def name():
            return "service_exception_jobcache"

        def process(self, data, corr_id):
            raise ServiceException(code=400, message="Job error", errors=["err2"])

    ServiceExceptionHandler.sub_classes = {
        "service_exception_jobcache": ServiceExceptionHandler
    }

    def message_callback():
        message_received.set()

    from mrkutil.cache.job_cache import JobCache

    job_cache = JobCache()
    # Pre-create the job in Redis
    job_cache.set(job_key, {"status": "PENDING"})

    listener_thread = threading.Thread(
        target=listen,
        kwargs={
            "async_processing": False,
            "on_message_process_complete": message_callback,
            "exchange": "test_exchange_jc",
            "exchange_type": "direct",
            "queue": "test_queue_jc",
            "max_threads": 1,
            "rabbit_url": RABBIT_URL,
            "base_handler": ServiceExceptionHandler,
            "use_job_cache": True,
        },
    )
    listener_thread.daemon = True
    listener_thread.start()
    time.sleep(1)

    test_message = {
        "method": "service_exception_jobcache",
        "request": {"job_key": job_key},
    }
    trigger_service(
        request_data=test_message,
        destination="test_exchange_jc",
        source="test_source",
        rabbit_url=RABBIT_URL,
    )

    assert message_received.wait(timeout=5), (
        "Completion callback was not called after ServiceException with job_key"
    )

    # Check that the job status in Redis is now FAILED and error message is present
    job = job_cache.get(job_key)
    assert job["status"] == "FAILED"
    assert "Job error" in job["data"]["message"]
    assert "err2" in str(job["data"].get("errors", ""))
    # Clean up
    job_cache.delete(job_key)
