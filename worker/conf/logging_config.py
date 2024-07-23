import logging
import logging.config
import os

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%m/%d/%Y %I:%M:%S %p'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False  # Do not propagate to parent loggers (e.g., no console output)
        },
    }
}

def setup_logging(log_file):
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = {
        'class': 'logging.FileHandler',
        'filename': log_file,
        'formatter': 'standard',
        'level': 'DEBUG',
    }

    config = LOGGING_CONFIG.copy()
    config['handlers']['file'] = file_handler

    try:
        logging.config.dictConfig(config)
    except Exception as e:
        print(f"Failed to configure logging: {e}")
        raise
