import sys
import json
import logging
import queue
import threading
import time

import serial


class UARTTable:
    def __init__(self, port, baudrate=115200, logging_level=logging.INFO):
        self.port = port
        self.baudrate = 115200
        self.ser = None
        self.stop_sig = threading.Event()
        self.stop_sig.clear()

        self.data_table = {}

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)
        
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setStream(sys.stdout)
            ch.setLevel(logging.DEBUG)
            # ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s::%(threadName)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            self.logger.addHandler(ch)
    
    def connect(self):
        self.logger.info("Connecting to serial port {0}...".format(self.port))
        # close any exising connection
        if self.ser:
            self.ser.close()
        while 1:
            # if main want to exit, we no longer try connect to port
            if self.stop_sig.is_set():
                return
            try:
                self.ser = serial.Serial(self.port, baudrate=self.baudrate)
            except serial.serialutil.SerialException as e:
                self.logger.error(str(e))
                self.logger.debug("Still trying...")
                time.sleep(0.5)
                continue
            
            # we only reach here if serial connection is established
            if self.ser.is_open:
                break

        self.logger.info("Connected.")
    
    def stop(self):
        self.stop_sig.set()
        if self.ser:
            self.ser.close()
        self.logger.info("Stopped.")
    
    def start(self):
        self.logger.debug("Starting...")
        self.recvPacket()
    
    def startThreaded(self):
        self.logger.debug("Starting thread...")
        self.t = threading.Thread(target=self.recvPacket)
        self.t.start()

    def get(self, key):
        return self.data_table.get(key)
    
    def recvPacket(self):
        while 1:
            if self.stop_sig.is_set():
                return
            
            c = b""
            buf = b""
            while c != b"\n":
                if self.stop_sig.is_set():
                    return
                buf += c
                # atomically handle serial object exceptions
                try:
                    c = self.ser.read()
                except (AttributeError, TypeError, serial.serialutil.SerialException) as e:
                    print(e)
                    self.connect()
                    continue

            data = buf.decode()
            # self.logger.debug(data)
            try:
                data = json.loads(data)
            except json.decoder.JSONDecodeError:
                self.logger.warning("packet format error.")
                continue
            key = data.get("key")
            if not key:
                self.logger.warning("packet format error.")
                continue
            
            self.data_table[key] = data.get("value")
        

if __name__ == "__main__":
    try:
        uart_table = UARTTable("COM5", logging_level=logging.DEBUG)
        
        # uart_table.start()
        uart_table.startThreaded()

        while 1:
            print(uart_table.get("/joint/0"))
            
            time.sleep(0.01)
    except KeyboardInterrupt:
        uart_table.stop()
