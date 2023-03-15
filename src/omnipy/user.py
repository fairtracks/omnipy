from typing import Iterable

from omnipy.vehicles import Car

from .isvehicle import IsVehicle


def drive_vehicle(vehicle: IsVehicle):
    vehicle.drive()


drive_vehicle(Car())


class Plane:
    def fly(self):
        print('Flying')


drive_vehicle(Plane())


class MyStuff:
    def __iter__(self):
        ...


isinstance(MyStuff, Iterable)
