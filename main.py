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
def main(ticks_resolution: int,
         sender: Buffer,
         receiver: Buffer,
         iterations: int,
         length = 32,
         buffer_limit = 1,
         live_traffic = {"value": False, "period": 0, "type": "exponential"},
         secret = None,
         network_delay=0,
         traffic_type="exponential",
         debug = True):
    # Generate a random message.
    secret_message = secret[:length]
    # the simulator module needs to create packets based on this information
    # of the secret packet.
    encoder = None
    if traffic_type == "exponential":
        encoder = EncoderV2(name="updated encoder", traffic_type="Exponential",
                            length=len(secret_message), params={"lambda": 1},
                            simulator_quantum=ticks_resolution,
                            message=secret_message)
    elif traffic_type == "uniform":
        encoder = EncoderV2(name="updated encoder", traffic_type="Uniform",
                            length=len(secret_message), params={"low": 0,
                                                                "high": 1},
                            simulator_quantum=ticks_resolution,
                            message=secret_message)
    else:
        print("fatal! traffic type not supported!")
        exit(-1)
    # the incorrect assumption that i had was that we pushg these packets into
    # the buffer and wait for process_time to pop. however, these packets are
    # already processed. we just need to push them into the buffer and then
    # start popping as per the interpacket arrival times.
    encoded_message = encoder.create_packets()
    # The simulator has to atleast simulate these packets. we can add a live
    # traffic source if we want too.
    interpacket_arrival_times = np.sort(encoder.get_traffic_delay())
    # we might need to adjust the ticks_resolutions.
    adjusted_res = ticks_resolution
    if traffic_type == "uniform":
        adjusted_res = ticks_resolution * 10
    interpacket_arrival_times = process_time_arrays(interpacket_arrival_times,
                                        adjusted_res, traffic_type, length)

    if debug == True:
        print(encoder.get_stats())
        print(interpacket_arrival_times)
        for packets in encoded_message:
            print(packets.process_time, end=". ")
        print("info: the user wants to send this message", secret_message)
        print("info: initializing an event queue to simulate this!")
    
    # The simulator will always have the first packet at time t = 0
    simulator = Simulator(clock_resolution=ticks_resolution,
                          buffers=[alice_buffer, bob_buffer],
                          buffer_limit=buffer_limit,
                          network_delay=network_delay,
                          debug=False)
    
    # The packets sent by the application will be enqueued into the buffer at
    # interpacket arrival times. this will be simulated.
    simulator.set_packet_stream(encoded_message, interpacket_arrival_times)
    # This is for the bonus question. the user can generate live traffic
    # after every n time units. these will be enqueued by the simulator.
    if live_traffic["value"] == True:
        simulator.set_live_traffic(period=live_traffic["value"],
                                   traffic_type=live_traffic["type"])
    
    if debug == True:
        # Using this to debug whether out implementation is correct or not.
        print("info: expected times: ",
              encoded_message[buffer_limit - 1].enqueue_time , end = " ")
        s = encoded_message[buffer_limit - 1].enqueue_time
        for i in range(length):
            s +=  encoded_message[i].process_time
            print(s, end =  " ")
        print()
    
    # We start the simulator here. we add the first packet from the packet
    # stream so that the event queue in the simulator can start progressing.
    simulator.pre_simulate()
    # here goes nothing!
    simulator.simulate()
    # each simulation instance has it's own result set. time does not reset if
    # simulator object is not destroyed!
    return simulator.simulation_stats  
###############################################################################

if __name__ == "__main__":
    # define all the global-like variables here i nthis area. we call main
    # after this. tell the simulator how precise you want it to be.
    # 1000 -> 1 ms.
    simulation_precision = int(1e3)
    message = create_random_message(size=187) #, quantum=simulation_precision)
    buffer_length = 20
    buffer_limit_i = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    iterations = 100
    message_length = 32
    traffic_type = "exponential"
    network_delay = 0

    for buffer_limit in buffer_limit_i:
        overflow_count = 0
        underflow_count = 0
        for i in range(iterations):
            if buffer_limit < message_length:
                alice_buffer = Buffer(buffer_name="alice buffer",
                                      buffer_size=buffer_length)
                bob_buffer = Buffer(buffer_name="bob buffer", buffer_size=200) 
                sim = main(ticks_resolution=simulation_precision,
                           sender=alice_buffer,
                           receiver=bob_buffer,
                           iterations=iterations,
                           buffer_limit=buffer_limit,
                           secret=message,
                           network_delay=network_delay,
                           length=message_length,
                           traffic_type=traffic_type,
                           debug = False)
                
                if sim["status"] == False:
                    if "overflow" in sim["error"]:
                        overflow_count += 1
                    elif "underflow" in sim["error"]:
                        underflow_count += 1
        print("iterations", iterations,
            "B", buffer_length,
            "i", buffer_limit,
            "success",
            float(iterations - underflow_count - overflow_count) * 100.0/iterations,
            "underflow", float(underflow_count) * 100.0/iterations,
            "overflow", float(overflow_count) * 100.0/iterations)