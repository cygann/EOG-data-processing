# EOG-data-processing


## Dependencies
`pip install -r requirements.txt`

## Usage
Each python file have different modules that can be used in an interactive python environment (jupyter notebook, ipython session, etc.). Simply import each module you wish to use as such:
```
import viz
import compression
import loader
... etc
```
## Data exploration
For data already extrated from MATLAB files and post-processed with event labels & timestamps, this can be loaded from file. Check the `data_obj/` directory for saved recording objects. To load such files, run:

```
import loader
recs = loader.load_recordings_object("aug02_recordings.pkl")
```

This function returns an dict object with raw data and event condition information from multiple recordings. Each recording was captured separately and have unique identifiers. The keys to `recs` are the recording names, which can be viewed easily with `recs.keys()`. To access a single recording's data:

```
single_rec = recs['006'] # This is a dictionary with two keys, 'data' and 'cond'
print(single_rec['data']) # Prints a numpy array of raw data
```
Now to view the marked event conditions, there is a `'cond'` key for each recording. This is another dictionary that contains the start and end points for the event conditions. For example, to view when scent 31 was active during recording 006, we can do the following:

```
rec_006 = recs['006']
print('Scent 31 started at ' + rec_006['cond']['scent 31']['start'])
print('Scent 31 ended at ' + rec_006['cond']['scent 31']['end'])
```
To get the raw data for only scent 31:
```
scent_31_event = rec_006['cond']['scent 31']
scent_31_raw = rec_006['data'][scent_31_event['start']:scent_31_event['end']]
```
There are some plotting functions to view data as well. In the `viz.py` module, `plotly_raw_with_events` will plot raw data with line segments of all event conditions. To plot only the raw data associated with scent 31 in recording 6:
```
import viz
rec_006 = recs['006']
viz.plotly_raw_with_events(rec_006, rec_006['cond']['scent 31']['start'], rec_006['cond']['scent 31']['end'])
```

## Blackrock data object extraction with MATLAB
Blackrock has a library called [NPMK](https://github.com/BlackrockMicrosystems/NPMK) that contains dataloaders for their custom data structures of NEV and NSx files. The script `preproc.m` contains a script that will read one set of NEV and NSx files and save them as `.mat` such that they can be used for further MATLAB or Python processing. 

To perform this step, make sure to clone the [NPMK repository](https://github.com/BlackrockMicrosystems/NPMK) and add it to your MATLAB path. Now run the `preproc.m` script for every set of `.nev` and `.nsx` files that you have. For further instructions on using NPMK, check out [Blackrock's NPMK tutorial video](https://www.youtube.com/watch?v=amPdC7mW68I).
