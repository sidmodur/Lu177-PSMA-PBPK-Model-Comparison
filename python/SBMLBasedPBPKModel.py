from abc import ABC, abstractmethod
import io 
import libsbml
import XCATPhantom
import PBPKModel

class SBMLModelParams(PBPKModel.IPBPKModelParams):

    def __init__(self, listOfParams):
        self.underlying = listOfParams
        self.keys = [elem.getId() for elem in listOfParams.getListOfAllElements()]

    def __getitem__(self, key):
        return self.underlying.getElementBySId(key)
    
    def __setitem__(self, key, value):
        self[key].setValue(value)

    def __str__(self):
        return self.underlying.toSBML()
    
    def __repr__(self):
        return self.underlying.toSBML()

    def get_params(self):
        return self.keys
    
    def __len__(self):
        return self.underlying.size()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        for key in self.keys:
            yield (key, self[key].getValue())

    def __deepcopy__(self, memo):
        SBMLModelParams(self.underlying.clone())

    def update(self, new_params):
        PBPKModel.IPBPKModelParams(self, new_params)

class SBMLModelCompartments(PBPKModel.IPBPKModelCompartments):
    def __init__(self, listOfParams):
        self.underlying = listOfParams
        self.keys = [elem.getId() for elem in listOfParams.getListOfAllElements()]

    def __getitem__(self, key):
        return self.underlying.getElementBySId(key)
    
    def __setitem__(self, key, value):
        self[key].setValue(value)

    def __str__(self):
        return self.underlying.toSBML()
    
    def __repr__(self):
        return self.underlying.toSBML()

    def get_params(self):
        return self.keys
    
    def __len__(self):
        return self.underlying.size()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        for key in self.keys:
            yield (key, self[key].getValue())

    def __deepcopy__(self, memo):
        SBMLModelCompartments(self.underlying.clone())

    def update(self, new_compartments):
        PBPKModel.IPBPKModelCompartments(self, new_compartments)

class SBMLBasedPBPKModel(PBPKModel.PBPKModel, ABC):

    VALID_SOLVERS = {"Runge-Kutta", "AM1", "BD1", "AM2", "AM3", 
                     "AM4", "BD2", "BD3", "BD4", "AB1", "AB2", 
                     "AB3", "AB4", "Runge-Kutta-Fehlberg", "Cash-Karp"}

    def __init__(self, sbml, name):
        if isinstance(sbml, libsbml.SBMLDocument):
            self.sbmlModel = sbml
        else:    
            reader = libsbml.SBMLReader()
            if isinstance(sbml, str):
                self.sbmlModel = reader.readSBMLFromFile(sbml)
            elif isinstance(sbml, io.IOBase):
                self.sbmlModel = reader.readSBML(sbml.read())
        
        compartments = SBMLModelCompartments(self.sbmlModel.getListOfCompartments())
        params = SBMLModelParams(self.sbmlModel.getListOfParameters())
        super().__init__(params, compartments, name)

    def set_solver(self, solver):
        if solver in self.VALID_SOLVERS:
            self.solver = solver
        else:
            raise ValueError(f"solver not a valid solver. Valid solvers are: {self.VALID_SOLVERS}")