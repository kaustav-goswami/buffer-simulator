from application.application import Application
from application.encoder import EncoderV2
from buffer.buffer import Buffer
from event.event import Event, EventV2
from simulator.simulator import Simulator

from tester_functions import *
from util_functions import *

from typing import List

def test_driver():
    test_application()
    test_encoder()

###############################################################################
def main(ticks_resolution: int, sender: Buffer, receiver: Buffer,
         iterations: int, length = 32,
         live_traffic = {"value": False, "period": 0, "type": "exponential"},
         secret = None,
         debug = True):
    # Generate a random message.
    secret_message = secret[:length]
    # the simulator module needs to create packets based on this information
    # of the secret packet.
    encoder = EncoderV2(name="updated encoder", traffic_type="Exponential",
                        length=len(secret_message), params={"lambda": 1},
                        simulator_quantum=ticks_resolution,
                        message=secret_message)
    # the incorrect assumption that i had was that we pushg these packets into
    # the buffer and wait for process_time to pop. however, these packets are
    # already processed. we just need to push them into the buffer and then
    # start popping as per the interpacket arrival times.
    encoded_message = encoder.create_packets()
    # The simulator has to atleast simulate these packets. we can add a live
    # traffic source if we want too.
    print(encoder.get_stats())
    interpacket_arrival_times = np.sort(encoder.get_traffic_delay())
    
    interpacket_arrival_times = process_time_arrays(interpacket_arrival_times,
                                        ticks_resolution)
    print(interpacket_arrival_times)
    for packets in encoded_message:
        print(packets.process_time, end=". ")
    if debug == True:
        print("info: the user wants to send this message", secret_message)
        print("info: initializing an event queue to simulate this!")
    
    # The simulator will always have the first packet at time t = 0
    simulator = Simulator(clock_resolution=ticks_resolution,
                          buffers=[alice_buffer, bob_buffer],
                          debug=True)
    simulator.set_packet_stream(encoded_message, interpacket_arrival_times)
    if live_traffic["value"] == True:
        simulator.set_live_traffic(period=live_traffic["value"],
                                   traffic_type=live_traffic["type"])
    
    # We start the simulator here.
    simulator.pre_simulate()
    for i in range(iterations):
        simulator.simulate()
    print(simulator.simulation_stats)
    
###############################################################################

if __name__ == "__main__":
    # define all the global-like variables here i nthis area. we call main
    # after this. tell the simulator how precise you want it to be.
    # 1000 -> 1 ms.
    simulation_precision = int(1e3)
    message = create_random_message(size=187) #, quantum=simulation_precision)
    buffer_length = 20
    buffer_limit = 2
    alice_buffer = Buffer(buffer_name="alice buffer", buffer_size=buffer_length)
    bob_buffer = Buffer(buffer_name="bob buffer", buffer_size=200)
    iterations = 1

    
    main(ticks_resolution=simulation_precision, sender=alice_buffer,
         receiver=bob_buffer, iterations=iterations,
         secret=message)