## mrkutil

This is a Python package containing common functions for Python service-based architecture.

### Base Handler

BaseHandler is an abstract class used for implementing function/class level factory pattern.

```python
data = ["method"] = "my_defined_method"
handler = BaseHandler.process_data(data)
```

Where my_defined_method is the name of the child handler name static method.

### Base Redis

Simple class with utility functions for working with redis.
Key is the prefix for all redis objects, and timeout is how long redis keeps the object in cache.
Example usage:

```python
cache = RedisBase(key="key", timeout=300)
res = cache.get("this_key")
```

### Communication

Communication package is a wrapper arround RabbitMQPubSub library that provides a simple interface for publishing and subscribing to messages.

call_service is a function that can be used to call a service with a message and await its response.

```python
call_service(request_data=data, destination="some_exchange", source="self_exchange")
```

listen is a function that can be used to listen to a queue and call a function when a message is received.
Commonly implemented in microservices in main.py as a long living process.

```python
listen(exchange="some_exchange", exchange_type="direct", queue="some_queue")
```

trigger_service triggers a service with a message but does not wait for a response. Useful for fire and forget scenarios.

```python
trigger_service(request_data=data, destination="some_exchange", source="self_exchange")
```

### Logging Configuration

The `get_logging_config` function in `mrkutil/logging/logging_config.py` generates a logging configuration dictionary based on the provided parameters. It supports both JSON and default formatters.

```python
config = get_logging_config(log_level="DEBUG", json_format=False, api=True)
```

### Pagination

The `paginate` function in mongoengine.py and sqlalchemy.py is a utility function that paginates a list of items based on the provided page and page size.
It is useful in microservices where there is no accessible web framework pagination method, and to avoid code duplication.

There is also a dependency.py which contains pagination_params function that are usually used in fastapi dependency injection.

```python
paginate(items, page_number=1, page_size=10, direction="asc", sort_by="id")
```

### Responses

ServiceResponse class is a utility class for creating a standard response object that can be used in all services.
It is useful for standardizing the response format across all services.

```python
ServiceResponse(code=400, message="Validation Error", errors=[{"field": "name", "message": "Name is required"}])
```

## Authors

- [@nmrkic](https://github.com/nmrkic)
- [@ivke-99](https://github.com/ivke-99)

## Deployment to PyPI

To deploy this package to PyPI, use the following commands:

```bash
flit build
flit publish
```

## Contributing

Contributions are always welcome! If you have any suggestions or improvements, feel free to submit a pull request or open an issue.
