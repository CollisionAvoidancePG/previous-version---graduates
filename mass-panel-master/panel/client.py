from common.units import toDD


def badge_color(value, danger, warning):
    if (value <= danger):
        return 'badge-danger'
    elif (value <= warning):
        return 'badge-warning'
    else:
        return 'badge-success'


def toDDstr(point):
    if point is None:
        return None
    dd = toDD(*point)
    return f"{dd[0]:.5f} {dd[1]:.5f}"


CLIENT_FUNCTIONS = {
    'badge_color': badge_color,
    'toDD': toDDstr
}
