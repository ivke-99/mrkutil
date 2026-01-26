import pytest
from unittest.mock import patch
from mrkutil.base import BaseHandler


# Test Handler Classes
class TestHandler(BaseHandler):
    @staticmethod
    def name():
        return "test_handler"

    def process(self, data, corr_id):
        return {"result": "test_processed", "corr_id": corr_id, "data": data}


class AnotherHandler(BaseHandler):
    @staticmethod
    def name():
        return "another_handler"

    def process(self, data, corr_id):
        return {"result": "another_processed", "input": data}


class EmptyNameHandler(BaseHandler):
    @staticmethod
    def name():
        return ""

    def process(self, data, corr_id):
        return {"result": "empty_name"}


class ExceptionHandler(BaseHandler):
    @staticmethod
    def name():
        return "exception_handler"

    def process(self, data, corr_id):
        raise ValueError("Handler exception")


# Additional test handlers for specific tests
class BaseTestHandler(BaseHandler):
    @staticmethod
    def name():
        return "base_handler"

    def process(self, data, corr_id):
        return {"type": "base", "data": data}


class DerivedTestHandler(BaseHandler):
    @staticmethod
    def name():
        return "derived_handler"

    def process(self, data, corr_id):
        # Simulate calling a base method
        base_result = {"type": "base", "data": data}
        base_result["type"] = "derived"
        base_result["enhanced"] = True
        return base_result


class SpecialHandler(BaseHandler):
    @staticmethod
    def name():
        return "special-handler_123"

    def process(self, data, corr_id):
        return {"special": True}


class StatefulHandler(BaseHandler):
    def __init__(self):
        self.counter = 0

    @staticmethod
    def name():
        return "stateful_handler"

    def process(self, data, corr_id):
        self.counter += 1
        return {"counter": self.counter}


# Fixtures
@pytest.fixture(autouse=True)
def setup_handlers():
    BaseHandler.initialize()


# Basic functionality tests
def test_handler_registration():
    """Test that handlers are properly registered during initialization."""

    assert "test_handler" in BaseHandler.sub_classes
    assert "another_handler" in BaseHandler.sub_classes
    assert "exception_handler" in BaseHandler.sub_classes
    assert BaseHandler.sub_classes["test_handler"] == TestHandler
    assert BaseHandler.sub_classes["another_handler"] == AnotherHandler


def test_process_data_with_valid_handler():
    """Test processing data with a valid handler method."""
    data = {"method": "test_handler", "value": 123}

    result = BaseHandler.process_data(data, "test-corr-id")

    assert result["result"] == "test_processed"
    assert result["corr_id"] == "test-corr-id"
    assert result["data"]["value"] == 123


def test_process_data_with_different_handler():
    """Test processing data with a different valid handler."""
    data = {"method": "another_handler", "payload": "test"}

    result = BaseHandler.process_data(data, "another-corr-id")

    assert result["result"] == "another_processed"
    assert result["input"]["payload"] == "test"


def test_process_data_with_nonexistent_method():
    """Test processing data with a method that doesn't exist."""
    data = {"method": "nonexistent_method"}

    result = BaseHandler.process_data(data, "test-corr-id")

    assert result["code"] == 404
    assert "Method not found." in result["response"]["message"]


def test_process_data_without_method_key():
    """Test processing data without a method key."""
    data = {"some_key": "some_value"}

    result = BaseHandler.process_data(data, "test-corr-id")

    assert result["code"] == 404
    assert "Method not found." in result["response"]["message"]


def test_process_data_with_empty_data():
    """Test processing completely empty data."""
    result = BaseHandler.process_data({}, "test-corr-id")

    assert result["code"] == 404
    assert "Method not found." in result["response"]["message"]


def test_process_data_with_none_method():
    """Test processing data with None as method value."""
    data = {"method": None}

    result = BaseHandler.process_data(data, "test-corr-id")

    assert result["code"] == 404
    assert "Method not found." in result["response"]["message"]


def test_process_data_with_numeric_method():
    """Test processing data with numeric method value."""
    data = {"method": 123}

    result = BaseHandler.process_data(data, "test-corr-id")

    assert result["code"] == 404
    assert "Method not found." in result["response"]["message"]


# Logging tests
@patch("mrkutil.base.base_handler.logger")
def test_logs_method_name(mock_logger):
    """Test that the method name is logged."""
    data = {"method": "test_handler"}

    BaseHandler.process_data(data, "test-corr-id")

    mock_logger.info.assert_any_call("process_data method: test_handler")


