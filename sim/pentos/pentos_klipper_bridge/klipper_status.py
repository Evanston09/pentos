"""Moonraker status parsing helpers for the Gazebo bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MM_TO_M = 0.001


@dataclass(frozen=True)
class BridgePosition:
    """Gazebo joint positions in controller order."""

    x: float
    y: float
    z: float
    a: float
    b: float

    def as_list(self) -> list[float]:
        return [self.x, self.y, self.z, self.a, self.b]


def as_float_sequence(value: Any, min_length: int) -> list[float] | None:
    if not isinstance(value, (list, tuple)) or len(value) < min_length:
        return None
    try:
        return [float(v) for v in value[:min_length]]
    except (TypeError, ValueError):
        return None


def extract_klipper_xyz(status: dict[str, Any]) -> list[float] | None:
    """Extract XYZ in millimeters from a Moonraker status payload."""

    motion_report = status.get("motion_report")
    if isinstance(motion_report, dict):
        live_position = as_float_sequence(motion_report.get("live_position"), 3)
        if live_position is not None:
            return live_position

    toolhead = status.get("toolhead")
    if isinstance(toolhead, dict):
        position = as_float_sequence(toolhead.get("position"), 3)
        if position is not None:
            return position

    return None


def status_to_bridge_position(
    status: dict[str, Any],
    a_default: float = 0.0,
    b_default: float = 0.0,
) -> BridgePosition | None:
    xyz_mm = extract_klipper_xyz(status)
    if xyz_mm is None:
        return None
    return BridgePosition(
        x=xyz_mm[0] * MM_TO_M,
        y=xyz_mm[1] * MM_TO_M,
        z=xyz_mm[2] * MM_TO_M,
        a=a_default,
        b=b_default,
    )


def subscription_request() -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "method": "printer.objects.subscribe",
        "params": {
            "objects": {
                "motion_report": ["live_position"],
                "toolhead": ["position"],
            }
        },
        "id": 1,
    }


def extract_status_update(message: dict[str, Any]) -> dict[str, Any] | None:
    if message.get("method") == "notify_status_update":
        params = message.get("params")
        if isinstance(params, list) and params and isinstance(params[0], dict):
            return params[0]
        return None

    result = message.get("result")
    if isinstance(result, dict):
        status = result.get("status")
        if isinstance(status, dict):
            return status

    return None

