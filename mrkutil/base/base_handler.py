import abc
import logging
from mrkutil.responses import ServiceResponse

logger = logging.getLogger(__name__)


class BaseHandler(metaclass=abc.ABCMeta):
    """
    Base class for implementing handlers.

    This class defines the interface for handlers and provides a method for processing data.
    Subclasses must implement the `name` and `process` methods.
    """
    sub_classes = {}

    @classmethod
    def initialize(cls):
        for sub_cls in cls.__subclasses__():
            if sub_cls.name():
                cls.sub_classes[sub_cls.name()] = sub_cls

    @abc.abstractmethod
    def name():
        """
        Get the name of the handler.

        Returns:
            str: The name of the handler.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process(self, data, corr_id):
        """
        Process the data.

        Args:
            data (dict): The data to be processed.
            corr_id (str): The correlation ID.

        Returns:
            dict: The result of the processing.
        """
        raise NotImplementedError

    @classmethod
    def process_data(cls, data, corr_id):
        """
        Process the data using the appropriate handler.

        Args:
            data (dict): The data to be processed.
            corr_id (str): The correlation ID.

        Returns:
            dict: The result of the processing.
        """

        # Initialize subl class list on the first use
        if not cls.sub_classes:
            cls.initialize()

        logger.info(f"process_data method: {data.get('method')}")
        handler = cls.sub_classes.get(data.get('method', ""), None)
        if handler:
            logger.info(f"process_data found method {handler}")
            return handler().process(data, corr_id)
        logger.warning(f"No handler covering this method, method: {data.get('method')}")
        return ServiceResponse(code=404, message="Method not found.")
