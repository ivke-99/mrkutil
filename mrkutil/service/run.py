import os
import sys
from mrkutil.utilities import import_all_subclasses_from_package, register_service_pid
from mrkutil.communication import listen
import logging

logger = logging.getLogger(__name__)


def __run_service_prod(exchange: str, exchange_type: str, queue: str, max_threads: int):
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
        )
        sys.exit(0)
    finally:
        os.unlink(pidfile)


def __run_service_develop(
    exchange: str, exchange_type: str, queue: str, max_threads: int
):
    """
    Service starting point with watchfiles
    """
    try:
        __run_service_prod(exchange, exchange_type, queue, max_threads)
    except KeyboardInterrupt:
        logger.info("Detecting changes, reloading..")


def run_service(
    develop: bool,
    exchange: str,
    exchange_type: str,
    queue: str,
    max_threads: int,
    root_package: str = "package",
):
    """
    Run service in develop mode or production mode
    develop: bool, if True, run service in develop mode
    exchange: str, exchange name - make sure its unique
    exchange_type: str, exchange type usually direct
    queue: str, queue name
    max_threads: int, max threads - start with 5 and increase if needed
    root_package: str, root package name
    """
    if develop:
        from watchfiles import run_process

        logger.info("Running watchfiles, will watch for changes in current service ...")
        run_process(
            root_package,
            target=__run_service_develop,
            args=(exchange, exchange_type, queue, max_threads),
        )
    else:
        __run_service_prod(exchange, exchange_type, queue, max_threads)
