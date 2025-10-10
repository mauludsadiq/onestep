from typing import Iterable, Set, Union

class CompressedFlags:
    """Minimal compressed flags placeholder.
    Internally a Python set[int]; replace with Roaring later.
    """
    __slots__ = ("_bits",)

    def __init__(self) -> None:
        self._bits: Set[int] = set()

    def add(self, items: Iterable[Union[int, str]]) -> None:
        self._bits.update(int(x) for x in items)

    def query(self, other: "CompressedFlags") -> Set[int]:
        if not isinstance(other, CompressedFlags):
            raise TypeError("query expects CompressedFlags")
        return self._bits & other._bits

    # helper accessors for later extensions
    def __len__(self) -> int: return len(self._bits)
    def to_set(self) -> Set[int]: return set(self._bits)
