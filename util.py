import numpy as np
import scipy.io as sio

def get_comments(nev):
    """
    Returns array containing comments from an nev .mat object.
    """
    return nev['NEV']['Data'][0][0]['Comments'][0][0]['Text'][0][0]
