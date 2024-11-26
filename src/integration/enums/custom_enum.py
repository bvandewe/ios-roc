from enum import Enum


class CustomEnum(str, Enum):
    def __repr__(self):
        return self.value