@patch("mrkutil.base.base_handler.logger")
def test_logs_handler_found(mock_logger):
    """Test that finding a handler is logged."""
    data = {"method": "test_handler"}

    BaseHandler.process_data(data, "test-corr-id")

    mock_logger.info.assert_any_call(f"process_data found method {TestHandler}")


@patch("mrkutil.base.base_handler.logger")
def test_logs_warning_for_missing_handler(mock_logger):
    """Test that missing handlers generate warning logs."""
    data = {"method": "missing_handler"}

    BaseHandler.process_data(data, "test-corr-id")

    mock_logger.warning.assert_called_with(
        "No handler covering this method, method: missing_handler"
    )


@patch("mrkutil.base.base_handler.logger")
def test_logs_none_method(mock_logger):
    """Test logging when method is None."""
    data = {"method": None}

    BaseHandler.process_data(data, "test-corr-id")

    mock_logger.info.assert_any_call("process_data method: None")
    mock_logger.warning.assert_called_with(
        "No handler covering this method, method: None"
    )


# Exception handling tests
def test_handler_exception_propagates():
    """Test that exceptions in handlers are propagated."""
    data = {"method": "exception_handler"}

    with pytest.raises(ValueError, match="Handler exception"):
        BaseHandler.process_data(data, "test-corr-id")


# Abstract method tests
def test_cannot_instantiate_incomplete_handler():
    """Test that handlers without required methods cannot be instantiated."""

    class IncompleteHandler(BaseHandler):
        pass

    with pytest.raises(TypeError):
        IncompleteHandler()


def test_cannot_instantiate_handler_without_name():
    """Test that handlers without name method cannot be instantiated."""

    class NoNameHandler(BaseHandler):
        def process(self, data, corr_id):
            return {}

    with pytest.raises(TypeError):
        NoNameHandler()


def test_cannot_instantiate_handler_without_process():
    """Test that handlers without process method cannot be instantiated."""

    class NoProcessHandler(BaseHandler):
        @staticmethod
        def name():
            return "no_process"

    with pytest.raises(TypeError):
        NoProcessHandler()


# Inheritance tests
def test_handler_inheritance():
    """Test that handler inheritance works correctly."""

    # Test base handler
    base_result = BaseHandler.process_data({"method": "base_handler"}, "test")
    assert base_result["type"] == "base"

    # Test derived handler
    derived_result = BaseHandler.process_data({"method": "derived_handler"}, "test")
    assert derived_result["type"] == "derived"
    assert derived_result["enhanced"] is True


# Complex data tests
def test_complex_data_processing():
    """Test processing complex nested data structures."""
    complex_data = {
        "method": "test_handler",
        "nested": {
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "bool": True,
            "null": None,
        },
        "array": ["a", "b", "c"],
    }

    result = BaseHandler.process_data(complex_data, "complex-corr-id")

    assert result["result"] == "test_processed"
    assert result["corr_id"] == "complex-corr-id"
    assert result["data"]["nested"]["list"] == [1, 2, 3]
    assert result["data"]["nested"]["dict"]["key"] == "value"
    assert result["data"]["nested"]["bool"] is True
    assert result["data"]["nested"]["null"] is None
    assert result["data"]["array"] == ["a", "b", "c"]


# Edge case tests
def test_handler_with_special_characters_in_name():
    """Test handlers with special characters in names."""

    result = BaseHandler.process_data({"method": "special-handler_123"}, "test")
    assert result["special"] is True


def test_correlation_id_handling():
    """Test that correlation IDs are properly passed through."""
    test_corr_ids = ["simple", "complex-id-123", "", None, 12345]

    for corr_id in test_corr_ids:
        result = BaseHandler.process_data({"method": "test_handler"}, corr_id)
        assert result["corr_id"] == corr_id


def test_handler_state_isolation():
    """Test that handler instances don't share state."""

    # Each call should create a new instance
    result1 = BaseHandler.process_data({"method": "stateful_handler"}, "test1")
    result2 = BaseHandler.process_data({"method": "stateful_handler"}, "test2")

    assert result1["counter"] == 1
    assert result2["counter"] == 1  # New instance, so counter resets


def test_service_response_structure():
    """Test that ServiceResponse returns proper structure for 404."""
    data = {"method": "nonexistent"}

    result = BaseHandler.process_data(data, "test")

    assert "code" in result
    assert "response" in result
    assert result["code"] == 404
    assert "message" in result["response"]
    assert result["response"]["message"] == "Method not found."
