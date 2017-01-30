def ErrorHandler(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e: # pragma: no cover
            print(e)
    return wrapper
