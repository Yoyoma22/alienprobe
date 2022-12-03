"""
Just an object that wraps a message being printed.  We do this so its easier for the dispatchers
to process the messages.
"""
from typing import Union

from alienprobe.log_levels import LogLevel


class Message:
    """
    A class which contains an essential message to log.
    """
    level: LogLevel
    class_name: Union[str, object]
    message_static: str = None
    params: dict = {}
    ex: BaseException = None

    def __str__(self):
        """
        String representation for debugging.
        :return: Whats going on here.
        """
        return f"{self.level} - {self.class_name} - {self.message_static}"