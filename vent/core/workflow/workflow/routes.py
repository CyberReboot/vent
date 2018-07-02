def routes():
    from .paths import ConnectionR, DataR
    p = paths()
    data_r = DataR()
    connection_r = ConnectionR()
    funcs = [connection_r, data_r]
    return dict(list(zip(p, funcs)))


def paths():
    return ['/connection/{from_conn}/{to_conn}', '/data.json']
