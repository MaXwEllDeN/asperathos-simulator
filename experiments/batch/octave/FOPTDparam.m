function [G0, G0L, T1] = FOPTDparam(h, y, L_init, DeltaT)
    N = size(y, 1);
    Theta = zeros(1, 3);
    R = zeros(size(Theta, 2));
    f = zeros(size(Theta, 2));
    for k = L_init:N
        Tau = DeltaT * k;
        Phi = [h * Tau; -h; -y(k)];
        R = R + Phi * Phi';
        A = sum(y(1:k)) * DeltaT;
        f = f  + Phi * A;
    end

    Theta = R\f;

    G0 = Theta(1);
    G0L = Theta(2);
    T1 = Theta(3);
end
