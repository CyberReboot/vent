def ErrorHandler(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:  # pragma: no cover
            pass
    return wrapper
