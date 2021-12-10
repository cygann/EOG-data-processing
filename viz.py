import os

import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

SAMPLE_RATE = 30000 # samples / s

def spec_plot(Sxx, t, f, events=None):
    plt.pcolormesh(t, f, np.log(Sxx))

    if events is not None:
        for ev in events:
            plt.axvline(events[ev]['start'] / 30000, color='white', linewidth=0.5)

    plt.show()

def matplotlib_full_raw(recs, key, show=True, new_data=None):
    rec = recs[key]
    data = rec['data']
    events = rec['cond']
    n = data.shape[0]

    if new_data is not None:
        xticks = [x / SAMPLE_RATE for x in range(new_data.shape[0])]
        plt.plot(xticks, new_data, label='raw data')
    else:
        xticks = [x / SAMPLE_RATE for x in range(n)]
        plt.plot(xticks, data, label='raw data')

    for ev in events:
        start = events[ev]['start'] / SAMPLE_RATE
        end = events[ev]['end'] / SAMPLE_RATE

        plt.plot([start, end], [-500, -500], label=ev)

    plt.title('Raw data of recording ' + key)
    plt.ylabel('voltage (uV)')
    plt.xlabel('Time into recording (seconds)')
    # plt.legend()
    if show: plt.show()
    return 

def matplotlib_snippet(data, start_s, end_s, key=None):
    n = data.shape[0]

    xticks = [(x / SAMPLE_RATE) + (start_s * SAMPLE_RATE) for x in range(n)]
    plt.plot(xticks, data, label='raw data')

    plt.title('Raw data of recording ' + str(key))
    plt.ylabel('voltage (uV)')
    plt.xlabel('Time into recording (seconds)')
    # plt.legend()
    plt.show()

def plotly_raw_with_events(rec, start=None, end=None):
    """
    Plots the raw data with event conditions as line segments at the bottom.
    Accepts a single recording dictionary. For example, if recs has the keys
    '001', '002', '003', you would pass recs['001'] as the first argument to
    plot from recording 001. 

    Optionally, one can include a start and end sample index. This is highly
    recommended due to how slow plotly can be when plotting large amounts of
    data.
    """

    fig = go.Figure()

    # Prepare data
    data = rec['data']
    use_data = data
    x_ticks = np.arange(data.shape[0])
    if start is not None and end is not None:

        if start < 0:
            print("ERROR: start idx must be > 0.")
            return
        if end > data.shape[0]:
            print("ERROR: end idx must be less than size of raw data array. ")
            return

        use_data = data[start:end]
        x_ticks = x_ticks[start:end]

    fig.add_trace(go.Scatter(x=x_ticks, y=use_data, 
        name='Raw signal',
        mode='lines'))
    fig.update_layout(xaxis_title='sample # (sample rate: 30 kHz)',
            yaxis_title='uV')

    # Draw the event durations at the minumum y value
    min_y = np.min(use_data)

    events = rec['cond']
    for event in events:
        xvals = []
        start_val = events[event]['start']
        end_val = events[event]['end']

        # Only plot the event conditions nearby the window bounded by start and
        # end idx.
        if (start is None and end is None) or \
            (start_val >= start and end_val <= end) or \
            (start_val <= end and end_val >= start):
            xvals.append(start_val)
            xvals.append(end_val)

            fig.add_trace(go.Scatter(x=xvals, y=np.ones(len(xvals)) * min_y, 
                name=event))

    fig.show()
    return fig
