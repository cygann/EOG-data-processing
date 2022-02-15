openNEV();
openNSx('uv');

c_start = NEV.Data.Comments.TimeStampStarted;
c_end = NEV.Data.Comments.TimeStamp;
comments = NEV.Data.Comments.Text;
n_comments = length(c_start);

n_samples = length(NS6.Data(1,:));
fs = double(NEV.MetaTags.SampleRes);

% Normalized to seconds
seconds = 1:n_samples;
seconds = seconds / fs;
c_start_s = c_start / fs;
c_end_s = c_end / fs;


