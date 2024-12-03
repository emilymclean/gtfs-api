from datetime import datetime
from time import mktime, strptime

from .. import format_pb2 as pb

gt_date_format = "%Y%m%d"


def parse_datetime(format: str, st: str) -> datetime:
    return datetime.fromtimestamp(mktime(strptime(format, st)))


wheelchair_boarding_options = {
    0: "none",
    1: "partial",
    2: "full"
}

wheelchair_boarding_options_pb = {
    0: pb.WheelchairStopAccessibility.WHEELCHAIR_STOP_ACCESSIBILITY_NONE,
    1: pb.WheelchairStopAccessibility.WHEELCHAIR_STOP_ACCESSIBILITY_PARTIAL,
    2: pb.WheelchairStopAccessibility.WHEELCHAIR_STOP_ACCESSIBILITY_FULL
}

route_type_options = {
    0: "tram",
    1: "metro",
    2: "rail",
    3: "bus",
    4: "ferry"
}

route_type_options_pb = {
    0: pb.RouteType.ROUTE_TYPE_TRAM,
    1: pb.RouteType.ROUTE_TYPE_METRO,
    2: pb.RouteType.ROUTE_TYPE_RAIL,
    3: pb.RouteType.ROUTE_TYPE_BUS,
    4: pb.RouteType.ROUTE_TYPE_FERRY
}

timetable_service_exception_type = {
    1: "added",
    2: "removed"
}

timetable_service_exception_type_pb = {
    1: pb.TimetableServiceExceptionType.TIMETABLE_SERVICE_EXCEPTION_TYPE_ADDED,
    2: pb.TimetableServiceExceptionType.TIMETABLE_SERVICE_EXCEPTION_TYPE_REMOVED
}