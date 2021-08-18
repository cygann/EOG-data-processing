"""
Script for compression experiment. 
"""

import numpy as np
import utils as util
from pathlib import Path

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
    
            # Get file size (in bytes) without compression 
            np.savetxt('slice.npy', data_slice)
            size_raw = Path('slice.npy').stat().st_size

            # Get file size (in bytes) with compression 
            np.savetxt('slice.gz', data_slice)
            size_gz = Path('slice.gz').stat().st_size

            ratio = size_gz / size_raw

            print('<' + rec_id + ': ' + cond + '>: raw size: ' + str(size_raw) + \
                    ' compressed size: ' + str(size_gz) + ' ratio: ' + \
                    str(ratio))

            if rec_id not in compression_results:
                compression_results['rec_id'] = {}
