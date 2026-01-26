import logging
import random
import string
import uuid
import importlib
import pkgutil
import os
import sys
from typing import TypedDict

logger = logging.getLogger(__name__)


class RequestData(TypedDict):
    method: str
    request: dict


def random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_uuid():
    return uuid.uuid4().hex


def import_all_subclasses_from_package(package_name):
    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        importlib.import_module(module_name)


def register_service_pid(service_name: str) -> str:
    pid = str(os.getpid())
    if not os.path.isdir("/tmp/service"):
        os.makedirs("/tmp/service")
    pidfile = f"/tmp/service/service_{service_name}.pid"
    if os.path.isfile(pidfile):
        logger.warning(f"Service {service_name} is already running")
        sys.exit(1)
    with open(pidfile, "w") as file:
        file.write(pid)
        file.write("\n")
    return pidfile
