"""
Holds some various dispatchers.  A dispatcher is a class that takes the log messages and sends it to a logging
system.  Logging systems can be stdio/stdout, files, TCP Sockets, Oracle Database, PostGres Databse,
Elastic, Splunk, Syslog, MongoDB...
Basically anywhere you want to hold the log messages in a structured way.
"""