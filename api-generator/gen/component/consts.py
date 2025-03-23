from .. import format_pb2 as pb

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

service_wheelchair_accessible = {
    0: "unknown",
    1: "accessible",
    2: "inaccessible"
}

service_wheelchair_accessible_pb = {
    0: pb.ServiceWheelchairAccessible.SERVICE_WHEELCHAIR_ACCESSIBLE_UNKNOWN,
    1: pb.ServiceWheelchairAccessible.SERVICE_WHEELCHAIR_ACCESSIBLE_ACCESSIBLE,
    2: pb.ServiceWheelchairAccessible.SERVICE_WHEELCHAIR_ACCESSIBLE_INACCESSIBLE,
}

service_bikes_allowed = {
    0: "unknown",
    1: "allowed",
    2: "disallowed"
}

service_wheelchair_accessible_pb = {
    0: pb.ServiceWheelchairAccessible.SERVICE_WHEELCHAIR_ACCESSIBLE_UNKNOWN,
    1: pb.ServiceWheelchairAccessible.SERVICE_WHEELCHAIR_ACCESSIBLE_ACCESSIBLE,
    2: pb.ServiceWheelchairAccessible.SERVICE_WHEELCHAIR_ACCESSIBLE_INACCESSIBLE,
}

service_bikes_allowed_pb = {
    0: pb.ServiceBikesAllowed.SERVICE_BIKES_ALLOWED_UNKNOWN,
    1: pb.ServiceBikesAllowed.SERVICE_BIKES_ALLOWED_ALLOWED,
    2: pb.ServiceBikesAllowed.SERVICE_BIKES_ALLOWED_DISALLOWED,
}

multiple_qualifier_pb = {
    True: pb.MultipleQualifier.MULTIPLE_QUALIFIER_ALL,
    False: pb.MultipleQualifier.MULTIPLE_QUALIFIER_SOME,
}