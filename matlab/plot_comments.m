function plot_comments(comments, c_start_s, is_end)
    tag = '-';
    if is_end
        tag = '--r';
    end
    n_comments = length(c_start_s);
    for c = 1:n_comments
        xline(c_start_s(c), tag, {comments(c, :)});
    end
end