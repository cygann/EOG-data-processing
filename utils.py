import numpy as np
import scipy.io as sio

def get_comments(nev):
    """
    Returns a dictionary containing three abributes that define the comments 
    from an nev .mat object:
        - 'text': (N, ) array containing the raw text of the comments
        - 'start': (1, N) array containing the start times of the comments
        - 'end': (1, N) array containing the end times of the comments
    """
    comments = {}
    comments['text'] = nev['NEV']['Data'][0][0]['Comments'][0][0]['Text'][0][0]
    comments['start'] = nev['NEV']['Data'][0][0]['Comments'][0][0]['TimeStampStarted'][0][0]
    comments['end'] = nev['NEV']['Data'][0][0]['Comments'][0][0]['TimeStamp'][0][0]

    return comments

def get_data(nsx, mode='NS6'):
    """
    Extracts the raw EOG data from the NSx object. 
    Returns a (1, N) array of data.
    """
    data = nsx[mode]['Data'][0][0]
    return data
