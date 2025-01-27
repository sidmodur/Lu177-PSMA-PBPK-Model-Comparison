from abc import ABC, abstractmethod
import XCATPhantom

class IPBPKModelParams(ABC):
    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __str__(self):
        pass
    
    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_params(self):
        pass
    
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __copy__(self, memo):
        pass

    @abstractmethod
    def __deepcopy__(self, memo):
        pass

    def update(self, new_params):
        for param in new_params.get_params():
            self[param] = new_params[param]

class PBPKModelParams(IPBPKModelParams, dict):
    def get_params(self):
        return super().keys()
    
    def update(self, new_params):
        IPBPKModelParams(self, new_params)


class IPBPKModelCompartments(ABC):
    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_compartments(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __copy__(self, memo):
        pass

    @abstractmethod
    def __deepcopy__(self, memo):
        pass
    
    @abstractmethod
    def update(self, new_compartments):
        for compartment in new_compartments.get_compartments():
            self[compartment] = new_compartments[compartment]
            

class PBPKModelCompartments(IPBPKModelCompartments, dict):
    def get_compartments(self):
        return super().keys()
    
    def update(self, new_compartments):
        IPBPKModelCompartments.update(self, new_compartments)


class PBPKModel(ABC):
    def __init__(self, params: IPBPKModelParams, compartments: IPBPKModelCompartments, name):
        self.params = params
        self.name = name
        self.compartments = compartments

    @abstractmethod
    def update_compartments(self, subject: XCATPhantom):
        pass
    
    @abstractmethod
    def simulate(self, time: float, dt:float):
        pass

    def simulate_with_subject(self, subject: XCATPhantom, time: float, dt:float):
        self.update_compartments(subject)
        return self.simulate(time, dt)