from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

class Strategy(ABC):
    @abstractmethod
    def on_bar(self, context: Dict[str, Any]) -> None:
        ...

    def on_fill(self, fill: Dict[str, Any]) -> None:
        ...

    def on_funding(self, event: Dict[str, Any]) -> None:
        ...
