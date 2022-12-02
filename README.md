# alienprobe
A logging library which allows for rapid logging development, debugging and analysis by downstream log analysis systems.

This library favours readability and auditability of the logs over processing speeds.  This is when you need to know exactly what is going on in your scripts, and possibly broadcast the logs to other loggers, databse tables, message queues, etc.

Configuration is done with environment variables, so that it can easily be passed 