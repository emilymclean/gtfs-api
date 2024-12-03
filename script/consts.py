import format_pb2 as pb

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