import os
from tqdm import tqdm

import numpy as np
import scipy.io as sio

import utils as util

DATA_DIR = "blackrock_data/mat_files"
COND_DIR = "blackrock_data/conditions"

REC_IDS = ['001', '003', '006', '007', '009', '011', '012', '013']

def load_recording(rec_id):

    NEV_FILENAME = "OE_recording_Blackrock" + rec_id + "_NEV.mat"
    NSX_FILENAME = "OE_recording_Blackrock" + rec_id + "_NS6.mat"

    # Read NEV, NSX
    nev_path = os.path.join(DATA_DIR, NEV_FILENAME)
    nsx_path = os.path.join(DATA_DIR, NSX_FILENAME)
    nev = sio.loadmat(nev_path)
    nsx = sio.loadmat(nsx_path)
    data = util.get_data(nsx) # make data available

    # Read Comments from csv
    comment_path = "OE_recording_Blackrock" + NEV_FILENAME[-11:-8] + "_comments.csv"
    # comments = util.get_comments(nev)
    comments = util.load_comments_from_csv(comment_path)

    cond_file = rec_id + ".pkl"
    cond = util.load_conditions_from_file(cond_file)

    # If there is no conditions file saved, then auto generate the conditions 
    # from the comments
    if cond is None:
        cond = util.find_condition_endpoints(comments)

    return data, cond

def load_all_recordings():
    """
    Reads all recordings (raw data and conditions dictionary) and returns it as
    a dictionary structure with the recording ids as keys.
    """

    print('Loading all recordings...')
    recordings = {}
    for rec_id in tqdm(REC_IDS):
        data, cond = load_recording(rec_id)
        recordings[rec_id] = {'data': data, 'cond': cond}

    return recordings
