import os
import sys
from mrkutil.utilities import import_all_subclasses_from_package, register_service_pid
from mrkutil.communication import listen
from typing import Callable
import logging

logger = logging.getLogger(__name__)


def __run_service_prod(
    exchange: str,
    exchange_type: str,
    queue: str,
    max_threads: int,
    on_message_processing_complete: Callable = None,
):
    """
    Service starting point
    """
    import_all_subclasses_from_package("package.app.handlers")
    pidfile = register_service_pid(exchange)
    try:
        logger.info("Starting ...")
        listen(
            exchange=exchange,
            exchange_type=exchange_type,
            queue=queue,
            max_threads=max_threads,
            on_message_process_complete=on_message_processing_complete,
        )
        sys.exit(0)
    finally:
        os.unlink(pidfile)


def __run_service_develop(
    exchange: str,
    exchange_type: str,
    queue: str,
    max_threads: int,
    on_message_processing_complete: Callable = None,
):
    """
    Service starting point with watchfiles
    """
    try:
        __run_service_prod(
            exchange, exchange_type, queue, max_threads, on_message_processing_complete
        )
    except KeyboardInterrupt:
        logger.info("Detecting changes, reloading..")


def run_service(
    develop: bool,
    exchange: str,
    exchange_type: str,
    queue: str,
    max_threads: int,
    on_message_processing_complete: Callable = None,
    root_package: str = "package",
):
    """
    Run service in develop mode or production mode.

    Parameters:
    - develop (bool): If True, run service in develop mode.
    - exchange (str): Exchange name - must be unique.
    - exchange_type (str): Exchange type, usually 'direct'.
    - queue (str): Queue name.
    - max_threads (int): Max number of threads; start with 5 and increase if needed.
    - on_message_processing_complete (Callable): Optional callback.
    - root_package (str): Root package name.
    """
    if develop:
        try:
            from watchfiles import run_process
        except (ModuleNotFoundError, ImportError):
            logger.warning(
                "watchfiles is not installed. Development mode with auto-reloading is disabled. "
                "Run 'uv add watchfiles' to enable it."
            )
            logger.info("Falling back to production mode...")
            __run_service_prod(
                exchange, exchange_type, queue, max_threads, on_message_processing_complete
            )
            return

        logger.info("Running in development mode with watchfiles. Watching for changes...")
        run_process(
            root_package,
            target=__run_service_develop,
            args=(
                exchange,
                exchange_type,
                queue,
                max_threads,
                on_message_processing_complete,
            ),
        )
    else:
        __run_service_prod(
            exchange, exchange_type, queue, max_threads, on_message_processing_complete
        )
