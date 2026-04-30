from abc import ABC, abstractmethod


class Chromosome(ABC):
    generation: int = 0
    created_generation: int = 0
    created_with: str = None

    @abstractmethod
    def cost(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def copy(self):
        raise NotImplementedError()
