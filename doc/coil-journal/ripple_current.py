

def compute_L(vin, vout, f, Ipp):
    L = vout / (f * Ipp) * (1 - vout / vin)
    return L


