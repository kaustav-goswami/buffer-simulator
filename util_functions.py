import numpy as np
import random

def convert_to_quantum(time, quantum):
    # time is in seconds.
    return int(time * quantum)

def process_time_arrays(time_array, quantum):
    ret_times = np.zeros(time_array.shape)
    for idx, time in enumerate(time_array):
        ret_times[idx] = convert_to_quantum(time, quantum)
    return ret_times

def create_random_message(size):
    message = []
    for i in range(size):
        message.append(int(random.randint(0, int(1e10)) % 2 == 0))
    return message