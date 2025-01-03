from typing import Dict, Any, Optional, List, Tuple


def _get_route_designation(code: str, extras: Dict[str, Any]) -> Optional[str]:
    special_designations: List | None = extras.get("route", {}).get("special-designations", None)
    if special_designations is None:
        return None

    for d in special_designations:
        if f"{d['code']}" == code:
            return d["designation"]

    return None


def _get_route_prefix(designation: str, extras: Dict[str, Any]) -> Optional[str]:
    return extras.get("designations", {}).get(designation, {}).get("prefix", None)


def _get_route_real_time(id: str, extras: Dict[str, Any]) -> Optional[str]:
    rt: List = extras.get("route", {}).get("real-time", None)
    if rt is None:
        return None

    for r in rt:
        if id == r["id"]:
            return r["url"]
    return None


def _get_route_colors(code: str, extras: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    colors: List[Any]|None = extras.get("route", {}).get("colors", None)

    if colors is None:
        return None

    for color in colors:
        if f"{color['code']}" == code:
            return color["color"], color["onColor"]

    return None