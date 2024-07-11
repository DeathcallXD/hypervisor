import logging.config

LOGGING_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "lib.jsonlogformatter.JsonLogFormatter",
            "fmt_dict": {
                "level": "levelname",
                "message": "message",
                "loggerName": "name",
                "processName": "processName",
                "processID": "process",
                "threadName": "threadName",
                "threadID": "thread",
                "timestamp": "asctime",
                "func": "funcName",
                "lineno": "lineno",
            },
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # root logger
        "root": {"handlers": ["consoleHandler"], "level": "INFO", "propagate": False},
        
        # 3rd party libraries loggers
        "botocore": {"handlers": ["consoleHandler", ], "level": "ERROR", "propagate": False},
        "lambdawarmer": {"handlers": ["consoleHandler"], "level": "ERROR", "propagate": False},

        # app loggers
        "src": {"handlers": ["consoleHandler"], "level": "DEBUG", "propagate": False}
    },
}


logging.config.dictConfig(LOGGING_CONF)


def set_logger(name):
    return logging.getLogger(name)