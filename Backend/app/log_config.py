import logging
import os
import logging.config

# Create a directory for logs if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/app.log',
            'formatter': 'standard',
            'encoding': 'utf-8',  # Add this line to specify UTF-8 encoding
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# Configure logging with this config
logging.config.dictConfig(LOGGING_CONFIG)