import glob
import os

import numpy as np
import scipy.io as sio
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd

BLACKROCK_DATA_DIR = 'blackrock_data'

def get_comments(nev):
    """
    Returns a dictionary containing three abributes that define the comments 
    from an nev .mat object:
        - 'text': (N, ) array containing the raw text of the comments
        - 'start': (N, ) array containing the start times of the comments
        - 'end': (N, ) array containing the end times of the comments
    """
    comments = {}
    comments['text'] = nev['NEV']['Data'][0][0]['Comments'][0][0]['Text'][0][0]
    comments['start'] = \
        nev['NEV']['Data'][0][0]['Comments'][0][0]['TimeStampStarted'][0][0][0]
    comments['end'] = \
        nev['NEV']['Data'][0][0]['Comments'][0][0]['TimeStamp'][0][0][0]

    return comments

def get_data(nsx, mode='NS6'):
    """
    Extracts the raw EOG data from the NSx object. 
    Returns a (N, ) array of data.
    """
    data = nsx[mode]['Data'][0][0][0]
    return data

def plot_data(data, comments):
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=np.arange(data.shape[1]), y=data,
                    # mode='lines'))
    # fig.show()

    plt.plot(np.arange(data.shape[0]), data, label="EOG Data")

def save_comments_to_csv(comments, pathname):
    df = pd.DataFrame(comments)
    df.to_csv(pathname, index=False)

def process_all_nev_to_csv(data_dir='blackrock_data/mat_files'):
    files = glob.glob(data_dir + '/*NEV.mat', recursive=True)

    for f in files:
        num = f[-11:-8]
        nev = sio.loadmat(f)
        comments = get_comments(nev)

        comment_path = "OE_recording_Blackrock" + num + "_comments.csv"
        save_comments_to_csv(comments, comment_path)

def load_comments_from_csv(filename, path='blackrock_data/comment_csv/'):

    fullpath = os.path.join(path, filename)
    df = pd.read_csv(fullpath)
    comments = df.to_dict()

    return comments

def find_condition_endpoints(comments):

    conditions = {}
    prev_key = ''
    for i in comments['text']:
        text = comments['text'][i]
        start = comments['start'][i]
        end = comments['end'][i]
        text_l = text.lower()

        if '!eb' in prev_key:
            conditions[prev_key]['end'] = start

        # This indicates the start of a new scent condition
        if 'scent' in text_l:
            # The end time for the scent comment indicates the time at which the
            # smell was presented
            conditions[text_l] = {}
            conditions[text_l]['start'] = end
            prev_key = text_l

        # This indicates the point in which the scent stimuli was removed
        elif 'removed' in text_l:
            # The start time for the 'Removed' comment indicates the time at
            # which the smell was removed.
            conditions[prev_key]['end'] = start

        elif '!sb' in text_l:
            conditions[text_l] = {}
            conditions[text_l]['start'] = end
            prev_key = text_l

        elif '!eb' in text_l:
            conditions[prev_key]['end'] = start

            conditions[text_l] = {}
            conditions[text_l]['start'] = end
            prev_key = text_l




    return conditions

def get_condition_slice(cond, key, data):
    slice_data = data[cond[key]['start']:cond[key]['end']]
    return slice_data

def get_slice(data, start, end):
    slice_data = data[start:end]
    return slice_data
