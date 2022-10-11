from unittest import TestCase
from mrkutil.communication import listen, trigger_service
import json
import time
import os


class SubsHandler():
    results = {}

    def handle(self, body):
        body = json.loads(body)
        print(body)
        if body.get("data", {}).get("test") not in self.results.keys():
            self.results[body['data']['test']] = []
        self.results[body['data']['test']].append(body)


class SubscriberTest(TestCase):

    def setUp(self):
        self.test_handler = SubsHandler()

    def tearDown(self):
        self.test_handler.results = []

    def test_subscriber_async(self):
        amqp_url = "amqp://guest:guest@127.0.0.1:5672/guest"
        os.environ['RABBIT_URL'] = amqp_url
        subscriber = listen(
            listener=self.test_handler,
            exchange="some",
            exchange_type="direct",
            queue="somequeue",
            async_processing=True
        )
        subscriber.subscribe(self.test_handler)
        subscriber.start()

        for i in range(10):
            trigger_service(
                request_data={"request_number": i, "test": "b"},
                destination="some",
                source="someother",
                corr_id="aaaa"
            )
        time.sleep(2)
        subscriber.stop_consuming()
        subscriber.join()
        # print(subscriber._observers[0])
        self.assertEqual(len(self.test_handler.results["b"]), 10)
        self.test_handler.results = []
