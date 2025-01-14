from mrkutil.base import BaseHandler
from mrkutil.communication.listen import Subscriber


class NewSubHandlerClass(BaseHandler):

    @staticmethod
    def name():
        return "NewSubHandlerClass"

    def process(self, data, corr_id):
        return "NewSubHandlerClass"


class SecondSubBaseHandler(BaseHandler):
    @staticmethod
    def name():
        return None


class NewSecondHandlerClass(SecondSubBaseHandler):

    @staticmethod
    def name():
        return "NewSecondHandlerClass"

    def process(self, data, corr_id):
        return "NewSecondHandlerClass"


class TestBaseHandler:

    def test_initialize_working(self):
        BaseHandler.sub_classes = {}
        SecondSubBaseHandler.sub_classes = {}

        subscriber = Subscriber('temp', None)
        print(subscriber.base_handler)
        response = subscriber.base_handler.process_data({"method": "NewSubHandlerClass"}, "corr_id")
        assert response == "NewSubHandlerClass"

        subscriber = Subscriber('temp', None, SecondSubBaseHandler)
        print(subscriber.base_handler)
        response = subscriber.base_handler.process_data({"method": "NewSecondHandlerClass"}, "corr_id")
        assert response == "NewSecondHandlerClass"
