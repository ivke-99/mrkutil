from mrkutil.base import BaseHandler


class NewHandlerClass(BaseHandler):

    def name():
        return "NewHandlerClass"

    def process(self, data, corr_id):
        return "NewHandlerClass"


class TestBaseHandler:

    def test_initialize_working(self):
        BaseHandler.sub_classes = {}
        data = {
            "method": "NewHandlerClass"
        }
        BaseHandler.process_data(data, "corr_id")
        print(BaseHandler.sub_classes)
        assert BaseHandler.sub_classes != {}

    def test_handler_working(self):
        BaseHandler.sub_classes = {}
        data = {
            "method": "NewHandlerClass"
        }
        response = BaseHandler.process_data(data, "corr_id")
        print(response)
        assert response == "NewHandlerClass"

    def test_handler_no_method(self):
        BaseHandler.sub_classes = {}
        data = {
            "method": "NoHandlerClass"
        }
        response = BaseHandler.process_data(data, "corr_id")
        print(response)
        assert response['code'] == 404
