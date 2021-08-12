import os

import numpy as np
import scipy.io as sio

import utils as util

DATA_DIR = "blackrock_data/mat_files"
NEV_FILENAME = "OE_recording_Blackrock013_NEV.mat"
NSX_FILENAME = "OE_recording_Blackrock013_NS6.mat"

# Read NEV, NSX
nev_path = os.path.join(DATA_DIR, NEV_FILENAME)
nsx_path = os.path.join(DATA_DIR, NSX_FILENAME)
nev = sio.loadmat(nev_path)
nsx = sio.loadmat(nsx_path)
data = util.get_data(nsx) # make data available

# Read Comments from csv
comment_path = "OE_recording_Blackrock" + NEV_FILENAME[-11:-8] + "_comments.csv"
comments = util.load_comments_from_csv(comment_path)

cond = util.find_condition_endpoints(comments)

