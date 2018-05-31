def routes():
    from .paths import CreateR, DeleteR, InfoR, NICsR, ListR, StartR, StopR, UpdateR
    p = paths()
    create_r = CreateR()
    delete_r = DeleteR()
    info_r = InfoR()
    nics_r = NICsR()
    list_r = ListR()
    start_r = StartR()
    stop_r = StopR()
    update_r = UpdateR()
    funcs = [create_r,
             delete_r,
             info_r,
             list_r,
             nics_r,
             start_r,
             stop_r,
             update_r]
    return dict(list(zip(p, funcs)))

def paths():
    return ['/create',
            '/delete',
            '/info',
            '/list',
            '/nics',
            '/start',
            '/stop',
            '/update']
