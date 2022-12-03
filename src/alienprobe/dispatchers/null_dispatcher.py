"""
A log dispatcher that consumes logs and does nothing
"""
from alienprobe.dispatchers.base_dispatcher import BaseDispatcher
from alienprobe.message import Message


class NullDispatcher(BaseDispatcher):
    """
    A log dispatcher that consumes logs and does nothing
    """

    def config_dispatcher(self, config: dict):
        """
        We pass in the section of the dispatcher from the toml config file.  This is used to configure the logger,
        and learn more about how to set itself up.  Like target ip addresses, etc.
        :param config: The configuration that we are using for this logger.
        """
    pass

    def write_message(self, message_object: Message) -> bool:
        """
        Base method that writes a message to whatever resource you are writing messages to.  Like files, whatever.
        :param message_object: The log message values we need to write.  If you just want a standard render,
        just call the format_message call in the base class.
        :return: True if the message was written.
        """
        pass
