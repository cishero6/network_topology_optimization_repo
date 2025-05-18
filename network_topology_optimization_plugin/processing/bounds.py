def validate(lower, upper):
    if not (0 < lower < 1 < upper):
        raise ValueError('Bounds must satisfy 0 < lower < 1 < upper')
    return True