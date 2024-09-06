from abc import ABC, abstractmethod

class gData(ABC):
    def save(self): ...
    def extract(self): ...
    def _reset(self): ...
    

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwargs)
        return it
    
    def init(self, *args, **kwargs):
        ...

class AbstractSwitch(ABC):
    def __init__(self):
        self.state = None
    
    @abstractmethod
    def deactivate(self):
        pass
    
    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def is_active(self):
        pass

class BoolSwitch(AbstractSwitch):
    def __init__(self):
        super().__init__()
        self.state = False
    
    def deactivate(self):
        self.state = False
    
    def activate(self):
        self.state = True

    def is_active(self):
        return self.state