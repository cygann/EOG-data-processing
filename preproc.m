% This script uses the openNEV and openNSx functions to load the EOG data into
% matlab, and then saves them as .mat files. These functions require the user 
% to select the file of interest, so this must be done for each recorded 
% session.
openNEV();
openNSx();

disp("Loaded NEV and NS6 files");

comment_start_ts = NEV.Data.Comments.TimeStampStarted;
comment_end_ts = NEV.Data.Comments.TimeStamp;
comments = NEV.Data.Comments.Text;

% Get Filenames
nev_fname = strcat(NEV.MetaTags.Filename, '_NEV');
nsx_fname = strcat(NS6.MetaTags.Filename, '_NS6');

% Save the corresponding .mat files for each of these structures.
save(strcat(nev_fname, '.mat'), 'NEV');
save(strcat(nsx_fname, '.mat'), 'NS6');

disp("Saved .mat files for the NEV and NS6 objects.");
