import logging
from logging.config import dictConfig
from flask import Flask

def setup_logger(app: Flask):
    # Use Gunicorn's error logger handlers if running under Gunicorn
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    if gunicorn_error_logger.handlers:
        app.logger.handlers = gunicorn_error_logger.handlers
        app.logger.setLevel(gunicorn_error_logger.level)
    else:
        # Fallback logging config if not running under Gunicorn
        dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                },
            },
            'handlers': {
                'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default'
                },
            },
            'root': {
                'level': 'INFO',
                'handlers': ['wsgi']
            }
        })
        app.logger.setLevel(logging.INFO)