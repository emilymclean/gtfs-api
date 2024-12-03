import json
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import TypeVar, Generic, Any, AnyStr, Optional, List

from ..generator import GtfsCsv

T = TypeVar("T")
O = TypeVar("O")


class GeneratorComponent(ABC):
    _output_folder: Path

    def __init__(self, output_folder: Path):
        self._output_folder = output_folder

    @abstractmethod
    def generate(self):
        pass

    def _write_distinguished(self, data: AnyStr, distinguisher: Optional[str], path: str | PathLike):
        if distinguisher is None:
            return

        self._write(data, Path(distinguisher).joinpath(path))

    @abstractmethod
    def _write(self, data: AnyStr, path: str | PathLike):
        path = self._output_folder.joinpath(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write(data)


class GeneratorFormat(ABC, Generic[T]):

    @abstractmethod
    def extension(self) -> str:
        pass

    @abstractmethod
    def parse(self, intermediary: T) -> Any:
        pass

    @abstractmethod
    def to_final(self, data: Any) -> AnyStr:
        pass


class JsonGeneratorFormat(GeneratorFormat[T], ABC):

    def extension(self) -> str:
        return "json"

    def to_final(self, data: Any) -> AnyStr:
        return json.dumps(data)


class ProtoGeneratorFormat(GeneratorFormat[T], ABC):

    def extension(self) -> str:
        return "pb"

    def to_final(self, data: Any) -> AnyStr:
        return data.SerializeToString()


class FormatGeneratorComponent(Generic[T], GeneratorComponent, ABC):
    endpoint: str

    @abstractmethod
    def formats(self) -> List[GeneratorFormat[T]]:
        pass

    def generate(self):
        

    def read_intermediary(self):

    @abstractmethod
    def _messages_to_message(self, messages: List[Message]) -> Message:

    @abstractmethod
    def _generate_single_json(self, csv: GtfsCsv) -> List:
        pass

    @abstractmethod
    def _generate_single_pb(self, csv: GtfsCsv) -> List[Message]:
        pass