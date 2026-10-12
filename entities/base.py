from abc import ABC, abstractmethod

class BaseEntity(ABC):
    @abstractmethod
    def display_info(self) -> str:

        ...