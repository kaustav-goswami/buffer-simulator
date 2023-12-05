# import os
# import sys

# # all the source files are one directory above.                             
# sys.path.append(                                                            
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# )
from packet.packet import Packet                                  

class Buffer:
    def __init__(self,
                 buffer_name: str,
                 buffer_size: int,
                 debug = False):
        # Sets up a buffer with a specific size for the simulation
        self._name = buffer_name
        self._buffer_pointer = 0
        self._debug = debug
        self.buffer_size = buffer_size
        self.buffer = []
    
    def __del__(self):
        if self._debug == True:
            print(f"info: Buffer {self._name} was destroyed!")
    
    def _get_buffer_size(self):
        return self.buffer_size
    
    def push(self, packet: Packet):
        # For maintianing naming convention
        if self._debug == True:
            print(f"buffer: pushing into {self._name} buffer with current length {len(self.buffer)}")
        return self.enqueue_packet(packet)

    def pop(self):
        # For maintianing naming convention
        return self.dequeue_packet()

    def enqueue_packet(self, packet: Packet):
        if self._buffer_pointer < self._get_buffer_size() and \
                self._buffer_pointer >= 0:
            # can enqueue this packet into the buffer.
            self.buffer.append(packet)
            self._buffer_pointer += 1
            # print(self.buffer)
            return True
        elif self._buffer_pointer >= self._get_buffer_size():
            if self._debug == True:
                print(f"warn: buffer overflow with packet {packet._idx}!")
            # could not enqueue this packet
            return False
        else:
            raise NotImplementedError(
                f"fatal: unhandled exception at {self.__name__}")
    
    def get_pop_packet(self):
        if self._buffer_pointer > 0:
            return self.buffer[0]
        else:
            return None
    
    def dequeue_packet(self):
        # Poor implementation of a buffer!
        if self._buffer_pointer <= 0:
            if self._debug == True:
                print(f"warn: buffer underflow!")
            # could not enqueue this packet
            return False
        else:
            # The packet object will get automatically deleted!
            if len(self.buffer) > 0:
                self.buffer = self.buffer[1:]
                self._buffer_pointer -= 1
            else:
                self.buffer = []
                self._buffer_pointer = 0
            return True

class BatchedBuffers(Buffer):
    def __init__(self,
                 buffer_name: str,
                 buffer_size: int,
                 batch_size: int,
                 debug: bool = False):
        super().__init__(buffer_name=buffer_name,
                       buffer_size=buffer_size,
                       debug=debug)
        
        self.batch_size = batch_size
        self.buffering_phase = True