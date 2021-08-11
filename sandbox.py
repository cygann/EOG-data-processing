import os

import numpy as np
import scipy.io as sio

import utils as util

DATA_DIR = "mat_files"

nev_path = os.path.join(DATA_DIR, "OE_recording_Blackrock013_NEV.mat")
nsx_path = os.path.join(DATA_DIR, "OE_recording_Blackrock013_NS6.mat")

nev = sio.loadmat(nev_path)
nsx = sio.loadmat(nsx_path)
