import glob
import os
import pickle
import pdb

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

def plot_data(data, label=None, xlabel='sample # (sample rate: 30kHz)',
        ylabel='uV', freq=None):
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=np.arange(data.shape[1]), y=data,
                    # mode='lines'))
    # fig.show()

    if freq is not None:
        x = freq
    else:
        x = np.arange(data.shape[0])

    plt.plot(x, data, label=label, alpha=0.75)
    plt.legend()

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

def plot_data_plotly(data, fig, label=None, xlabel='sample # (sample rate: 30kHz)',
        ylabel='uV', freq=None):

    if freq is not None:
        x = freq
    else:
        x = np.arange(data.shape[0])

    # fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=data,
                    mode='lines', name=label))
    fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
    # fig.show()

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

    return conditions

def save_conditions_to_file(cond, filename, outdir='blackrock_data/conditions'):
    outpath = os.path.join(outdir, filename)
    pickle.dump(cond, open(outpath, 'wb'))

def load_conditions_from_file(filename, cond_dir='blackrock_data/conditions'):
    outpath = os.path.join(cond_dir, filename)
    cond = pickle.load(open(outpath, 'rb'))
    return cond

def get_condition_slice(cond, key, data):
    slice_data = data[cond[key]['start']:cond[key]['end']]
    return slice_data

def get_slice(data, start, end):
    slice_data = data[start:end]
    return slice_data

def plot_fft(data_samples, labels=None, use_plotly=None):

    # Truncate everything to the size of the smallest sample
    size = data_samples[0].shape[0]
    for ds in data_samples:
        s = ds.shape[0]
        if s < size:
            size = s

    freq = np.fft.rfftfreq(size) * 30000
    for i, ds in enumerate(data_samples):
        fft = np.fft.rfft(ds[:size])
        fft = np.abs(fft)
        label = None if labels is None else labels[i]
        if use_plotly is not None:
            plot_data_plotly(fft, fig=use_plotly, label=label, freq=freq, xlabel='Frequency',
                ylabel='Power')
        else:
            plot_data(fft, label=label, freq=freq, xlabel='Frequency',
                ylabel='Power')

def plot_conditions_fft(cond, data, keys=None, use_plotly=None):
    """
    Plots the fft results for every condition specified in keys. 
    Inputs:
    - cond: dictionary of conditions
    - data: the raw data of the recording
    - keys: list of keys (conditions) that should be plotted. If none, then this
            plots all conditions in cond.
    """
    # pdb.set_trace()

    if keys is not None:
        key_set = keys
    else: 
        key_set = cond.keys()

    slices = [get_condition_slice(cond, key, data) for key in key_set]
    plot_fft(slices, key_set, use_plotly=use_plotly)

def plot_recording_conditions_fft(recordings, keys, use_plotly=None):
    """
    Plots the fft results for every condition specified in keys. 
    Inputs:
    - recordings: dictionary of all recordings
    - keys: dict of recordings that stores all the keys in a specific recording
            that should be plotted, as a list. 
    """
    # pdb.set_trace()

    slices = []
    key_set = []

    for rec_id in keys:
        for condition in keys[rec_id]:
            cond_slice = get_condition_slice(recordings[rec_id]['cond'], condition,
                                                recordings[rec_id]['data']) 
            slices.append(cond_slice)
            key_set.append(rec_id + ': ' + condition)


    plot_fft(slices, key_set, use_plotly=use_plotly)

def plot_raw_from_dict(recordings, keys, use_plotly=None):

    if use_plotly is not None:
        print('Plotting with plotly')

    for rec_id in keys:
        for condition in keys[rec_id]:
            label_txt = rec_id + ': ' + condition

            if use_plotly is not None:
                plot_data_plotly(get_condition_slice(recordings[rec_id]['cond'], condition,
                    recordings[rec_id]['data']), fig=use_plotly, label=label_txt)
            else:
                plot_data(get_condition_slice(recordings[rec_id]['cond'], condition,
                    recordings[rec_id]['data']), label=label_txt)

def plot_recording_raw(recs, rec, plotly_fig):

    conds = recs[rec]['cond']

    for c in conds:
        plot_data_plotly(get_condition_slice(recs[rec]['cond'], c,
            recs[rec]['data']), fig=plotly_fig, label=rec + ': ' + c)


def plotly_fft_and_raw(recs):
    # Plot fft
    fig = go.Figure()
    plot_recording_conditions_fft(recs, {'006': [c for c in
        recs['006']['cond']]}, fig)
    fig.show()

    # Plot raw
    fig = go.Figure()
    plot_recording_raw(recs, '006', fig)
    fig.show()

def get_min_length(recs, keys):
    """
    Get the minimum length of all the event conditions specified by the keys
    dictionary.
    Inputs:
    - recs: recordings dictionary
    - keys: dictionary of rec_ids -> list of desired conditions
    """

    slices = []

    min_len = -1
    for rec_id in keys:
        for condition in keys[rec_id]:
            cond_slice = get_condition_slice(recs[rec_id]['cond'], condition,
                                                recs[rec_id]['data']) 
            slices.append(cond_slice)
            slice_size = cond_slice.shape[0]
            print('<' + rec_id + ': ' + condition + '> has length ' + str(slice_size))

            if slice_size < min_len or min_len == -1:
                min_len = slice_size


    print('Min length of condition:', min_len)
    return min_len

def add_keys_to_dict(old_keys, new_keys):
    """
    Puts the new keys into the old keys dict
    """

    for rec_id in new_keys:
        if rec_id not in old_keys:
            old_keys[rec_id] = []

        for cond in new_keys[rec_id]:
            if cond in old_keys[rec_id]: pass
            else: old_keys[rec_id].append(cond)

def custom_condition_keys(recs):
    # base_keys = {'006': [c for c in recs['006']['cond']]}
    no_breathe = {'006': ['hold breath'], '007': ['hold breath'], '003': ['no breathing']}
    breathe = {'001': ['nose breathing'], '003': ['nose breathe'], '007': ['breathing', 'breathing 2'], '011': ['breathing']}

    new_keys = {}
    add_keys_to_dict(new_keys, no_breathe)
    add_keys_to_dict(new_keys, breathe)

    return new_keys


