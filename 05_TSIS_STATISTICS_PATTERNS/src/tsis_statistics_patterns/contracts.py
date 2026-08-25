from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AtlasConfig:
    atlas_version: str = "v0_1"
    trajectory_sessions: int = 20
    episode_cooldown_sessions: int = 20
    relative_volume_sessions: int = 20
    resistance_sessions: dict[str, int] = field(
        default_factory=lambda: {
            "previous_day": 1,
            "previous_week": 5,
            "previous_month": 21,
            "previous_quarter": 63,
            "previous_half_year": 126,
            "previous_year": 252,
        }
    )
    gap_thresholds: tuple[float, ...] = (
        0.10,
        0.20,
        0.30,
        0.50,
        0.75,
        1.00,
        1.50,
        2.00,
        3.00,
    )
    close_advance_thresholds: tuple[float, ...] = (0.20, 0.30, 0.50, 1.00)
    relative_volume_thresholds: tuple[float, ...] = (3.0, 5.0, 10.0, 20.0)
    range_thresholds: tuple[float, ...] = (0.20, 0.30, 0.50, 1.00)
    quantiles: tuple[float, ...] = (0.10, 0.25, 0.50, 0.75, 0.90)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AtlasConfig":
        payload: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        windows = payload["windows"]
        thresholds = payload["activation_thresholds"]
        return cls(
            atlas_version=str(payload["atlas_version"]),
            trajectory_sessions=int(windows["trajectory_sessions"]),
            episode_cooldown_sessions=int(windows["episode_cooldown_sessions"]),
            relative_volume_sessions=int(windows["relative_volume_sessions"]),
            resistance_sessions={k: int(v) for k, v in windows["resistance_sessions"].items()},
            gap_thresholds=tuple(float(x) for x in thresholds["gap_pct"]),
            close_advance_thresholds=tuple(float(x) for x in thresholds["close_advance_pct"]),
            relative_volume_thresholds=tuple(float(x) for x in thresholds["relative_volume"]),
            range_thresholds=tuple(float(x) for x in thresholds["range_pct"]),
            quantiles=tuple(float(x) for x in payload["statistics"]["quantiles"]),
        )


SESSION_KEY = ["ticker", "date"]
EPISODE_KEY = ["episode_id"]
TRAJECTORY_KEY = ["episode_id", "offset_session"]
EVENT_KEY = ["episode_id", "event_label"]
