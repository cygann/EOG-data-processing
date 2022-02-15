
xcorr_coeffs = zeros(12);

for x1 = 1:12
    for x2 = 1:12
        coef = corrcoef(NS6.Data(x1,c_start(1):c_end(1)), NS6.Data(x2,c_start(1):c_end(1)));
        disp(coef);
        xcorr_coeffs(x1, x2) = coef(1, 2);
    end
end 