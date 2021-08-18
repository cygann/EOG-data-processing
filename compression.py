"""
Script for compression experiment. 
"""

import numpy as np
import utils as util
from pathlib import Path
import gzip

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

            data_bytes = data_slice.tobytes()
            data_bytes_compressed = gzip.compress(data_bytes)

            size_raw = len(data_bytes)
            size_gz = len(data_bytes_compressed)
    
            # Get file size (in bytes) without compression 
            # f = open('slice.txt', 'wb')
            # f.write(data_bytes)
            # f.close()
            # size_raw = Path('slice.txt').stat().st_size

            # Get file size (in bytes) with compression 
            # np.savetxt('slice.gz', data_slice)
            # f = open('slice.gz', 'wb')
            # f.write(data_bytes)
            # f.close()
            # size_gz = Path('slice.gz').stat().st_size

            ratio = size_gz / size_raw

            print('<' + rec_id + ': ' + cond + '>: raw size: ' + str(size_raw) + \
                    ' compressed size: ' + str(size_gz) + ' ratio: ' + \
                    str(ratio))

            compression_results[rec_id + ": " + cond] = {'raw': size_raw,
                    'comp': size_gz}

    return compression_results
