# -*- coding: utf-8 -*-

import asyncio, argparse, struct, signal, timeit
from bleak import BleakClient
from pylsl import StreamInfo, StreamOutlet

# how often we expect to get new data from device (Hz)
SAMPLINGRATE = 12


class BBeltBleak():
    """
    Experimeting with bleak and asyncio.
    FIXME: better useage of asyncio...
    """

    def __init__(self, addr, char_id, verbose=False, callback=None, loop_interval=5):
        """
        addr: MAC adresse
        char_id: GATT characteristic ID
        verbose: debug info to stdout
        callback: function that will be called upon new samples, with a a list of samples in parameters
        loop_interval: how often sampling rate is shown and connectivity is checked
        """
        self.bamp = 0
        self.bIR = 0  # Note: we might not get additional infrared values
        self.addr = addr
        self.char_id = char_id
        self.verbose = verbose
        self.samples_in = 0
        self.callback = callback
        self.loop_interval = loop_interval
        self.client = BleakClient(self.addr)

    def launch(self):
        """
        blocking call, connect and then wait for notifications
        """
        asyncio.run(self._main())

    def _ble_handler(self, sender, data):
        """
        Handler for incoming BLE Gatt data, update values, print if verbose
        """
        # might get 8 bytes, 4 for red led, 4 for IR led
        if (len(data) >= 4):
            self.bamp = struct.unpack('>L', data[0:4])[0]
            # got optionnal IR value, update it as well
            if (len(data) >= 8):
                self.bIR = struct.unpack('>L', data[4:8])[0]
            self.samples_in += 1

            if self.verbose:
                print("Breathing Amp: " + str(self.bamp) + " raw IR: " + str(self.bIR))

            if self.callback is not None:
                self.callback([self.bamp, self.bIR])

    async def connect(self):
        """
        Establish connection with breathing belt
        """
        if not self.client.is_connected:
            print("Connecting to %s" % self.addr)
            try:
                await self.client.connect()
                print(f"Connected: {self.client.is_connected}")
            except Exception as e:
                print(e)

    async def _main(self):
        print("launch the loop")
        while True:
            try:
                start_time = timeit.default_timer()
                if not self.client.is_connected:
                    await self.connect()
                    if self.client.is_connected:
                        print("start notify")
                        await self.client.start_notify(self.char_id, self._ble_handler)
                        print("notify started")
                    else:
                        print("could not connect")
                # sleep used to debug sampling rate but also to make the script work in the background, and how often we check connectivity
                # TODO: take into account the time taken for connection?
                await asyncio.sleep(self.loop_interval)
                tick = timeit.default_timer()
                # debug info for sampling rate
                sampling_rate_in = 0
                if start_time != tick:
                    sampling_rate_in = self.samples_in / float(tick - start_time)
                print("Samples incoming at: %s Hz" % sampling_rate_in)
                self.samples_in = 0
            except Exception as e:
                print("Exception during belt loop")
                print(e)

    async def _terminate(self):
        await self.client.stop_notify(self.char_id)
        await self.client.disconnect()

    def terminate(self):
        """
        Gracefully end BLE connection
        FIXME: we should await...
        """
        try:
            asyncio.run(self._terminate())
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # make sure to catch SIGINT and also catch SIGTERM signals with KeyboardInterrupt, to cleanup properly later
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    # retrieve MAC address
    parser = argparse.ArgumentParser(
        description='Stream breathing amplitude of bluetooth BLE compatible devices using LSL.')
    parser.add_argument("-m", "--mac-address", help="MAC address of the  device.", default="FB:88:11:1E:90:F3",
                        type=str)
    parser.add_argument("-n", "--name", help="LSL id name on the network", default="ullo_bb", type=str)
    parser.add_argument("-t", "--type", help="LSL id type on the network", default="breathing_amp", type=str)
    parser.add_argument("-v", "--verbose", action='store_true', help="Print more verbose information.")

    parser.set_defaults()
    args = parser.parse_args()

    # characteristic where the belt sends raw values
    char_id = "0000fed1-0000-1000-8000-00805f9b34fb"

    # init LSL streams
    info_bamp = StreamInfo(args.name, args.type, 2, SAMPLINGRATE, 'float32',
                           '%s_%s_%s' % (args.name, args.type, args.mac_address))
    outlet_bamp = StreamOutlet(info_bamp)


    def stream(data):
        """
        will be called by bbelt
        TODO: check parameters (number, types)
        """
        outlet_bamp.push_sample(data)

    #FB:88:11:1E:90:F3
    bbelt = BBeltBleak(args.mac_address, char_id, True, callback=stream)

    # delegate the main loop to Bbelt
    try:
        bbelt.launch()
    except KeyboardInterrupt:
        print("Catching Ctrl-C or SIGTERM, bye!")
    finally:
        # disconnected and erase outlet before letting be
        bbelt.terminate()
        del outlet_bamp
        print("terminated")