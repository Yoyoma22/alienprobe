import datetime
import traceback
from abc import ABC, abstractmethod

from alienprobe.log_levels import LogLevel
from alienprobe.message import Message


class BaseDispatcher(ABC):
    """
    A base logger for all loggers, and provides the methods that you have to overload.
    """

    @abstractmethod
    def config_dispatcher(self, config: dict):
        """
        We pass in the section of the dispatcher from the toml config file.  This is used to configure the logger,
        and learn more about how to set itself up.  Like target ip addresses, etc.
        :param config: The configuration that we are using for this logger.
        """
        pass

    @abstractmethod
    def write_message(self, message_object: Message) -> bool:
        """
        Base method that writes a message to whatever resource you are writing messages to.  Like files, whatever.
        :param level: The log level that we are writing at.
        :param message_object: The log message values we need to write.  If you just want a standard render,
        just call the format_message call in the base class.
        :return: True if the message was written.
        """
        pass

    def format_message(self, message_object: Message, datetime_format: str, log_utc: bool,
                       message_format: str, exception_format: str):
        """
        Using the common tokens below, format the message according to the format runes.  Basically just does some
        string replaces on the message format of your choosing.
        [[INSTANCE_ID]] This is a unique number created once per process (if you use the global
        logger) or once per logger instance.  This is VERY useful when debugging clustered environments, as you can
        do a where clause in the downstream system and see the log of the exact node that did the processing, ignoring
        the rest.
        [[MACHINE_NAME]] The name of the machine that this logger is running on, we get that from the host name.  So it's
        never a bad idea to set the hostname of your docker image to something unique during the docker build or startup.
        [[DATE_STRING]]: The string date, formatted in the format passed into the message_format parameter.
        [[CLASS_NAME]]: The name of the class (or file) we are logging.
        [[LOG_MESSAGE_STATIC]]: The static part of the log, like 'Read input file'.  Things that never change go
        in here.  It is basically an "alert", so in your downstream system, you can group all the
        events by 'Read input file'.
        [[DATE_FORMAT]] The date string, in the format defined above.
        [[LOG_MESSAGE_STATIC]] The static part of the log, like 'Read input file'.  Things that never change go in here.
        It is basically an "alert", so in your downstream system, you can group all the events by 'Read input file'.
        [[LOG_PARAMS]] The framework takes a dictionary of log parameters to add.
        [[EXCEPTION_TEXT]].  For our example, we simply add the stack trace, and we break down a line as well.How
        we format the exception text (in the exception_format field).
        :param exception_format: The format of how we will output the exceptions.
        Default is 'exception="\n[[EXCEPTION_TEXT]]"'
        :param message_format: The format of how we want the log to output.  The default is something
        like -> 'date="[[DATE_STRING]]" level="[[LOG_LEVEL]]" message="[[LOG_MESSAGE_STATIC]]" [[LOG_PARAMS]]'
        :param message_object: The values for all the fields we want to output.
        :param exception_format: The format of how we want to output the exception should it exist.
        """

        msg = message_format

        ex: BaseException = message_object.ex
        if ex:
            msg += exception_format
            ex_text = ''
            for ex_str in traceback.format_exception(value=ex):
                ex_text += ex_str + '\n'

            msg = msg.replace('[[EXCEPTION_TEXT]]', ex_text )
        #message_format = 'class=[[CLASS_NAME]] date="[[DATE_STRING]]" level="[[LOG_LEVEL]]" message="[[LOG_MESSAGE_STATIC]]" [[LOG_PARAMS]]'

        cls_name = message_object.class_name
        if not isinstance(cls_name, str ):
            cls_name = str(type(cls_name))

        msg = msg.replace('[[CLASS_NAME]]', cls_name)

        #
        # Format Date according to the date format passed in as a parameter.
        #
        log_date = datetime.datetime.now()
        if log_utc:
            log_date = datetime.datetime.utcnow()

        if not datetime_format:
            raise ValueError("No Valid datetime_format configured in the configuration file.  Was None.")

        curtime_str = log_date.strftime(datetime_format)
        msg = msg.replace('[[DATE_STRING]]', curtime_str)
        msg = msg.replace('[[LOG_LEVEL]]', message_object.level.name)
        msg = msg.replace('[[LOG_MESSAGE_STATIC]]', message_object.message_static)
        msg = msg.replace('[[INSTANCE_ID]]', message_object.instance_id)
        msg = msg.replace('[[MACHINE_NAME]]', message_object.machine_name)

        if not message_object.params:
            message_object.params = {}

        params_msg = ''
        for param_key, param_val in message_object.params.items():
            params_msg += str(param_key) + '='

            if isinstance(param_val, datetime.datetime):
                date_str = param_val.strftime(message_format)
                param_val_str = f'"{str(date_str)}"'
            elif isinstance(param_val, int) or isinstance(param_val, float):
                param_val_str = str(param_val)
            elif isinstance(param_val, dict):
                import pprint
                param_val_str = f'"{pprint.pformat(param_val)}"'
            else:
                param_val_str = f'"{str(param_val)}"'
            params_msg += param_val_str + ' '

        msg = msg.replace('[[LOG_PARAMS]]', params_msg.strip())

        return msg
