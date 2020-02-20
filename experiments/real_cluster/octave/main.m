pkg load control

exp = 1;
step_amplitude = 5;

model_queue_length = 1536;
queue_length = 800;

[y, t, u, Ts] = loadExperimentData(exp, step_amplitude);

%% Identifying the system
[y_id, t_id, u_id, Ts_id] = loadExperimentData(exp, 1);
y_filtered = y_id;
N = length(y_id);
if (y_id(N - 1) == 1)
	y_filtered = y_id(1:(N - 1));
end

[G, L, T] = identifySystem(1, y_filtered, Ts_id)
L
L = abs(L);
%% Approximating the delay function e^-sT by Padé Coefficients
[pade_num, pade_den] = padecoef(L, 9);
delay = tf(pade_num, pade_den);

G = tf([G], [T, 1]) * delay;
G = c2d(G, Ts);
t_s_exp = 0;

for i = 1:length(y)
	if (y(i) == 1)
		t_s_exp = t(i);
		break;
	end
end

t_sim = 0:Ts:t_s_exp;
u_sim = ones(1, length(t_sim)) * step_amplitude;
[y_sim, t_sim, x] = lsim(G, u_sim, t_sim);

%t_s_model
[~, i] = min(abs(1 - y_sim));
t_s_model = t_sim(i);

% Expected time for given `queue_length`:
[~, i] = min(abs(queue_length/model_queue_length - y_sim));
expected_ts = t_sim(i);

fprintf('For a queue of length equal to %d, the job is expected to finish at %d seconds.\n', queue_length, expected_ts);

figure;
subplot(2, 1, 1);
plot(t_sim, y_sim*100, sprintf(';Model(t_s=%ds);', t_s_model), 'linestyle', '--');
title(sprintf('Output (Jobs completed) for step = %d replicas.', step_amplitude));
hold on;
plot(t, y*100, sprintf(';Experimental Data(t_s=%ds);', t_s_exp), 'color', 'g');
ylim([0, 105]);
xlim([0, t(length(t) - 1)]);
ylabel('Job Progress(%)');
xlabel("Time (s)");
grid();

subplot(2, 1, 2);
plot(t_sim, u_sim, 'linestyle', '--');
title('Input( Replicas)');
hold on;
plot(t, u, 'color', 'g');
ylabel('Replicas');
xlabel('Time (s)');
ylim([0, step_amplitude + 1]);
xlim([0, t(length(t) - 1)]);
grid();

