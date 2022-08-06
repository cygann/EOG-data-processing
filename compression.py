"""
Script for compression experiment.
"""
from functools import partial
from multiprocessing import cpu_count
from pathlib import Path
import gzip
import pdb
from typing import Any, Optional, Dict

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from tqdm.contrib.concurrent import process_map


def get_compression_ratios_for_array(
    data,
    window_size: int = 20000,
    inc: int = 9000,
    method: str = "gzip"
) -> npt.NDArray:
    """
    Computes a time-series of compression ratios for the provided data array

    Example:
        For an array of lenth (N x 1) and window_size=w, inc=i, we compress
        each set of w samples that are spaced i samples apart and find
        compression ratios for them.

                0 1 2 3 4 5 6 7 8 9
        data = [][][][][][][][][][][][][][][][][][][][][][][]
              {    _     }
                   |  {    _     }
                   |       |  {    _     }    ...
                   V       |       |
                  .32      V       |
                          .37      V
                                  .43

        The output would be:
            [[.32, w],
             [.37, w + i],
             [.43, w + 2 * i],
             ...]

    Args:
        data: A (N x M x ...) Numpy array of data to compress. Compression
            windows are performed along the first dimension.
        window_size: Size of window over which to compression and compute a
            compression ratio for.
        window_inc: By how many samples to increment the start of a subequent
            compression window.

    Returns:
        A (N // inc x 2) numpy array where the first column contains compression
        ratios that correspond to the sample indexes in the second column.
        For an input array N, a result array R, and w as the width of the
        compression window, then the compression ratio at R[n, 0] is the
        "compressibility" of the w samples preceeding the sample at
        N[R[n, 1], ::]. The second column of the result array then represents
        indexes into the original array.
    """

    num_slices = data.shape[0] // inc

    result = np.zeros((num_slices, 2))
    # Second column will contain the sample "timestamps" that each compression
    # ratio in the first column corresponds to.
    result[:,1] = (np.arange(num_slices) * inc) + window_size

    # Prepare data slices for compression.
    data = data.astype('float32')
    slices = []
    for i in range(num_slices):
        data_slice = data[i * inc:i * inc + window_size]
        slices.append(data_slice)

    # Compress all the data slices and derive compression ratios for them.
    func = partial(get_compression_ratio_for_slice, method)
    compression_ratios = process_map(func, slices, max_workers=cpu_count())
    result[:,0] = np.asarray(compression_ratios)

    return result


def get_compression_ratio_for_slice(
    method: str,
    data_slice: npt.NDArray[np.float32]
) -> float:
    """

    Computes the compression ratio for the provided slice:
        compression ratio = compressed size / raw size

    Args:
        method: Which compression method to use.
        data_slice: numpy array of data to use.

    Returns:
        The compression ratio for the data slice.
    """
    data_bytes = data_slice.tobytes()

    # Compress
    if method == "gzip":
        data_bytes_compressed = gzip.compress(data_bytes)
    else:
        raise ValueError("Unsupported compression method.")

    # Get raw size, ratio size
    size_raw = len(data_bytes)
    size_gz = len(data_bytes_compressed)
    ratio = size_gz / size_raw

    return ratio


def plot_compression_ratios(
    compression_ratios,
    compression_sample_idxs,
    show=True,
    fig=None,
    line_name: Optional[str] = None,
    sample_rate: int = 1,
    events: Optional[Dict[str, Any]] = None
):
    """
    Args:
        compression_ratios: N x 1 array of compression ratios
        compression_sample_idxs: N x 1 array containing the sample indexes that
            correspond to the compression ratios.
        show: Whether to display the plot at the end of this function.
        fig: Previous plotly figure that this plot result can be appended to.
        line_name: Name for the line drawn by the provided compression ratios.
        sample_rate: Sample rate of the provided data (samples per second).
        events: An optional dictionary of events to mark on the plot. This
            should be a dicionary where each key is the name of an event, and
            it maps to another dictionary containing the 'start' and 'end'
            keys, where 'start' and 'end' are integer sample indexes.

    Returns:
        A plotly graph object.
    """

    # Convert the sample indexes to seconds for the provided sample rate.
    np_tstamps = np.asarray(compression_sample_idxs) / sample_rate
    n = compression_ratios.shape[0]

    if fig is None:
        fig = go.Figure()

    if line_name is None:
        line_name = 'Compression ratio (gz size / raw size)'

    fig.add_trace(
        go.Scatter(
            x=np_tstamps, y=compression_ratios,
            name=line_name, mode='markers'
        )
    )

    fig.update_layout(
        title='Compressibility over Recording',
        yaxis_title='Compressibility Ratio (gz size / raw size)',
        xaxis_title='Recording duration in seconds (' + \
            str(sample_rate) + ' samples/s)'
    )

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

            color = 'rgba(20, 200, 250, .2)'

            fig.add_trace(
                go.Scatter(
                    x=xvals,
                    y=yvals,
                    name=event,
                    fill='toself',
                    mode='markers',
                    marker_color=color,
                    fillcolor=color
                )
            )

    if show: fig.show()
    return fig
