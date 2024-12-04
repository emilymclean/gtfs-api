import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from os import PathLike
from pathlib import Path
from typing import TypeVar, Generic, Any, AnyStr, Optional, List, Tuple, Dict

from ..time_helper import TimeHelper

T = TypeVar("T")
R = TypeVar("R")


class GeneratorComponent(ABC):
    config: Dict[str, Any]
    time_helper: TimeHelper

    @abstractmethod
    def generate(self, output_folder: Path):
        pass

    def _write_distinguished(self, data: bytes|str, distinguisher: Optional[str], path: str | PathLike):
        if distinguisher is None:
            return

        self._write(data, Path(distinguisher).joinpath(path))

    def _write(self, data: bytes|str, path: str | PathLike):
        path = Path(path)
        sha_path = Path(f"{path}.sha")
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            sha = sha256(data).digest()
            with path.open('wb') as f:
                f.write(data)
        else:
            sha = sha256(data.encode('utf-8')).digest()
            with path.open('w') as f:
                f.write(data)

        with sha_path.open('wb') as f:
            f.write(sha)



class GeneratorFormat(ABC, Generic[T]):
    config: Dict[str, Any]
    time_helper: TimeHelper

    @abstractmethod
    def extension(self) -> str:
        pass

    @abstractmethod
    def parse(self, intermediary: T, distinguisher: Optional[str]) -> Any:
        pass

    @abstractmethod
    def to_final(self, data: Any) -> AnyStr:
        pass


class JsonGeneratorFormat(Generic[T], GeneratorFormat[T], ABC):

    def extension(self) -> str:
        return "json"

    def to_final(self, data: Any) -> AnyStr:
        return json.dumps(data)


class ProtoGeneratorFormat(Generic[T], GeneratorFormat[T], ABC):

    def extension(self) -> str:
        return "pb"

    def to_final(self, data: Any) -> AnyStr:
        return data.SerializeToString()


class FormatGeneratorComponent(Generic[T], GeneratorComponent, ABC):
    endpoint: str
    distinguishers: List[str]

    @abstractmethod
    def _formats(self) -> List[GeneratorFormat[T]]:
        pass

    @abstractmethod
    def _path(self, output_folder: Path, intermediary: T, extension: str) -> Path:
        pass

    def generate(self, output_folder: Path):
        distinguished: List[Tuple[Optional[str], List[T]]] = (
            [(d, self._read_intermediary(d)) for d in self.distinguishers])
        distinguished.append((None, self._read_intermediary(None)))
        formats = self._formats()
        for dc in distinguished:
            d, im = dc
            for i in im:
                for f in formats:
                    f.config = self.config
                    f.time_helper = self.time_helper
                    self._write_for_format(i, d, f, output_folder)

    def _write_for_format(self, intermediary: T, distinguisher: Optional[str], format: GeneratorFormat[T], output_folder: Path):
        created = format.parse(intermediary, distinguisher)
        path = self._path(
            output_folder if distinguisher is None else output_folder.joinpath(distinguisher),
            intermediary,
            format.extension()
        )

        self._write(format.to_final(created), path)

    @abstractmethod
    def _read_intermediary(self, distinguisher: Optional[str]) -> List[T]:
        pass


@dataclass
class IndexedWrapper(Generic[T]):
    index: Optional[str]
    data: List[T]


class IndexedGeneratorComponent(Generic[T], FormatGeneratorComponent[IndexedWrapper[T]], ABC):

    @abstractmethod
    def _name(self) -> str:
        pass

    def _path(self, output_folder: Path, intermediary: IndexedWrapper[T], extension: str) -> Path:
        name = self._name()
        if intermediary.index is None:
            return output_folder.joinpath(f"{name}.{extension}")
        else:
            return output_folder.joinpath(f"index/{name}/{intermediary.index}/{name}.{extension}")

    def _read_intermediary(self, distinguisher: Optional[str]) -> List[IndexedWrapper[T]]:
        idx = {key: [] for key in "abcdefghijklmnopqrstuvwxyz0123456789"}
        all = self._read_all_intermediary(distinguisher)

        for entry in all:
            keys = {k[0].lower() for k in self._keys_from_intermediary(entry)}
            for k in keys:
                idx[k].append(entry)

        indexed = [IndexedWrapper(k, v) for k, v in idx.items()]
        indexed.append(IndexedWrapper(None, all))

        return indexed

    @abstractmethod
    def _read_all_intermediary(self, distinguisher: Optional[str]) -> List[T]:
        pass

    @abstractmethod
    def _keys_from_intermediary(self, intermediary: T) -> List[str]:
        pass
