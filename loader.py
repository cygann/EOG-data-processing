import os
from tqdm import tqdm
import pickle
import pdb

import numpy as np
import scipy.io as sio

import utils as util

DATA_DIR = "blackrock_data/2021-10-11/mat_files"
COND_DIR = "blackrock_data/2021-10-11/conditions"
COMMENT_DIR = "blackrock_data/2021-10-11/comment_csv"

FILEBASE = "datafile"

DATA_OBJ_DIR = "data_obj/"


def save_recordings_object(recs, filename):
    """
    Saves the recordings object recs to the specified filename in the
    DATA_OBJ_DIR path.
    """
    outpath = os.path.join(DATA_OBJ_DIR, filename)
    pickle.dump(recs, open(outpath, 'wb'))
    print("Saved recordings object to file at", outpath)

def load_recordings_object(filename):
    """
    Loads the recordings object from the specified filename in the
    DATA_OBJ_DIR path, and returns it
    """
    path = os.path.join(DATA_OBJ_DIR, filename)
    recs = pickle.load(open(path, 'rb'))

    return recs

### Raw data extraction functions below ###

def load_recording(rec_id, create_csv_only=False):
    """
    Loads the raw data from blackrock NEV and NS6 files saved to .mat files. The
    x_NEV.mat and x_NS6.mat files are read to extract the raw recording data and
    the event conditions.
    The event conditions are processed into a dictionary where event key
    strings, such as "scent 20" map to another dictionary with 'start' and 'end'
    keys, which each map to the raw data timestamp associated with it.

    Returns raw data numpy array and dict of event conditions.
    """

    NEV_FILENAME = FILEBASE + rec_id + "_NEV.mat"
    NSX_FILENAME = FILEBASE + rec_id + "_NS6.mat"

    # Read NEV, NSX
    nev_path = os.path.join(DATA_DIR, NEV_FILENAME)
    nsx_path = os.path.join(DATA_DIR, NSX_FILENAME)
    nev = sio.loadmat(nev_path)
    nsx = sio.loadmat(nsx_path)
    data = util.get_data(nsx) # make data available

    # Read Comments from csv
    comment_filename = FILEBASE + NEV_FILENAME[-11:-8] + "_comments.csv"
    comment_path = os.path.join(COMMENT_DIR, comment_filename)

    if not os.path.exists(COMMENT_DIR):
        os.makedirs(COMMENT_DIR)

    if create_csv_only:
        comments = util.get_comments(nev)
        util.save_comments_to_csv(comments, comment_path)
        return None, None

    comments = util.load_comments_from_csv(comment_path)

    cond_file = rec_id + ".pkl"
    cond = util.load_conditions_from_file(cond_file)

    # If there is no conditions file saved, then auto generate the conditions 
    # from the comments
    if cond is None:
        # pdb.set_trace()
        cond = util.find_condition_endpoints(comments)

    return data, cond

# REC_IDS = ['001', '003', '006', '007', '009', '011', '012', '013']
REC_IDS = ['001', '002', '003', '004', '005', '006']

def load_all_recordings(create_csv_only=False):
    """
    Reads all recordings (raw data and conditions dictionary) and returns it as
    a dictionary structure with the recording ids as keys.
    """
    print('Loading all recordings...')
    recordings = {}
    for rec_id in tqdm(REC_IDS):
        data, cond = load_recording(rec_id, create_csv_only)
        if create_csv_only: continue
        recordings[rec_id] = {'data': data, 'cond': cond}

    return recordings
