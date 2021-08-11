function plot_data(data, keypoints1, keypoints2)
    figure
    plot(data);

    hold on
    keyp_y1 = size(keypoints1, 2);
    y1 = ones(keyp_y1);
    plot(keypoints1, y1, '--go');

    y2 = ones(keyp_y1);
    plot(keypoints2, y2, '--ro');
    hold off
end
