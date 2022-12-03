"""
A dispatcher that writes log messages to STDOUT.
"""
from alienprobe.dispatchers.base_dispatcher import BaseDispatcher
from alienprobe.log_levels import LogLevels, LogLevel
from alienprobe.message import Message


class ConsoleDispatcher(BaseDispatcher):
    """
    Logging formatter that also adds the color to console output.
    """

    """
    The color names from black to white ANSI colors
    """
    ascii_colour_codes = {
        'black':   '\033[0;30m',
        'red':     '\033[0;31m',
        'green':   '\033[0;32m',
        'yellow':   '\033[0;33m',
        'blue':    '\033[0;34m',
        'magenta': '\033[0;35m',
        'cyan':    '\033[0;36m',
        'light-gray':     '\033[0;37m',

        'light-red':     '\033[1;31m',
        'light-green':   '\033[1;32m',
        'light-yellow':  '\033[1;33m',
        'light-blue':    '\033[1;34m',
        'light-magenta': '\033[1;35m',
        'light-cyan':    '\033[1;36m',

        'reset': "\033[0m"
    }

    """
    The mapping of log levels to colour codes.
    """
    color_mappings = {
        LogLevels.TRACE: ascii_colour_codes['light-gray'],
        LogLevels.DEBUG: ascii_colour_codes['light-green'],
        LogLevels.INFO: ascii_colour_codes['light-blue'],
        LogLevels.WARNING: ascii_colour_codes['yellow'],
        LogLevels.NOTICE: ascii_colour_codes['light-cyan'],
        LogLevels.ERROR:  ascii_colour_codes['light-red'],
        LogLevels.CRITICAL: ascii_colour_codes['light-magenta'],
        LogLevels.FATAL: ascii_colour_codes['red'],
    }

    """
    When we are outputting to console, should we use ASCII colorization for warning, debug, etc. It is very convenient,
    especially whilst developer, to highlight different logging levels as differnt colors.
    """
    colorize_messages: bool

    """
    What is the date and time format we should use in the logging.  You can use the ISO format such as
    YYYY-MM-DDTHH_MM_SS or any other format you wish.  Different systems have different date formats.
    """
    datetime_format = 'YY%Y-%m-%d_%H:%M:%S.%f'

    """
    When we log, should we be using UTC time zone? Or do we take the local machine's time zone.
    After many bloody battles, and many deaths, I always logging in UTC, especially if you have an international
    user base.
    """
    log_utc_timezone = True

    """
    Here you can set the exact format of your message
    [[DATE_FORMAT]] The date string, in the format defined above.
    [[LOG_MESSAGE_STATIC]] The static part of the log, like 'Read input file'.  Things that never change go in here.
    It is basically an "alert", so in your downstream system, you can group all the events by 'Read input file'.
    [[LOG_PARAMS]] The framework takes a dictionary of log parameters to add.  This is where you add your variable
    details (not in LOG_MESSAGE_STATIC).  For our 'Read Input File', we can add {'path': file_path, 
    'client': client_name, 'file_size': file_size}
    With this, you can actually make a query (or graph!) in a downstream system of how many times a 
    client sent a file and sum up how much data is being processed from this client per day.
    """
    message_format = 'date="[[DATE_FORMAT]]" level="[[LOG_LEVEL]]" message="[[LOG_MESSAGE_STATIC]]" [[LOG_PARAMS]]'

    """
    If an exception was passed, we append this exception_format to the message_format, replacing the stack trace with
    [[EXCEPTION_TEXT]].  For our example, we simply add the stack trace, and we break down a line as well.    
    """
    exception_format = 'exception="\n[[EXCEPTION_TEXT]]"'

    def config_dispatcher(self, config: dict):
        """
        We pass in the section of the dispatcher from the toml config file.  This is used to configure the logger,
        and learn more about how to set itself up.  Like target ip addresses, etc.
        :param config: The configuration that we are using for this logger.
        """

        self.colorize_messages = bool(config.get('colorize_messages', 'true'))
        self.datetime_format = config.get('datetime_format', 'YY%Y-%m-%d_%H:%M:%S.%f')
        self.log_utc_timezone = bool(config.get('log_utc_timezone', 'true'))
        self.message_format = config.get('message_format',
                                         'machine_name="[[MACHINE_NAME]]"'
                                         'date="[[DATE_STRING]]" '
                                         'level="[[LOG_LEVEL]]" '
                                         'message="[[LOG_MESSAGE_STATIC]]" '
                                         '[[LOG_PARAMS]]'
                                         )
        self.exception_format = config.get('exception_format', 'exception="\n[[EXCEPTION_TEXT]]"')

    def write_message(self, message_object: Message) -> bool:
        """
        Base method that writes a message to whatever resource you are writing messages to.  Like files, whatever.
        :param level: The log level that we are writing at.
        :param message_object: The log message values we need to write.  If you just want a standard render,
        just call the format_message call in the base class.
        :return: True if the message was written.
        """
        message: str = super().format_message(message_object=message_object,
                                              datetime_format=self.datetime_format,
                                              log_utc=self.log_utc_timezone, message_format=self.message_format,
                                              exception_format=self.exception_format)
        level = message_object.level
        if level in self.color_mappings.keys():
            msg = f"{self.color_mappings[level]}{message}{self.ascii_colour_codes['reset']}"
            print(msg, flush=True)
        else:
            print(message, flush=True)

        return True
