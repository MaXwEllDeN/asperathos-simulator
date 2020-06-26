% y: Job Process
% u: Replicas
% Ts: Sampling Time
function [y, t, u, Ts] = loadExperimentData(file_name)
	data = load(file_name);
	y = data(:, 2);
	t = data(:, 1);
	u = data(:, 3);

	aux_t = t;

	for i = 2:length(t)
		aux_t(i) = t(i) - t(i - 1);
	end

	Ts = round(mode(aux_t));
end
