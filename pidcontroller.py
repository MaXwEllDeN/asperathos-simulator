
class PIDController:    
    def __init__(self, kp, ki, kd, dt):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.dt = dt
        self.i = 0
        self.d = 0
        self.prev_error = 0

    def work(self, e):
        self.i += self.dt * e
        self.d = (e - self.prev_error) / self.dt

        control_action = self.kp * e + (self.ki * self.i) + (self.kd * self.d)

        return control_action
