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


def compress_recording(data, window_size=150000, sliding=True, inc=7000):
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
            timestamps.append(start + window_size)
            start += inc

    
    return comp_ratios, timestamps

def compress_recordings_list(recs, keys):

    results = {}

    for key in keys:
        data = recs[key]['data']
        cmp_ratios, ts = compress_recording(data)

        results[key] = {}
        results[key]['comp ratios'] = cmp_ratios
        results[key]['timestamps'] = ts

    return results

def plot_ratios_key(results, key, events=None, show=True, fig=None,
        line_name=None, sample_rate=30000):

    ratios = results[key]['comp ratios']
    tstamps = results[key]['timestamps']
    return plot_ratios(ratios, tstamps, events=events, show=show, fig=fig,
        line_name=line_name, sample_rate=sample_rate)

def plot_ratios(ratios, timestamps, events=None, show=True, fig=None,
        line_name=None, sample_rate=30000):

    np_ratios =  np.asarray(ratios)

    # Convert timestamps to seconds
    np_tstamps = np.asarray(timestamps) / sample_rate
    n = np_ratios.shape[0]


    if fig is None:
        fig = go.Figure()

    if line_name is None:
        line_name = 'Compression ratio (gz size / raw size)'

    fig.add_trace(go.Scatter(x=np_tstamps, y=np_ratios, 
        name=line_name,
        mode='markers'))

    fig.update_layout(title='Compressibility over EOG recording',
                        yaxis_title='Compressibility Ratio (gz size / raw size)',
                        xaxis_title='Recording duration in seconds (' + \
                            str(sample_rate) + ' samples/s')

    # Plot events as well
    if events is not None:
        min_y = np.min(np_ratios)
        max_y = np.max(np_ratios)

        for event in events:
            xvals = []

            xvals.append(events[event]['start'] / sample_rate)
            xvals.append(events[event]['end'] / sample_rate)
            xvals.append(events[event]['end'] / sample_rate)
            xvals.append(events[event]['start'] / sample_rate)

            yvals = np.ones(len(xvals)) * min_y
            yvals[0] = max_y
            yvals[1] = max_y

            color = None
            if 'sham' in event:
                color = 'rgba(60, 60, 60, .3)'
            else:
                color = 'rgba(20, 200, 250, .2)'

            fig.add_trace(go.Scatter(x=xvals, y=yvals, 
                name=event, fill='toself', mode='markers', marker_color=color,
                fillcolor=color))


    if show: fig.show()
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

def compression_pyramid(data):
    """
    Compression experiment of varied size window increments.
    """

    # inc_vals = [100, 1000, 4000, 7000, 10000, 15000, 20000, 25000]
    # window_vals = [2000, 5000, 10000, 15000, 20000, 30000, 60000, 90000, 120000]
    window_vals = [100000, 120000, 150000]
    results = []

    # for v in inc_vals:
    for w in window_vals:
        print("Compressing data with increment value " + str(w))
        comp_rat, timestamps = compress_recording(data, window_size=w,
                sliding=True, inc=7000)
        name = "Window size " + str(w)
        results.append((comp_rat, timestamps, name))

    return results

def plot_compression_pyramid(results, show=True, events=None,
        use_seconds=False):

    fig = go.Figure()

    for i, res in enumerate(results):
        comp_rats, tstmps, name = res
        if use_seconds: 
            tstmps = [t / 30000 for t in tstmps]
        plot_ratios(comp_rats, tstmps, show=False, fig=fig, 
                line_name=name)

    # Plot events as well
    if events is not None:
        min_y = np.min(results[0][0])

        for event in events:
            xvals = []

            xvals.append(events[event]['start'])
            xvals.append(events[event]['end'])

            if use_seconds: 
                xvals = [t / 30000 for t in xvals]

            fig.add_trace(go.Scatter(x=xvals, y=np.ones(len(xvals)) * min_y, 
                name=event))
    
    if show: fig.show()
    return fig
