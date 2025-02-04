import math

from gen.component.intermediaries import LocationCSV


class LocationHelper:

    @staticmethod
    def midpoint(ls: list[LocationCSV]) -> LocationCSV:
        lat_r = [math.radians(l.lat) for l in ls]
        lng_r = [math.radians(l.lng) for l in ls]

        X = [math.cos(lat_r[i]) * math.cos(lng_r[i]) for i, _ in enumerate(lat_r)]
        Y = [math.cos(lat_r[i]) * math.sin(lng_r[i]) for i, _ in enumerate(lat_r)]
        Z = [math.sin(lat_r[i]) for i, _ in enumerate(lat_r)]

        x = sum(X) / len(X)
        y = sum(Y) / len(Y)
        z = sum(Z) / len(Z)

        o_lng = math.atan2(y, x)
        hyp = math.hypot(x, y)
        o_lat = math.atan2(z, hyp)

        return LocationCSV(
            math.degrees(o_lat),
            math.degrees(o_lng),
        )
