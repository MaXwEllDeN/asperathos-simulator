exp_count = 9;
step_max = 11;

settling_time = [];

for n = 1:exp_count
	aux_settling_time = 0;
	settling_time = [settling_time; zeros(1, step_max)];
	for step = 1:step_max;
		file = sprintf('data/%02d/csv_data/step%d.csv', n, step);
		data = load(file);
		[~, i] = min(abs(1 - data));
		i = i(3);
		aux_settling_time = data(i, 1);
		settling_time(n, step) = aux_settling_time;
	end
end

m_settling_time = zeros(1, step_max);

for n = 1:exp_count
	for step = 1:step_max
		m_settling_time(step) += settling_time(n, step);
	end
end

m_settling_time /= exp_count

