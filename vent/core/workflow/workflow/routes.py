def routes():
    from .paths import DataR
    p = paths()
    data_r = DataR()
    funcs = [data_r]
    return dict(list(zip(p, funcs)))

def paths():
    return ['/data.json']
