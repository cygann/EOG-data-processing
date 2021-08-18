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

    min_length = get_min_length(recs, keys)

    for rec_id in keys:
        for cond in keys[rec_id]:
            data_slice = get_condition_slice(recs[rec_id]['cond'], cond,
                                                recs[rec_id]['data']) 
    
    # Get file size (in bytes) without compression 
    np.savetxt('slice.npy', data_slice)
    size = Path('slice.npy').stat().st_size

    # Get file size (in bytes) with compression 
    np.savetxt('slice.gz', data_slice)
    size = Path('slice.gz').stat().st_size


