class EphemCalc:#Object that include all
    def __init__(self,date,observer,satellite):
        self.observer = observer
        self.observer.date = str(date)
        self.satellite = satellite
        self.satellite.compute(self.observer)

    def return_computed_satellite(self):
        return self.satellite
