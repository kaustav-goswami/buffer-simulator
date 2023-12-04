from packet.packet import Packet
from event.event import EventV3
from buffer.buffer import Buffer
from typing import List

class Simulator:
    def __init__(self,
                 clock_resolution: int,
                 buffers: List[Buffer],
                 timeout = 5000,
                 debug=False):
        self._clock = clock_resolution
        self._sender = buffers[0]
        self._receiver = buffers[1]
        # There is an initial event at t = 0 that starts the communication.
        initial_event = EventV3(idx=-1,
                                    command="push",
                                    buffer=self._sender,
                                    time=0,
                                    packet=None)
        # Our event queue is a simple python array that maintains all the events it
        # has to manage. optionally, one can limit this to make sure that less
        # powerful machines.
        self.event_queue = [] #initial_event]
        self._event_queue_limit = 100000
        
        # expected to simulate this for 100000 seconds
        self._max_length = int(1e4)
        self.simulation_stats = {"status": True, "error": None}
        self._num_traffic_streams = 0
        self._packet_queue = []
        self._live_traffic_queue = []
        self._debug = debug
        self._buffering_length = 1
        self._buffer_push_counter = 0
        self._comm_flag = False
    
    def _check_for_events(self, current_tick):
        new_events_to_queue = []
        status = False
        if len(self._packet_queue) > 0:
            # There are packets in the packet queue to be processed!
            packets_to_delete = []
            for packets in self._packet_queue:
                if packets.enqueue_time == current_tick:
                    # found a packet to enqueue in the event queue
                    status = True
                    # make this packet to delete
                    packets_to_delete.append(packets)
            # create an event based on this packet and then delete packtes from
            # the packet queue
            for packets in packets_to_delete:
                new_events_to_queue.append(EventV3(idx=packets._idx,
                                                   command="push",
                                                   buffer=self._sender,
                                                   time=packets.enqueue_time,
                                                   packet=packets))
                # [NO] Every push request is paired with a pop.
                # new_events_to_queue.append(EventV3(idx=packets._idx,
                #                                    command="pop",
                #                                    buffer=self._sender,
                #                                    time=packets.process_time+current_tick,
                #                                    packet=packets))
                
                self._packet_queue.remove(packets)
        if len(self._live_traffic_queue) > 0:
            # There are packets in the live queue.
            raise NotImplementedError
        
        return [status, new_events_to_queue]
        
    def set_packet_stream(self, packet_list: List[Packet],
                          source_delay: List[int]):
        assert(len(packet_list) == len(source_delay))
        # create a list of packets to be inserted as events.
        for idx, packets in enumerate(packet_list):
            # packets are queued as per as the ipd times. these will be popped
            # from the buffer after processing time
            packets.enqueue_time = source_delay[idx]
            self._packet_queue.append(packets)
    
    def add_packet_to_packet_stream(self, packet: Packet):
        raise NotImplementedError
        
    def insert_event(self, event: EventV3):
        if len(self.event_queue) == 0:
            self.event_queue = [event]
            
        elif len(self.event_queue) == 1:
            if self.event_queue[0]._time < event._time:
                self.event_queue.append(event)
            else:
                # shift the first event by one
                self.event_queue.append(self.event_queue[0])
                self.event_queue[0] = event
        else:
            # find the index where to insert the new event.
            idx = 0
            flag = False
            for events in self.event_queue:
                if events._time < event._time:
                    idx += 1
                elif events._time >= event._time and flag == False:
                    break
            self.event_queue.insert(idx, event)
    
    def pre_simulate(self):
        # We have to signal our simulator to insert a packet which will start
        # the communication.
        # we create one more packet so taht we can start the communication.
        # this is a pop packet.
        self.event_queue.append(EventV3(idx=-1,
                                    command="pop",
                                    buffer=self._sender,
                                    time=self._packet_queue[0].enqueue_time,
                                    packet=None))
        print()
    
    def simulate(self, length: int = None):
        """:params:
            length : amount of time in seconds to simulate
        """
        if length is not None:
            self._max_length = length
        print("Entering simulation until", self._max_length, "seconds!")
        
        for current_tick in range(max(0, int(self.event_queue[0]._time)), self._max_length * self._clock):
            # check if there are events at this tick
            monitor = self._check_for_events(current_tick)
            if monitor[0] == True:
                # this is an event but it cannot be queued into the event queue
                if len(self.event_queue) >= self._event_queue_limit or \
                        len(self.event_queue) + len(monitor[1]) >= self._event_queue_limit:
                    print("fatal: ran out of event queue slots!")
                    self.simulation_stats["status"] = False
                    self.simulation_stats["error"] = "out of event queue length"
                    break
                
                for events in monitor[1]:
                    self.insert_event(events)
            
            # else:
                # there is nothing to do in this cycle.
            # Do we have events to process in the event queue?
            if len(self.event_queue) == 0:
                # simulation is finished! there are no more events in the event
                # queue.
                break
                # are there new events to process?
            else:
                # process events
                # fatal condition will be when we have to process events in
                # the past!
                if current_tick > self.event_queue[0]._time:
                    print(current_tick, self.event_queue[0]._time, self.event_queue[0]._idx, self.event_queue[0]._command)
                    exit(-1)
                events_to_process = []
                for events in self.event_queue:
                    if events._time == current_tick:
                        events_to_process.append(events)
                for events in events_to_process:
                    if self._debug == True:
                        print(f"sim: {current_tick} found event {events._idx} with command {events._command}", end=" ")
                        # if events._command != "comm":
                        #     print(f"for packet {events._packet._idx}")
                        # else:
                        #     print()
                    event_monitor = events.process_event()
                    if event_monitor[0] == False:
                        self.simulation_stats["status"] = False
                        if events._command == "push":
                            self.simulation_stats["error"] = "overflow"
                        else:
                            self.simulation_stats["error"] = "i underflow"
                    self.event_queue.remove(events)
                if self.simulation_stats["status"] == False:
                    break
                
        if len(self.event_queue) > 0:
            # limit was reached but there were events left to process!
            self.simulation_stats["status"] = False
            self.simulation_stats["error"] = "couldn't process all events!"
        if len(self.event_queue) == 0 and len(self._packet_queue) > 0:
            # this is an underflow condition!
            self.simulation_stats["status"] = False
            self.simulation_stats["error"] = "o underflow"  
            print(self._packet_queue[0].enqueue_time)          
        # raise NotImplementedError
    
    def check_for_incoming_packet(self):
        raise NotImplementedError
    
    def init_data(self):
        # The simulator can only work when there are some initial packets
        raise NotImplementedError