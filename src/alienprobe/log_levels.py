"""
A file that shows the different log levels, and a class that acts as a helper for these.
We set many log levels according to what level we want to log at.  We use levels to attempt to control
the number of logs being outputted to the downstream system for performance reasons.
"""
from typing import Optional


class LogLevel:
    """
    A wrapper that logs a single log level and the level id.  Used in the LogLevels structure.
    """
    name: str
    level_id: int

    def __init__(self, name: str, level_id: int):
        """
        Default constructor for the LogLevel.
        :param name: The name of the log level, like 'warn'.
        :param level_id: An integer id for the log level, ex: 5
        """
        self.name = name
        self.level_id = level_id

    def __eq__(self, other):
        """
        Overloaded equals operator, so you can do things like "if cur_level == LogLevel.WARN"
        :param other: The other object that we are comparing against.
        :return: True if it is, False if it aint.
        """
        if not isinstance(other, LogLevel):
            # don't attempt to compare against unrelated types
            return ValueError("You can only compare LogLevel objects against other LogLevel objects.")

        return self.level_id == other.level_id

    def __str__(self):
        """
        String representation of the Log Level.
        :return: Basically the name and the id.  For example, "warn(5)"
        """
        return f"{self.name}({self.level_id})"


class LogLevels:
    """
    A collection of log levels.
    This class contains all the log levels that is supported by alien logger.
    For each message you write, make the messages concise.
    Always think of the following whenever creating a log message.  The developer who is tracing, and the downstream
    system which is processing the error (in logs, audits, graphs, etc).

    Dev note: It's just easier doing it this way than dealing with the odd Enum type in python.
    """
    """
    The trace level indicates a level where a person would wish to exhaustively trace the execution path of a 
    process.  For example, if we are trying to debug a small part of the system, logging every operation, then
    we can use the 'trace' level.  NOTE: This level does affect performance.  Use sparingly.
    """
    TRACE = LogLevel('trace', 0)

    """
    The debug level is a bit less than the "trace" level.  We usually use these for information that developers 
    need to know whilst debugging, but not to the level of TRACE.  For example, "Input file read", {"bytes": bytes_read}
    NOTE:  Putting too many debug statements can slow down your code. 
    """
    DEBUG = LogLevel('debug', 1)

    """
    This must be the most common of the levels.  We uses the Info levels when we want to let the readers know that
    something occurred in the system.  Its not an error, but it is usually an event.  
    An example could be "Processed Uploaded File", {"client": client_name, "elapsed_time": elapsed_time}"
    """
    INFO = LogLevel('info', 2)

    """
    This level is a bit odd, in the sense that it's an INFO that you want to highlight, its more important than 
    a normal INFO log, but it's not a WARNING since it wasn't necessarily a recoverable error. 
    An example of this would be a notice like "Loaded a new item from the config file", {"item_name": item_name}
    """
    NOTICE = LogLevel('notice', 3)

    """
    The WARNING level (sometimes called WARN), signifies a recoverable error.  An error of something that happened,
    but the execution can continue.  An example of this could be "Cannot connect to URL! Retrying..."
    {"url": url_to_connect, "retries": retry_count}
    """
    WARNING = LogLevel('warning', 4)
    WARN = LogLevel('warning', 4)

    """
    The ERROR level signifies a non-recoverable error in execution.  This usually stops the execution from occurring, 
    and you need to know about it.  An example of this could be 
    "Cannot connect to URL, retry count exceeded!  Cannot continue", {"url": url_to_connect, "retries": retry_count}
    Consider passing an exception for this error level.
    """
    ERROR = LogLevel('error', 5)

    """
    The CRITICAL level indicates something that is more severe than an average error.  
    This can be akin to a "warning" that a fatal will occur if immediate action is not taken, of that something
    catastrophic has happened in the system. 
    An example could be:
    "Data Drive is almost full", {"drive_size": drive_size, "drive_used": drive_used, 
    "drive_used_pcnt": drive_used/drive_size}
    Consider passing an exception for this error level.
    """
    CRITICAL = LogLevel('critical', 6)

    """
    This is the level that you never want to see in production.  The FATAL level means the system has stopped, 
    crashed, and is no longer processing anything.  Your OutOfMemoryError, DiskToFullException, 
    UpSchitsCreekWithoutAPaddleException.  Basically, the system has stopped executing or has entered an 
    incoherent or corrupted state.  
    """
    FATAL = LogLevel('fatal', 7)

    """
    A map of integer values to log levels.
    """
    log_levels_by_id = {
        0: LogLevel('trace', 0),
        1: LogLevel('debug', 1),
        2: LogLevel('info', 2),
        3: LogLevel('notice', 3),
        4: LogLevel('warn', 4),
        5: LogLevel('error', 5),
        6: LogLevel('critical', 6),
        7: LogLevel('fatal', 7),
    }

    """
    A map of uppercase log levels like 'error'
    """
    log_levels_by_name = {
        'trace': LogLevel('trace', 0),
        'debug': LogLevel('debug', 1),
        'info': LogLevel('info', 2),
        'notice': LogLevel('notice', 3),
        'warning': LogLevel('warning', 4),
        'warn': LogLevel('warn', 4),
        'error': LogLevel('error', 5),
        'critical': LogLevel('critical', 6),
        'fatal': LogLevel('fatal', 7),
    }

    def get_level_by_name(self, str_name: str) -> Optional[LogLevel]:
        """
        Pass in a level name, like 'eRRor', or 'Error' and it will return the actual log level
        for that string.  If we can't find it, we return None.
        :param str_name: The level name that you are looking for.
        :return: The LogLevel instance, or None if not found.
        """
        if not str_name:
            return None

        str_name = str_name.strip().lower()
        for key_str in self.log_levels_by_name.keys():
            if str_name in key_str:
                return self.log_levels_by_name[str_name]

        return None

    def get_log_level_by_id(self, level_id: int) -> Optional[LogLevel]:
        """
        Gets a log level by its integer identifier.  Returns None if not found.
        :param level_id: The level int that you are looking for.
        :return: The LogLevel instance, or None if not found.
        """
        if not level_id:
            return None

        for cur_id in self.log_levels_by_id.keys():
            if cur_id == level_id:
                return self.log_levels_by_id[cur_id]

        return None
