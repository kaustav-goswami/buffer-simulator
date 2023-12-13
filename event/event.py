from packet.packet import Packet
from buffer.buffer import Buffer

class Event:
    # For a push, we enque a packet into Alice's buffer. For a pop, we deque
    # alice's queue and eqneue Bob's queue with the same packet.
    def __init__(self,
                 idx: int,
                 init_time: int,
                 packet: Packet = None,
                 params: dict = None,
                 debug = False):
        # Application sends this packet at some time.
        self._packet = packet
        self._idx = idx
        self._debug = debug
        
        # This is when Alice sees this packet.
        self._init = int(init_time)
        if self._packet is None:
            self._command = "pop"
        else:
            self._command = "push"
        # We will use the params for min, max and median
        self._params = params
        # We delete this event after it is processed!
        self._end = self._get_end_time()
    
    def __del__(self):
        if self._debug == True:
            print(f"info: Event {self._idx} was peocessed!")
    
    def process_event(self, current_time):
        if self._command == "push":
            # push this packet to Alice's queue at this stage.
            self._packet.process_time = current_time + self._end
            # This event will have a pop event for this packet at the end time.
            return [self._command, A.push(self._packet)]
        else:
            # pop this packet form Alice's queue and push this packet in Bob's
            # queue.
            packet = A.get_pop_packet()
            if packet is not None:
                packet.enqueue_time = current_time
                B.enqueue_packet(packet)
            return [self._command, A.pop()]

    def _get_end_time(self):
        if self._command == "push":
            # find process time from the encoding delays. this time is
            # calculated everytime when a 0 or a 1 is encountered.
            if self._packet.get_data() == "0":
                self._packet.process_time = 10000
                return 10000
            else:
                self._packet.process_time = 33333
                return 33333
    
    def _get_end_time_random(self):
        if self._command == "push":
            # print(convert_to_quantum(self._params["min"]), convert_to_quantum(self._params["median"]), convert_to_quantum(self._params["max"]))
            # find process time from the encoding delays. this time is
            # calculated everytime when a 0 or a 1 is encountered.
            if self._packet.get_data() == "0":
                return random.randint(convert_to_quantum(self._params["min"]),
                                    convert_to_quantum(self._params["median"]))
            else:
                return random.randint(
                                    convert_to_quantum(self._params["median"]),
                                    convert_to_quantum(self._params["max"]))
class EventV2(Event):
    def __init__(self,
                idx: int,
                init_time: int,
                batch_size: int = None,
                packet: Packet = None,
                params: dict = None,
                debug = False):
        super().__init__(idx=idx,
                         init_time=init_time,
                         packet=packet,
                         params=params,
                         debug=debug)
        
        # We will not pop packets from Alice's buffer until batch_size number
        # of packets are enqueued.
        self._batch_size = batch_size
        # self._pop_queue = []
        # We delete this event after it is processed!
        self._end = self._get_end_time_random()
        
    def process_event(self, current_time, Alice, Bob):
        if self._command == "push":
            # push this packet to Alice's queue at this stage.
            self._packet.process_time = current_time + self._end
            # This event will have a pop event for this packet at the end time.
            return [self._command, Alice.push(self._packet), None]
        else:
            # pop this packet form Alice's queue and push this packet in Bob's
            # queue.
            # We only start processing packets if there are batch_size number
            # of packets are present.
            
            # we only consider the first N buffered cases.application_times
            if Alice.buffering_phase == True:
                if len(Alice.buffer) < self._batch_size:
                    # need to keep this pop event pending
                    self._init=self._init + 1
                    return [self._command, False, "+1", self]
                else:
                    Alice.buffering_phase = False
                    # pop this packet
                    print("ver 4 popped!!!")
                    packet = Alice.get_pop_packet()
                    if packet is not None:
                        packet.enqueue_time = current_time
                        Bob.enqueue_packet(packet)
                    return [self._command, Alice.pop(), "+2", Alice]
                
            else:
                print("popped!!!")
                packet = Alice.get_pop_packet()
                if packet is not None:
                    packet.enqueue_time = current_time
                    Bob.enqueue_packet(packet)
                return [self._command, Alice.pop(), None]

class EventV3:
    """This is a simple event with a start time and an end time. this event
    should insert an object to a buffer and pop an object from a buffer.
    """
    def __init__(self,
                 idx: int,
                 command: str,
                 buffer: Buffer,
                 time: int,
                 packet: Packet,
                 recv: Buffer = None,
                 debug: bool = False):
        self._idx = idx
        self._time = time
        self._packet = packet
        self._debug = debug
        self._command = command
        self._buffer = buffer
        self._recv = recv
    
    def __del__(self):
        # This event shoulf be deleted at end time. if not, then crash this
        # program
        if self._debug == True:
            print("event:", self._idx, "event deleted!")
    
    def process_event(self, gambler_name):
        # this adds a new logic to map the gambler's ruin problem.
        old_status = self.process_event()
        return old_status
    
    def process_event(self):
        # overrides older process_Events
        status = [True, None]
        if self._command == "push":
            status[0] = self._buffer.push(self._packet)
            if self._debug == True and status[0] == True:
                print(f"event: pushed into {self._buffer._name} buffer with length {len(self._buffer.buffer)}")
        elif self._command == "pop":
            status[0] = self._buffer.pop()
            if self._debug == True and status[0] == True:
                print(f"event: popped from {self._buffer._name} buffer with length {len(self._buffer.buffer)}")
        return status
        
    