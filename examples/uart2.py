# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola

import uuid

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

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
    UART.disconnect_devices()

    # Enter a loop and print out whenever a new UART device is found.
    known_uarts = set()
    myDevice = None
    try:
        adapter.start_scan()
        notFound = True
        while notFound:
            # Call UART.find_devices to get a list of any UART devices that
            # have been found.  This call will quickly return results and does
            # not wait for devices to appear.
            found = set(UART.find_devices())
            # Check for new devices that haven't been seen yet and print out
            # their name and ID (MAC address on Linux, GUID on OSX).
            new = found - known_uarts
            for device in new:
                print('Found UART: {0} [{1}]'.format(device.name, device.id))
                print type(device.name)
                if "NickBLE" in device.name:
                    myDevice = device
                    notFound = False

            known_uarts.update(new)
            # Sleep for a second and see if new devices have appeared.
            time.sleep(1.0)
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()


    print('Connecting to device...')
    print myDevice.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout

    print myDevice.name
    print myDevice.advertised

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        UART.discover(myDevice)

        print "Discover finished"

        services = device.list_services()
        for s in services:
            print s.uuid
            chars = s.list_characteristics()
            for c in chars:
                print "\t\t", c.uuid

        u1 = uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
        uart = myDevice.find_service(u1)
        print uart.uuid

        u2 = uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
        tx = uart.find_characteristic(u2)
        print tx.uuid

        u3 = uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
        rx = uart.find_characteristic(u3)
        print rx.uuid

        def _rx_received(data):
            print data

        rx.start_notify(_rx_received)

        tx.write_value( "PYTHON RULEZ" )

        while True:
            time.sleep(1)

    finally:
        # Make sure device is disconnected on exit.
        myDevice.disconnect()



# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
