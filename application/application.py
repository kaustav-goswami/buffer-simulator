# We need an application source that will generate packets with some timing
# parameters:

import math
import numpy as np

class Application:
    def __init__(self,
                 name: str,
                 traffic_type: str,
                 length: int,
                 params: dict):
        self._name = name
        self._type = traffic_type
        if self._type not in ["Exponential", "Uniform"]:
            raise NotImplementedError("Unknown traffic type!")
        self._length = length
        self._params = params

        self.traffic = self.generate_traffic()
        
        self.stats = {}
        self._calc_stats()
        
    def generate_traffic(self):
        if self._type == "Exponential":
            delay_values = np.random.default_rng().exponential(
                scale = self._params["lambda"],
                size = self._length
            )
        elif self._type == "Uniform":
            delay_values = np.random.uniform(
                self._params["low"],
                self._params["high"],
                size = self._length
            )
            # print(delay_values)
        # delay_values = np.sort(delay_values)
        return delay_values
    
    def get_traffic_delay(self):
        return self.traffic
    
    def _calc_stats(self):
        if self._type == "Exponential":
            # taken from wikipedia
            self.stats = {
                "min" : min(self.traffic),
                "max" : max(self.traffic),
                "mean" : float(1.0/self._params["lambda"]),
                "median" : float(math.log(2)/self._params["lambda"]),
                "mode" : 0.0,
                "variance" : float(1.0/math.pow(self._params["lambda"], 2))
            }
        elif self._type == "Uniform":
            # taken from wikipedia
            self.stats = {
                "min" : min(self.traffic),
                "max" : max(self.traffic),
                "mean" : float(
                    0.5 * (self._params["low"] + self._params["high"])),
                "median" : float(
                    0.5 * (self._params["low"] + self._params["high"])),
                "mode" : None, #self.get_traffic_delay()[random.randint(
                    # 0, self._length)],
                "variance" : float(1.0/12.0 * (
                    math.pow(self._params["high"] - self._params["low"], 2)))
            }

    def get_stats(self):
        return self.stats
