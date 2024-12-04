from typing import Dict, Any, Optional, List, Tuple


def _get_route_designation(code: str, extras: Dict[str, Any]) -> Optional[str]:
    special_designations: List | None = extras.get("route", {}).get("special-designations", None)
    if special_designations is None:
        return None

    for d in special_designations:
        if d["code"] == code:
            return d["designation"]

    return None


def _get_route_prefix(designation: str, extras: Dict[str, Any]) -> Optional[str]:
    return extras.get("designations", {}).get(designation, {}).get("prefix", None)


def _get_route_colors(code: str, extras: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    colors: List[Any]|None = extras.get("route", {}).get("colors", None)

    if colors is None:
        return None

    for color in colors:
        if color["code"] == code:
            return color["color"], color["onColor"]

    return None