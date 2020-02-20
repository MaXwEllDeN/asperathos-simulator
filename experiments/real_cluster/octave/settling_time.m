function ts = settling_time(G)
	[y, t] = step(G);
	[~, i] = min(abs(1 - y));
	ts = t(i);
end
