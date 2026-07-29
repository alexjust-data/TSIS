"""Small in-memory registries used by RunPreflight."""

from __future__ import annotations

from collections.abc import Mapping

from .contracts import DatasetDefinition, UniverseDefinition


class DatasetRegistry:
    def __init__(self, datasets: Mapping[str, DatasetDefinition] | None = None) -> None:
        self._datasets = dict(datasets or {})

    def resolve(self, dataset_id: str) -> DatasetDefinition | None:
        return self._datasets.get(dataset_id)


class UniverseRegistry:
    def __init__(self, universes: Mapping[str, UniverseDefinition] | None = None) -> None:
        self._universes = dict(universes or {})

    def resolve(self, universe_id: str) -> UniverseDefinition | None:
        return self._universes.get(universe_id)
