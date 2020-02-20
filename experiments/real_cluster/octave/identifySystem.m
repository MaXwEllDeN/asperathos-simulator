function [G, L, T] = identifySystem(h, y, DeltaT)
	[G, G0L, T] = FOPTDparam(h, y, DeltaT, DeltaT);
	L = G0L/G;
end
