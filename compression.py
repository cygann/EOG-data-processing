"""
Script for compression experiment. 
"""
from pathlib import Path
import gzip
import pdb

import numpy as np
import plotly.graph_objects as go
from tqdm import tqdm

import utils as util


def compress_recording(data, window_size=90000, sliding=False, inc=4000):
    """
    Compresses the raw data from a single recording using a window_size window
    of samples to include in each compression batch. 
    Can operate with or without sliding window. For sliding window, the inc
    argument represents the window increment between subsequent compression
    batches.

    Returns a list of compression ratios and a list of sample # timestamps that
    correspond to the compression ratios. For example, for comp_ratios[i], this
    compression sample was started at sample number timestamps[i] and included
    inc samples of data.
    """

    comp_ratios = []
    timestamps = []

    num_slices = data.shape[0] // window_size

    if not sliding:
        for i in tqdm(range(num_slices)):

            # Snip data slice, convert to bytes
            data_slice = data[i * window_size: i * window_size + window_size]
            data_slice = data_slice.astype('float32')
            data_bytes = data_slice.tobytes()

            # Compress
            data_bytes_compressed = gzip.compress(data_bytes)

            # Get raw size, ratio size
            size_raw = len(data_bytes)
            size_gz = len(data_bytes_compressed)
            ratio = size_gz / size_raw

            comp_ratios.append(ratio)
            timestamps.append(i * window_size)
    else:
        start = 0
        num_slices = data.shape[0] // inc

        for i in tqdm(range(num_slices)):
            # Snip data slice, convert to bytes
            data_slice = data[start:start + window_size]
            data_slice = data_slice.astype('float32')
            data_bytes = data_slice.tobytes()

            # Compress
            data_bytes_compressed = gzip.compress(data_bytes)

            # Get raw size, ratio size
            size_raw = len(data_bytes)
            size_gz = len(data_bytes_compressed)
            ratio = size_gz / size_raw

            comp_ratios.append(ratio)
            timestamps.append(start)
            start += inc

    
    return comp_ratios, timestamps

def plot_ratios(ratios, timestamps, events=None):

    np_ratios = np.asarray(ratios)
    np_tstamps = np.asarray(timestamps)
    fig = go.Figure()
    n = np_ratios.shape[0]

    fig.add_trace(go.Scatter(x=np_tstamps, y=np_ratios, 
        name='Compression ratio (gz size / raw size)',
        mode='markers'))

    fig.update_layout(title='Compressibility over EOG recording',
                        yaxis_title='Compressibility ratio (gz size / raw size)',
                        xaxis_title='Recording sample window start')

    if events is not None:
        min_y = np.min(np_ratios)

        for event in events:
            xvals = []

            xvals.append(events[event]['start'])
            xvals.append(events[event]['end'])

            fig.add_trace(go.Scatter(x=xvals, y=np.ones(len(xvals)) * min_y, 
                name=event))


    fig.show()
    return fig

def compression_experiment(recs, keys):
    """
    Original compression test experiment.
    Compresses data slices corresponding to all specified keys 
    """

    compression_results = {}

    min_length = util.get_min_length(recs, keys)

    for rec_id in keys:
        for cond in keys[rec_id]:
            data_slice = util.get_condition_slice(recs[rec_id]['cond'], cond,
                    recs[rec_id]['data'])[:min_length]

            data_slice = data_slice.astype('float32')

            data_bytes = data_slice.tobytes()
            data_bytes_compressed = gzip.compress(data_bytes)

            size_raw = len(data_bytes)
            size_gz = len(data_bytes_compressed)

            ratio = size_gz / size_raw

            print('<' + rec_id + ': ' + cond + '>: raw size: ' + str(size_raw) + \
                    ' compressed size: ' + str(size_gz) + ' ratio: ' + \
                    str(ratio))

            compression_results[rec_id + ": " + cond] = {'raw': size_raw,
                    'comp': size_gz}

    return compression_results

def plot_compression_results(result):

    fig = go.Figure()
    conds = []
    ratios = []
    for item in result:
        ratio = result[item]['comp'] / result[item]['raw']
        ratios.append(ratio)
        conds.append(item)

    fig.add_trace(go.Scatter(x=ratios, y=conds, 
        name='Compression ratio (gz size / raw size)',
        mode='markers'))

    fig.update_layout(title='Compressibility by recording condition',
                        xaxis_title='Compressibility ratio (gz size / raw size)',
                        yaxis_title='Recording condition')
    fig.show()
