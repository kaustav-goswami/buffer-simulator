import numpy as np

# We are spliting all the parts here:
# 1. we need buffers for the sender

class Packet:
    def __init__(self,
                 pkt_idx,
                 data = "",
                 enqueue_time = 0,
                 process_time = 0,
                 debug = False):
        self._idx = pkt_idx
        self._debug = debug
        self.data = str(data)
        # The packet can be enqueued anytime, we need to keep a track of that
        # time.
        self.enqueue_time = enqueue_time
        # The packet will get automatically popped if the global event queue
        # timer reaches process time
        self.process_time = process_time
    
    def __del__(self):
        if self._debug == True:
            print(f"info: packet idx {self._idx} was destroyed!")
    
    def func_reset_data(self, data: str):
        # sets data with 0 latency.
        self.data = data
        
    def get_data(self):
        return self.data