from modules.pidcontroller import PIDController
from modules.monitors import MONITOR_CHECK_INTERVAL

CONTROLLER_ACTUATION_TIME = 1
# Expressed on simpy ticks
# for simpy:
# 1 tick =  1s
# 1.5 tick = 1 second and 500 milliseconds

def debug_msg(msg):
    print(f"[CONTROLLER]: {msg}")

def default_controller(env, wmanager, persistence):
    ACTUATION_SIZE = 2
    TRIGGER_UP = 0
    TRIGGER_DOWN = 0

    wmanager.adjust_resources(1)
    while wmanager.is_running():
        data = persistence.getData()

        if len(data) > 0:
            data = data[-1]

            if data["error"] > 0 and data["error"] >= TRIGGER_DOWN:
                wmanager.adjust_resources(data["replicas"] - ACTUATION_SIZE)
            elif data["error"] < 0 and abs(data["error"]) >= TRIGGER_UP:
                wmanager.adjust_resources(data["replicas"] + ACTUATION_SIZE)

        yield env.timeout(CONTROLLER_ACTUATION_TIME)

def pid_controller(env, wmanager, persistence):
    # dt Must be the rating at which the error is updated

    KP = 0.9817
    KI = 0.0871
    KD = 0

    controller = PIDController(KP, KI, KD, dt=1) #dt=MONITOR_CHECK_INTERVAL)

    while wmanager.is_running():
        data = persistence.getData()[-1]

        data = persistence.getData()

        if len(data) > 0:
            data = data[-1]
            # since the asperathos way of calculating the error returns a negative
            # value for error when we're late, we must invert the sign of received monitor error
            # in order to adapt the magnitudes for the tradutional negative feedback loop model

            new_error = -data["error"]
            control_action = int(controller.work(new_error))

            total_rep = wmanager.get_replicas_count() + control_action

            wmanager.adjust_resources(total_rep)

        yield env.timeout(CONTROLLER_ACTUATION_TIME)
