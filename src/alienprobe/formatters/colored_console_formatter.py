"""
A python logger which formats the output according to log level.
"""
import logging


class ColoredConsoleFormatter(logging.Formatter):
    """
    The color names from black to white ANSI colors
    """
    colour_codes = {
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

    color_mappings = {
        'DEBUG': colour_codes['light-green'],
        'WARNING': colour_codes['yellow'],
        'INFO': colour_codes['light-blue'],
        'CRITICAL': colour_codes['light-magenta'],
        'ERROR': colour_codes['red'],
    }

    """
    Logging formatter that also adds the color to console output.
    """
    def format(self, record):
        """
        Override of the formatter to add the color sequence to the record.
        """
        level = record.levelname.upper()
        msg = logging.Formatter.format(self, record)

        if level in self.color_mappings:
            msg = f"{self.color_mappings[level]}{msg}{self.colour_codes['reset']}"

        return msg
