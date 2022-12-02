from abc import ABC, abstractmethod


class BaseDispatcher(ABC):
    """
    A base logger for all loggers, and provides the methods that you have to overload.
    """
    pass

    @abstractmethod
    def write_message(self, level, message):
        """
        Base method that writes a message to whatever resource you are writing messages to.  Like files, whatever.
        :param level:
        :param message:
        :return:
        """
        pass




class ConsoleLogger:
    """
    A logger that outputs the logs to console.  Colourizes the output for readability.
    """
    ...


