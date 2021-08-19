"""
Script for compression experiment. 
"""
from pathlib import Path
import gzip
import pdb

import numpy as np
import plotly.graph_objects as go

import utils as util

def compression_experiment(recs, keys):
    """
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

    # pdb.set_trace()

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
        
