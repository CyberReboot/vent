import logging

logger = logging.getLogger(__name__)


def ErrorHandler(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:  # pragma: no cover
            # log the exception
            logger.exception('Exception in {0}: {1}'.format(
                function.__name__, str(e)))
    return wrapper
