
class PersistenceManager:
    DATA = None

    def __init__(self):
        self.DATA = []

    def getData(self):
        return self.DATA

    def publish(self, model):
        self.DATA.append(model)
