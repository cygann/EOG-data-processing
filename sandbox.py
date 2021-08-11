import os

import numpy as np
import scipy.io as sio

import utils as util

DATA_DIR = "mat_files"
NEV_FILENAME = "OE_recording_Blackrock013_NEV.mat"
NSX_FILENAME = "OE_recording_Blackrock013_NS6.mat"
nev_path = os.path.join(DATA_DIR, NEV_FILENAME)
nsx_path = os.path.join(DATA_DIR, NSX_FILENAME)

nev = sio.loadmat(nev_path)
nsx = sio.loadmat(nsx_path)

comments = util.get_comments(nev)
data = util.get_data(nsx)

comment_path = "OE_recording_Blackrock" + NEV_FILENAME[-11:-8] + "_comments.csv"
util.save_comments_to_csv(comments, comment_path)
