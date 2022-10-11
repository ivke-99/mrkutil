import abc
import logging

logger = logging.getLogger(__name__)


class BaseHandler(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def name(cls):
        raise "Not implmented abstract method"

    @abc.abstractmethod
    def process(self, data, corr_id):
        raise "Not implmented abstract method"

    @classmethod
    def process_data(cls, data, corr_id):
        logger.info(f"process_data method: {data.get('method', None)}")
        handler = None
        for sub_cls in cls.__subclasses__():
            if data.get('method', None) == sub_cls.name():
                handler = sub_cls
                break
        logger.info(f"process_data found method {handler}")
        if handler:
            return handler().process(data, corr_id)
        logger.warning("No handler covering this method, method: {}".format(data.get('method', "Empty")))
        return False
