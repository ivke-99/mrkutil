import logging
import json


class JSONFormatter(logging.Formatter):
    def filter(self, record):
        exception = None
        if record.exc_info:
            try:
                exception = repr(super().formatException(record.exc_info))
                exception = json.dumps(exception[1:-1])[1:-1]
            except Exception as e:
                print(f'error in error {e}')
            record.exc_info = None
        if type(record.msg) == str:
            record.msg = record.msg.replace('"', '')
        record.user_id = ""
        record.http_method = ""
        record.url = ""
        record.clientip = ""
        record.trace = ""
        try:
            if exception:
                record.trace = exception
            if hasattr(record, 'request'):
                record.clientip = record.request.client.host
                record.clientip = record.clientip.split(':')[0]
            if "CUSTOM" in record.msg:
                record.msg = record.msg.replace("'", '"')
                msg = json.loads(record.msg[7:])
                record.user_id = msg['user_id']
                record.url = msg['url']
                record.http_method = msg['http_method']
                record.msg = ""
        except Exception:
            pass
        return record
