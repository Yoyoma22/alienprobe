"""
Tests for the different logging capabilities.
"""
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

