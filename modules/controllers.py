from modules.pidcontroller import PIDController
from modules.monitors import MONITOR_CHECK_INTERVAL

CONTROLLER_ACTUATION_TIME = 2
# Expressed on simpy ticks
# for simpy:
# 1 tick =  1s
# 1.5 tick = 1 second and 500 milliseconds

def debug_msg(msg):
    print(f"[CONTROLLER]: {msg}")

def default_controller(env, wmanager, persistence):
    DELAY_TO_CHANGE_REPLICAS = 5

    ACTUATION_SIZE = 2
    MAX_REPLICAS = 10
    TRIGGER_UP = 0
    TRIGGER_DOWN = 0

    wmanager.adjust_resources(1)
    wmanager.set_max_replicas(MAX_REPLICAS)

    yield env.timeout(DELAY_TO_CHANGE_REPLICAS)

    data = persistence.getData()[-1]

    while data["job_progress"] < 100:
        data = persistence.getData()[-1]

        if data["error"] > 0 and data["error"] >= TRIGGER_DOWN:
            wmanager.adjust_resources(data["replicas"] - ACTUATION_SIZE)
        elif data["error"] < 0 and abs(data["error"]) >= TRIGGER_UP:
            wmanager.adjust_resources(data["replicas"] + ACTUATION_SIZE)

        yield env.timeout(CONTROLLER_ACTUATION_TIME)

def pid_controller(env, wmanager, persistence):
    # dt Must be the rating at which the error is updated

    KP, KI, KD = 1, 0.14, 0
    controller = PIDController(KP, KI, KD, dt=MONITOR_CHECK_INTERVAL)

    data = persistence.getData()[-1]

    while data["job_progress"] < 100:
        data = persistence.getData()[-1]

        # since the asperathos way of calculating the error returns a negative
        # value for error when we're late, we must invert the sign of received monitor error
        # in order to adapt the magnitudes for the tradutional negative feedback loop model

        new_error = -data["error"]
        control_action = int(controller.work(new_error))

        debug_msg(f"Error: {new_error}")
        debug_msg(f"Control action: {control_action}")

        wmanager.adjust_resources(control_action)

        yield env.timeout(CONTROLLER_ACTUATION_TIME)
