% y: Job Process
% u: Replicas
% Ts: Sampling Time
function [y, t, u, Ts] = loadExperimentData(experiment, step)
	dir = sprintf('data/%02d/csv_data/step%d.csv', experiment, step);
	data = load(dir);
	y = data(:, 3);
	t = data(:, 1);
	u = data(:, 4);

	aux_t = t;
	for i = 2:length(t)
		aux_t(i) = t(i) - t(i - 1);
	end
	Ts = mode(aux_t);
end
