data = load("lol.csv")
%data = load("asp_data.csv");

time = data(:, 1);
job_progress = data(:, 3) * 100;
replicas = data(:, 4);

figure;
title("Asperathos Simulation")
subplot(2, 1, 1);
plot(time, job_progress);
ylabel("Job progress (%)");
xlabel("Time (s)");
grid;

subplot(2, 1, 2);
plot(time, replicas);
ylabel("Replicas");
xlabel("Time (s)");
ylim([0, 5]);
grid;

