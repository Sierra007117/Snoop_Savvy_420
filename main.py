import usb.core
import usb.util

def capture_cpcl_commands():
    # Find the printer device
    dev = usb.core.find(find_all=True)
    printer = None

    # Iterate through the connected USB devices and identify the printer
    for device in dev:
        if device.bDeviceClass == 7:  # Printer class
            printer = device
            break

    if printer is None:
        raise ValueError("Printer device not found.")

    # Set up the USB interface and endpoints for capture
    cfg = printer.get_active_configuration()
    intf = cfg[(0, 0)]
    ep_in = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

    # Open the device and start capturing
    printer.reset()
    printer.set_configuration(cfg)
    usb.util.claim_interface(printer, intf)

    try:
        # Capture USB traffic
        while True:
            # Capture IN (device to host) packets
            data_in = printer.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=5000)
            if len(data_in) > 0:
                cpcl_command = data_in.decode('utf-8')
                print("CPCL Command (IN):", cpcl_command)

            # Capture OUT (host to device) packets
            data_out = b"YOUR_CPCL_COMMAND_HERE"  # Replace with the CPCL command you want to send
            printer.write(ep_out.bEndpointAddress, data_out, timeout=5000)
            print("CPCL Command (OUT):", data_out)

            # Check if self-test page option is enabled
            if data_out == b"SELF_TEST_PAGE_COMMAND":
                # Print self-test page
                self_test_cmd = b"CPCL COMMAND TO PRINT SELF-TEST PAGE"
                printer.write(ep_out.bEndpointAddress, self_test_cmd, timeout=5000)
                print("Printing self-test page...")

            # Capture IN (device to host) packets after sending OUT command
            data_in = printer.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=5000)
            if len(data_in) > 0:
                cpcl_command = data_in.decode('utf-8')
                print("CPCL Command (IN):", cpcl_command)

    except KeyboardInterrupt:
        pass

    # Release the claimed interface and close the device
    usb.util.release_interface(printer, intf)
    usb.util.dispose_resources(printer)

# Start capturing CPCL commands
capture_cpcl_commands()
