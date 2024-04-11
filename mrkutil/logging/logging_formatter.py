import logging
import json


class JSONFormatter(logging.Formatter):
    """
    A custom logging formatter that formats log records as JSON.

    This formatter is designed to format log records as JSON objects, making it easier
    to process and analyze log data. It performs additional formatting and filtering
    operations on the log records before converting them to JSON.

    Attributes:
        None

    Methods:
        filter(record): Filters and modifies the log record before formatting it as JSON.

    Usage:
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
    """

    def filter(self, record):
        exception = None
        if record.exc_info:
            try:
                exception = repr(super().formatException(record.exc_info))
                exception = json.dumps(exception[1:-1])[1:-1]
            except Exception as e:
                print(f"error in error {e}")
            record.exc_info = None
        if isinstance(record.msg, str):
            record.msg = record.msg.replace('"', "")
        record.user_id = ""
        record.http_method = ""
        record.url = ""
        record.clientip = ""
        record.trace = ""
        try:
            if exception:
                record.trace = exception
            if hasattr(record, "request"):
                record.clientip = record.request.client.host
                record.clientip = record.clientip.split(":")[0]
            if "CUSTOM" in record.msg:
                record.msg = record.msg.replace("'", '"')
                msg = json.loads(record.msg[7:])
                record.user_id = msg["user_id"]
                record.url = msg["url"]
                record.http_method = msg["http_method"]
                record.msg = ""
        except Exception:
            pass
        return record
