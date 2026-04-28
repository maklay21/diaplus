import logging

logging_config = {
    'version': 1,
    'formatters': {
        'default_formatter': {
            'format': '%(asctime).19s [%(levelname)s] %(message)s'
        }
    },
    'handlers': {
        'main_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default_formatter',
            'filename': '/app/logs/app.log',
            'maxBytes': 1048576,
            'backupCount': 5
        }
    },
    'loggers': {
        'main_logger': {
            'level': 'INFO',
            'handlers': ['main_file_handler']
        }
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger('main_logger')