#!/usr/bin/python

from pydbus import SystemBus
bus = SystemBus()

# Create an object that will proxy for a particular remote object.
remote_object = bus.get(
    "com.example.HelloWorld", # Bus name
    "/HelloWorld" # Object path
)

print(remote_object.SayHello("BOB"))
print(remote_object.SayHello("CHARLES"))
