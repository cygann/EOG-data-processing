# EOG-data-processing

## Dependencies

## Blackrock data object extraction with MATLAB
Blackrock has a library called [NPMK](https://github.com/BlackrockMicrosystems/NPMK) that contains dataloaders for their custom data structures of NEV and NSx files. The script `preproc.m` contains a script that will read one set of NEV and NSx files and save them as `.mat` such that they can be used for further MATLAB or Python processing. 

To perform this step, make sure to clone the [NPMK repository](https://github.com/BlackrockMicrosystems/NPMK) and add it to your MATLAB path. Now run the `preproc.m` script for every set of `.nev` and `.nsx` files that you have. For further instructions on using NPMK, check out [Blackrock's NPMK tutorial video](https://www.youtube.com/watch?v=amPdC7mW68I).
