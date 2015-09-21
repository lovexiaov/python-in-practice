#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import collections
import random

random.seed(917) # Not truly random for ease of regression testing


def main():
    totalCounter = Counter()
    carCounter = Counter("cars")
    commercialCounter = Counter("vans", "trucks")

    multiplexer = Multiplexer()
    for eventName, callback in (("cars", carCounter),
            ("vans", commercialCounter), ("trucks", commercialCounter)):
        multiplexer.connect(eventName, callback)
        multiplexer.connect(eventName, totalCounter)

    for event in generate_random_events(100):
        multiplexer.send(event)
    print("After 100 active events:  cars={} vans={} trucks={} total={}"
            .format(carCounter.cars, commercialCounter.vans,
                    commercialCounter.trucks, totalCounter.count))

    multiplexer.state = Multiplexer.DORMANT
    for event in generate_random_events(100):
        multiplexer.send(event)
    print("After 100 dormant events: cars={} vans={} trucks={} total={}"
            .format(carCounter.cars, commercialCounter.vans,
                    commercialCounter.trucks, totalCounter.count))
    
    multiplexer.state = Multiplexer.ACTIVE
    for event in generate_random_events(100):
        multiplexer.send(event)
    print("After 100 active events:  cars={} vans={} trucks={} total={}"
            .format(carCounter.cars, commercialCounter.vans,
                    commercialCounter.trucks, totalCounter.count))
    

def generate_random_events(count):
    vehicles = (("cars",) * 11) + (("vans",) * 3) + ("trucks",)
    for _ in range(count):
        yield Event(random.choice(vehicles), random.randint(1, 3))



class Counter:

    def __init__(self, *names):
        self.anonymous = not bool(names)
        if self.anonymous:
            self.count = 0
        else:
            for name in names:
                if not name.isidentifier():
                    raise ValueError("names must be valid identifiers")
                setattr(self, name, 0)


    def __call__(self, event):
        if self.anonymous:
            self.count += event.count
        else:
            count = getattr(self, event.name)
            setattr(self, event.name, count + event.count)


class Event:

    def __init__(self, name, count=1):
        if not name.isidentifier():
            raise ValueError("names must be valid identifiers")
        self.name = name
        self.count = count


class Multiplexer:

    ACTIVE, DORMANT = ("ACTIVE", "DORMANT")

    def __init__(self):
        self.callbacksForEvent = collections.defaultdict(list)
        self.state = Multiplexer.ACTIVE


    def connect(self, eventName, callback):
        if self.state == Multiplexer.ACTIVE:
            self.callbacksForEvent[eventName].append(callback)


    def disconnect(self, eventName, callback=None):
        if self.state == Multiplexer.ACTIVE:
            if callback is None:
                del self.callbacksForEvent[eventName]
            else:
                self.callbacksForEvent[eventName].remove(callback)


    def send(self, event):
        if self.state == Multiplexer.ACTIVE:
            for callback in self.callbacksForEvent.get(event.name, ()):
                callback(event)


if __name__ == "__main__":
    main()
