def get_logging_config(log_level: str, json_format: bool, api: bool = False):
    """
    Generate a logging configuration dictionary based on the provided parameters.

    Args:
        log_level (str): The log level to be used for the handlers.
        json_format (bool): Flag indicating whether to use JSON formatter or default formatter.
        api (bool, optional): Flag indicating whether the configuration is for an API. Defaults to False.

    Returns:
        dict: The logging configuration dictionary.

    """
    config = {
        "version": 1,
        "disable_existing_loggers": True,
        "filters": {"json_formatter": {"()": "mrkutil.logging.JSONFormatter"}},
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s - %(name)s: %(message)s",
            },
            "json": {
                "format": '{"clientip": "%(clientip)s", "time": "%(asctime)s", "log_level": "%(levelname)s", "user_id": "%(user_id)s", "module": "%(module)s", "function": "%(name)s", "lineno": "%(lineno)s", "url": "%(url)s", "http_method": "%(http_method)s", "message": "%(message)s", "trace": "%(trace)s"}',  # noqa
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "json" if json_format else "default",
                "filters": ["json_formatter"] if json_format else [],
            }
        },
    }

    service_loggers = {
        "main": {"level": log_level, "handlers": ["console"]},
        "app": {"level": log_level, "handlers": ["console"]},
        "package": {"level": log_level, "handlers": ["console"]},
        "rabbitmqpubsub": {"level": log_level, "handlers": ["console"]},
        "mrkutil": {"level": log_level, "handlers": ["console"]},
    }

    api_loggers = {
        "multipart": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "main": {"level": log_level, "handlers": ["console"]},
        "app": {"level": log_level, "handlers": ["console"]},
        "package": {"level": log_level, "handlers": ["console"]},
        "uvicorn": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "mrkutil": {"level": log_level, "handlers": ["console"]},
    }

    config["loggers"] = api_loggers if api else service_loggers
    return config
