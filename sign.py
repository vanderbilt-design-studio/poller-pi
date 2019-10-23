from typing import Dict, NamedTuple, OrderedDict
import platform

import gpiozero
from gpiozero.pins.mock import MockFactory

# Mock values on non-GPIO computers
if platform.machine() in ['x86', 'x86_64', 'i386', 'i686']:
    gpiozero.Device.pin_factory = MockFactory()

class Sign(NamedTuple):
    switch: Dict[str, gpiozero.Button]
    door: gpiozero.Button

    @classmethod
    def setup(cls: 'Sign') -> 'Sign':
        return cls(
            **{
                'switch': {
                    'one_on': gpiozero.Button(27),
                    'two_on': gpiozero.Button(17)
                },
                # Use pull-down resistor for door pin; if sensor is disconnected, assume door is open.
                'door': gpiozero.Button(18, pull_up=False)
            })

    def as_value_dict(self) -> Dict:
        def read_sensors(sensors):
            if type(sensors) != gpiozero.Button:
                return {
                    key: read_sensors(sensor)
                    for key, sensor in sensors.items()
                }
            return sensors.is_pressed

        return read_sensors(self._asdict())


if __name__ == '__main__':
    print(Sign.setup().as_value_dict())
