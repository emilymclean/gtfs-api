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


def _get_route_show_on_browse(route_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return False

    return modifications["show-on-browse"] if "show-on-browse" in modifications else False


def _get_route_event_route(route_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return False

    return modifications["event-route"] if "event-route" in modifications else False


def _get_route_approximate_timings(route_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return False

    return modifications["approximate-timings"] if "approximate-timings" in modifications else False


def _get_route_link_url(route_id: str, extras: Dict[str, Any]) -> Optional[str]:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return None

    return modifications["more-link"] if "more-link" in modifications else None


def _get_route_description(route_id: str, extras: Dict[str, Any]) -> Optional[str]:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return None

    return modifications["description"].strip() if "description" in modifications else None


def _get_route_name(route_id: str, extras: Dict[str, Any]) -> Optional[str]:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return None

    return modifications["name"].strip() if "name" in modifications else None


def _get_route_has_realtime(route_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)
    if modifications is None:
        return True

    return modifications["has-realtime"] if "has-realtime" in modifications else True


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


def _get_search_weight_route(route_id: str, extras: Dict[str, Any]) -> Optional[float]:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)

    if modifications is None:
        return None

    return modifications["search-weight"] if "search-weight" in modifications else None


def _get_hidden_route(route_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("route", {}).get("modifications", {}).get(f"{route_id}", None)

    if modifications is None:
        return False

    return modifications["hidden"] if "hidden" in modifications else False


def _get_show_on_zoom_out_stop(stop_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("stops", {}).get("modifications", {}).get(f"{stop_id}", None)

    if modifications is None:
        return False

    return modifications["show-on-zoom-out"] if "show-on-zoom-out" in modifications else False


def _get_show_on_zoom_in_stop(stop_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("stops", {}).get("modifications", {}).get(f"{stop_id}", None)

    if modifications is None:
        return True

    return modifications["show-on-zoom-in"] if "show-on-zoom-in" in modifications else True


def _get_show_children_stop(stop_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("stops", {}).get("modifications", {}).get(f"{stop_id}", None)

    if modifications is None:
        return False

    return modifications["show-children"] if "show-children" in modifications else False


def _get_search_weight_stop(stop_id: str, extras: Dict[str, Any]) -> Optional[float]:
    modifications: Dict[str, Any] | None = extras.get("stops", {}).get("modifications", {}).get(f"{stop_id}", None)

    if modifications is None:
        return None

    return modifications["search-weight"] if "search-weight" in modifications else None


def _get_name_stop(stop_id: str, extras: Dict[str, Any]) -> Optional[str]:
    modifications: Dict[str, Any] | None = extras.get("stops", {}).get("modifications", {}).get(f"{stop_id}", None)

    if modifications is None:
        return None

    return modifications["name"] if "name" in modifications else None


def _get_has_realtime_stop(stop_id: str, extras: Dict[str, Any]) -> bool:
    modifications: Dict[str, Any] | None = extras.get("stops", {}).get("modifications", {}).get(f"{stop_id}", None)

    if modifications is None:
        return True

    return modifications["has-realtime"] if "has-realtime" in modifications else True
