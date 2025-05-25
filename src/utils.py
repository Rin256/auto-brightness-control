def round_up(x, base):
    return (x + base - 1) // base * base

def round_down(x, base):
    return x // base * base

def constrain(x, a, b):
        return max(a, min(x, b))