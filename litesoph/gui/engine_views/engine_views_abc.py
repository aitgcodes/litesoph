from abc import ABC, abstractmethod


class EngineViews(ABC):

    @abstractmethod
    def create_input_widgets(self):
        pass

    @abstractmethod
    def get_parameters(self):
        pass