"""
Tests for the different logging capabilities.
"""
import datetime

from alienprobe.alien_logger import AlienLogger
from alienprobe.log_levels import LogLevels
from test_fixtures import test_context, TestContext


def test_logger_init(test_context: TestContext):
    """
    Tests the simple initialization of a logger.
    :param test_context: The test context, which stores things we want to keep from test to test.
    :return:
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    logger.debug(__name__, 'Initialized Logger', {'config_path': test_context.log_config_path})


def test_logging_levels(test_context: TestContext):
    """
    Tests by sending a message to every handler at every logging level.
    :param test_context: The context to use.
    :return:
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE
    logger.trace(__name__, 'Message at TRACE Level', {'config_path': test_context.log_config_path, "foo": "bar"})
    logger.debug(__name__, 'Message at DEBUG Level', {'config_path': test_context.log_config_path, "foo": "bar"})
    logger.info(__name__, 'Message at INFO Level', {'config_path': test_context.log_config_path, "foo": "bar"})
    logger.warn(__name__, 'Message at WARN Level', {'config_path': test_context.log_config_path, "foo": "bar"})
    logger.error(__name__, 'Message at ERROR Level', {'config_path': test_context.log_config_path, "foo": "bar"})
    logger.critical(__name__, 'Message at CRITICAL Level', {'config_path': test_context.log_config_path, "foo": "bar"})
    logger.fatal(__name__, 'Message at FATAL Level', {'config_path': test_context.log_config_path, "foo": "bar"})


def test_logging_datetime(test_context: TestContext):
    """
    In the "parameters", you can put in a date time and it will be automatically formatted
    by the dispatcher.  Make sure that works properly.
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE
    logger.trace(__name__, 'Ensure dates get outputted', {'current_date': datetime.datetime.now(), "foo": "bar"})


def test_logging_integer(test_context: TestContext):
    """
    In the "parameters", you can put in an integer and it will be automatically formatted
    by the dispatcher.  Make sure that works properly.
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE
    logger.trace(__name__, 'Ensure integers get outputted', {'my_age': 43, "foo": "bar"})

def test_logging_bool(test_context: TestContext):
    """
    In the "parameters", you can put in an boolean and it will be automatically formatted
    by the dispatcher.  Make sure that works properly.
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE
    logger.trace(__name__, 'Ensure bools get outputted', {'is_false': True, "foo": "bar"})

def test_logging_float(test_context: TestContext):
    """
    In the "parameters", you can put in a float and it will be automatically formatted
    by the dispatcher.  Make sure that works properly.
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE
    logger.trace(__name__, 'Ensure floats get outputted', {'pcnt_completed': 0.5521, "foo": "bar"})


def test_logging_dict(test_context: TestContext):
    """
    In the "parameters", you can put in a dict and it will be automatically formatted
    by the dispatcher.  Make sure that works properly.
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE
    logger.trace(__name__, 'Ensure dict get outputted', {'persons': {"name": "Andre", "age": 42}, "foo": "bar"})


def test_logging_object_str(test_context: TestContext):
    """
    In the "parameters", you can put in an object with a __str__ and it will be automatically formatted
    by the dispatcher.  Make sure that works properly.
    """
    logger = AlienLogger()
    assert logger, "Should have had a correct instantiation."
    print()
    logger.default_log_level = LogLevels.TRACE

    class TestPerson:
        age = 43
        name = "Andre"

        def __str__(self):
            return f"{type(self).__name__}(age={self.age}, name={self.name})"

    logger.trace(__name__, 'Ensure objects get outputted', {"person": TestPerson()})
