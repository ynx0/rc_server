# MARK - Internal methods for speed generators (move to util class)


def __generate_smooth(ceil):
    return ((i * 10 ** exp) / 10000 for exp in range(2, 5) for i in range(1, ceil))


def __generate_smooth_stop(ceil):
    return reversed(list(__generate_smooth(ceil)))


def __generate_smooth_backwards(ceil):
    # its the same thing, but helps for code clarity
    return __generate_smooth_stop(ceil)
