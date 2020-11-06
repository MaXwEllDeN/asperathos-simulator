pkg load control

EXP_DIR = "data/step1";

step_amplitude = 1;
model_queue_length = 327;
queue_length = 327;

experiments = dir(EXP_DIR);

G0_array = [];
L_array = [];
T_array = [];

for i = 3:3
	file_name = experiments(i).name;

	[y, t, u, Ts] = loadExperimentData(strcat(EXP_DIR, "/", file_name));

	t = t - t(1);

	%% Identifying the system
	%% To identify the model, we must use an unitary step experiment data
	y_id = y;
	t_id = t;
	u_id = u;
	Ts_id = Ts;

	t_id = t_id - t_id(1);
	y_filtered = y_id;

	N = length(y_id);
	if (y_id(N - 1) == 100)
		y_filtered = y_id(1:(N - 1));
	end

	[G0, L, T] = identifySystem(1, y_filtered, Ts_id)

	%% Approximating the delay function e^-sT by Padé Coefficients

	G0_array = [G0_array, G0];
	L_array	= [L_array, L];
	T_array = [T_array, T];
endfor

G = mean(G0_array);
T = mean(T_array);
L = mean(L_array);

[pade_num, pade_den] = padecoef(L, 7);
delay = tf(pade_num, pade_den);

G = tf([G0], [T, 1]) * delay;
G = c2d(G, Ts);
t_s_exp = 0;

for i = 1:length(y)
	if (y(i) == 100)
		t_s_exp = t(i) - t(1);
		break;
	end
end

%we will double the experiment time to assure that the model will reach 100%

t_sim = 0:Ts:(t_s_exp * 2);

u_sim = ones(1, length(t_sim)) * step_amplitude;
[y_sim, t_sim, x] = lsim(G, u_sim, t_sim);
[~, i] = min(abs(100 - y_sim));
t_s_model = t_sim(i);

% Expected time for given `queue_length`:
[~, i] = min(abs((queue_length/model_queue_length) * 100 - y_sim));
expected_ts = t_sim(i);

fprintf('For a queue of length equal to %d, the job is expected to finish at %d seconds.\n', queue_length, expected_ts);
fprintf('Exp: %03fs\n', t_s_exp);
figure;
subplot(2, 1, 1);
plot(t_sim, y_sim, sprintf(';Model(t_s=%ds);', t_s_model), 'linestyle', '--');
title(sprintf('Output (Jobs completed) for step = %d replicas.', step_amplitude));
hold on;
plot(t, y, sprintf(';Experimental Data(t_s=%ds);', t_s_exp), 'color', 'g');
ylim([-5, 105]);
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
