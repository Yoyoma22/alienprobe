"""
A logging library which allows for rapid logging development, debugging and analysis by downstream log analysis systems.
"""
import datetime
import importlib
import random
import socket
import threading
import os
from pathlib import Path
from typing import Optional, Any, Union, List

import tomli

from alienprobe.dispatchers.base_dispatcher import BaseDispatcher
from alienprobe.log_levels import LogLevels, LogLevel
from alienprobe.message import Message


class AlienLogger:
    """
    A class that sets up a several loggers and log handlers for the broadcast of log messages.
    """

    """
    The dict of dispatcher names to dispatcher instances, which is used to send out messages.
     """
    dispatchers: dict = {}

    """
    The complete configuration for this logger, loaded from the TOML file.
    """
    logger_config: dict

    """
    The path that we loaded the config from.
    """
    logger_config_path: Path

    """
    A unique code for each instance of the logger.  We usually get it from the host name and 
    a unique alphanumeric code.
    """
    instance_id: str = "UNKNOWN"

    """
    The current hostname for this machine.
    """
    machine_name: str = "Unknown"

    """
    Default log level, either 'debug', 'info', 'notice', 'error', 'critical'.
    """
    default_log_level: LogLevel = LogLevels.DEBUG

    def __init__(self):
        """
        Initialize the logging engine.
        """
        self.instance_id = self._generate_instance_id()
        config_file_str = os.getenv('ALIENLOGGER__CONFIG_FILE_PATH')
        if not config_file_str:
            raise ValueError("Could not find the 'ALIENLOGGER__CONFIG_FILE_PATH' environment variable, which is the "
                             "path to the TOML config file.")
        self.machine_name = socket.gethostname()
        self.instance_id = self._generate_instance_id()

        self.load_config(config_path=config_file_str)



    """
    We need a mutex so that we don't have two loggers cobbling over themselves, especially when using stuff like syslog.
    """
    _output_mutex: threading.Lock = None

    def load_config(self, config_path: Union[Path, str]):
        """
        Loads this logger configuration from the given Path (or str).  Throws an exception if the
        path is not found.
        :param config_path: The path to the toml config file for this logger.
        """
        self.logger_config_path = Path(config_path)
        if not self.logger_config_path.exists():
            raise ValueError(f"Could not find Logger TOML config file in {self.logger_config_path}")

        #
        # We use 'rb' with no encoding, in case that other encodings are used for the config file.  Apparently,
        # tomli is able to handle this.  I hope its not just utf-8 or ascii.
        #
        with open(self.logger_config_path, "rb") as f:
            self.logger_config = tomli.load(f)

        self.default_log_level = LogLevels().get_level_by_name(self.logger_config.get('default_log_level', 'info'))

        self._init_dispatchers()

        self.info(self, "Logger Initialized", {
            "machine_name": self.machine_name,
            "start_time": datetime.datetime.now(),
            "utc_start_time": datetime.datetime.utcnow()
        })

    def _init_dispatchers(self):
        """
        Go through the list of dispatchers configured in the config file, and instantiate them all.
        This sets up the current array of dispatchers that is used to broadcast messages.
        """
        self.dispatchers = {}

        dispatchers = self.logger_config['common']['dispatchers']
        for dispatcher_name in dispatchers:
            if dispatcher_name not in self.logger_config.keys():
                raise ValueError(f"Could not find dispatcher {dispatcher_name} configuration "
                                 f"in config file {self.logger_config_path}")

            dispatcher_config = self.logger_config[dispatcher_name]
            #
            # For each logger that is configured, instantiate the logger.
            # You can write your own!
            #
            dispatcher_cls_name = dispatcher_config.get('dispatcher_class_name')
            if not dispatcher_cls_name:
                raise ValueError(f'Dispatcher {dispatcher_name} does not have a class name entry in config '
                                 f'(dispatcher_class_name)")')

            module_name, class_name = dispatcher_cls_name.rsplit(".", 1)
            MyDispatcher = getattr(importlib.import_module(module_name), class_name)
            dispatcher_instance = MyDispatcher()
            self.dispatchers[dispatcher_name] = dispatcher_instance
            dispatcher_instance: BaseDispatcher
            dispatcher_instance.config_dispatcher(config=dispatcher_config)

    def log_internal(self, log_level: LogLevel, log_source: Union[str, object], log_message_static: str,
                     log_params: dict = None, exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the given level.  We open this up in case you want to do some custom logging shennanigans.
        Ordinarily, you should not be using this method.
        :param log_level: The logging level that we are dispatching this message.
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        if log_params and not isinstance(log_params, dict):
            raise ValueError(f"Message log params for message '{log_message_static} in class "
                             f"{log_source} is not a dictionary!  Pass in a dictionary or None.")

        msg_obj = Message()
        msg_obj.level = log_level
        msg_obj.class_name = log_source
        msg_obj.message_static = log_message_static
        msg_obj.params = log_params
        msg_obj.ex = exception
        msg_obj.instance_id = self.instance_id
        msg_obj.machine_name = self.machine_name

        for disp in self.dispatchers.values():
            disp: BaseDispatcher
            disp.write_message(message_object=msg_obj)

    def _generate_instance_id(self) -> str:
        """
        Generates a unique instance id for each instantiation of the logger.
        @return A unique instance id which includes the logger start and date time.  That is useful for debugging
        multiple nodes in a cluster when you bring them online.
        """
        cur_date = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%SZ')
        instance_id = ''.join(random.choice('0123456789ABCDEF') for i in range(5))
        return cur_date + "_" + instance_id

    def trace(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
              exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.TRACE level. This is the lowest level and is used when performing excessively detailed
        tracing of an operation.  BE CAREFUL, this log level will affect performance.
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.TRACE, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def debug(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
              exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.DEBUG level. The debug level is a bit less than the "trace" level.
        We usually use these for information that developers need to know whilst debugging, but not to the level of
        TRACE.  For example, "Input file read", {"bytes": bytes_read}
        NOTE:  Putting too many debug statements can slow down your code.
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.DEBUG, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def info(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
             exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.INFO level.
        This must be the most common of the levels.  We uses the Info levels when we want to let the readers know that
        something occurred in the system.  Its not an error, but it is usually an event.
        An example could be "Processed Uploaded File", {"client": client_name, "elapsed_time": elapsed_time}"
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.INFO, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def notice(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
               exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.NOTICE level.
        This level is a bit odd, in the sense that it's an INFO that you want to highlight, its more important than
        a normal INFO log, but it's not a WARNING since it wasn't necessarily a recoverable error.
        An example of this would be a notice like "Loaded a new item from the config file", {"item_name": item_name}
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.NOTICE, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def warning(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
                exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.Warning level.
        The WARNING level (sometimes called WARN), signifies a recoverable error.  An error of something that happened,
        but the execution can continue.  An example of this could be "Cannot connect to URL! Retrying..."
        {"url": url_to_connect, "retries": retry_count}
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.WARNING, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def warn(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
                exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.Warning level.  This is a shortcut for logger.warning().
        The WARNING level (sometimes called WARN), signifies a recoverable error.  An error of something that happened,
        but the execution can continue.  An example of this could be "Cannot connect to URL! Retrying..."
        {"url": url_to_connect, "retries": retry_count}
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.WARNING, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def error(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
              exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.ERROR level.
        The ERROR level signifies a non-recoverable error in execution.  This usually stops the execution from occuring,
        you need to know about it.  An example of this could be
        "Cannot connect to URL, retry count exceeded!  Cannot continue", {"url": url_to_connect, "retries": retry_count}
        Note: Consider passing an exception for this error level.
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.ERROR, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def critical(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
              exception: Optional[BaseException] = None) -> None:
        """
        Logs something at the LogLevels.CRITICAL level.
        The CRITICAL level indicates something that is more severe than an average error.
        This can be akin to a "warning" that a fatal will occur if immediate action is not taken, of that something
        catastrophic has happened in the system.
        An example could be:
        "Data Drive is almost full", {"drive_size": drive_size, "drive_used": drive_used, "drive_used_pcnt": drive_used/drive_size}
        Consider passing an exception for this error level.
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.CRITICAL, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)

    def fatal(self, log_source: Union[str, object], log_message_static: str, log_params: dict = None,
              exception: Optional[BaseException] = None) -> None:
        """
        This is the level that you never want to see in production.  The FATAL level means the system has stopped,
        crashed, and is no longer processing anything.  Your OutOfMemoryError, DiskToFullException,
        UpSchitsCreekWithoutAPaddleException.  Basically, the system has stopped executing or has entered an
        incoherent or corrupted state.
        :param log_source: The source that called the operation.  Pass 'self' if you are in a class, or __name__ if you
        are in a python module.
        :param log_message_static:  The static part of the log, like 'Read input file'.  Things that never change
        go in here. It is basically an "alert", so in your downstream system, you can group all
        the events by 'Read input file'.
        :param log_params: The framework takes a dictionary of log parameters to add.  This is where you add your
        variable details (not in log_message_static!).
        For our 'Read Input File' example, we can add {'path': file_path, 'client': client_name, 'file_size': file_size}
        With this, you can actually make a query (or graph!) in a downstream system of how many times a
        client sent a file and sum up how much data is being processed from this client per day.  Default is empty
        if you are just outputting a message and don't have any variant details like "System Started".
        :param exception: The exception that we are logging.  Default is None, if not, the stack trace will be obtained
        and outputted as part of the message.
        :return: None
        """
        self.log_internal(log_level=LogLevels.FATAL, log_source=log_source, log_message_static=log_message_static,
                          log_params=log_params, exception=exception)


"""
Global logger so we only keep one instance in the process for speed and config reasons.
"""
_GLOBAL_LOGGER: Optional[AlienLogger] = None


def get_logger():
    """
    Factory Method for convenience method.  Gets a logger, and if one has not been instantiated we instantiate it here.
    :return: An instance of the alien logger which is global to the entire python process.
    :rtype: AlienLogger
    """
    global _GLOBAL_LOGGER
    if _GLOBAL_LOGGER:
        return _GLOBAL_LOGGER

    _GLOBAL_LOGGER = AlienLogger()
    return _GLOBAL_LOGGER
