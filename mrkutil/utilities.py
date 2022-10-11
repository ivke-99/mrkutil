import logging
import random
import string
import uuid

logger = logging.getLogger(__name__)


def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_uuid():
    return uuid.uuid4().hex
