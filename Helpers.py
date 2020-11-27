


def map(func, iterator):
    if len(iterator) == 0:
        return []
    return [func(iterator[0])] + map(func, iterator[1:])