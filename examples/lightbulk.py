# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola

import uuid

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import Colorific

import binascii
import logging
import time

logging.basicConfig(level=logging.DEBUG)

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()


# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    #ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    #adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    Colorific.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = Colorific.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    print device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout

    print device.name
    print device.advertised

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        Colorific.discover(device)

        print "Discover finished"

        # services = device.list_services()
        # for s in services:
        #     print s.uuid
        #     chars = s.list_characteristics()
        #     for c in chars:
        #         print "\t\t", c.uuid

        u1 = uuid.UUID('00001803-0000-1000-8000-00805f9b34fb')
        rgb = device.find_service(u1)
        print rgb.uuid

        u2 = uuid.UUID('00002a06-0000-1000-8000-00805f9b34fb')
        c = rgb.find_characteristic(u2)
        print c.uuid

        r = 0
        g = 0
        b = 255
        command = '\x58\x01\x03\x01\xFF\x00{0}{1}{2}'.format(chr(r & 0xFF),
                                                             chr(g & 0xFF),
                                                             chr(b & 0xFF))

        print "Value", binascii.hexlify( c.read_value() )

        c.write_value( command )

        time.sleep(1)

    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()



# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
