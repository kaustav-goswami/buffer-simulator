from typing import List
from .application import Application
from packet.packet import Packet

import numpy as np
import random

class Encoder(Application):
    # This also generates delays but for the encoder. Therefore these are
    # independent.
    def __init__(self,
                 name: str,
                 traffic_type: str,
                 length: int,
                 params: dict):
        super().__init__(name = name,
                        traffic_type = traffic_type,
                        length = length,
                        params = params)
    
class EncoderV2(Encoder):
    # This is the updated encoder which takes in an array of bits to process
    def __init__(self,
                 name: str,
                 traffic_type: str,
                 length: int,
                 params: dict,
                 simulator_quantum: int,
                 message: List[int]):
        super().__init__(name = name,
                        traffic_type = traffic_type,
                        length = length,
                        params = params)
        self._quantum = simulator_quantum
        self.message = message
        # We need another array to store the interpacket timing values.
        self.encoded_message = []
        # We are moving the timing addition into the packets into this class
        # with the new information.
        
        # self.encoded_message_ipd = []
    
    def _convert_to_quantum(self, value):
        return int(self._quantum * value)
    
    def _get_encoding_times(self, data):
        # cannot process anything other than 0 or 1
        assert(data == 0 or data == 1)
        # get a random time for each data that we get.
        if data == 0:
            return random.randint(self._convert_to_quantum(self.stats["min"]),
                self._convert_to_quantum(self.stats["median"]))
        else:
            return random.randint(self._convert_to_quantum(self.stats["median"]),
                self._convert_to_quantum(self.stats["max"]))
        
    def _process_message(self):
        # this method encodes a gicen message into timing values. this creates
        # packets without any data. make sure that we are not processing
        # an empty message
        assert(len(self.message) > 0)
        
        for element in self.message:
            self.encoded_message.append(self._get_encoding_times(element))
    
    def create_packets(self):
        self._process_message()
        list_of_packets = []
        assert(len(self.encoded_message) > 0)
        for idx, timing_values in enumerate(self.encoded_message):
            # We create a list of packets from the data. we are not allowed to
            # keep the data inside the packets. these packets will only have
            # an enqueuing time.
            list_of_packets.append(Packet(pkt_idx=idx, data="__not_allowed__",
                                          process_time=timing_values))
        return list_of_packets
        