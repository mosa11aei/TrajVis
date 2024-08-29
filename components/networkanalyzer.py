from TrajVis.components.defaults import *
import random
from enum import Enum
import matplotlib.pyplot as plt
from TrajVis.functions.var_datarate import data_rate_for_desired_link_margin
from typing import NamedTuple

class LinkBudgetParams(NamedTuple):
    transmitter_frequency: float    # in GHz
    transmitter_power: float        # in W
    transmitter_antenna_gain: float # in dB
    transmitter_line_loss: float    # in dB
    distance: float                 # in km
    freespace_loss: float           # in dB
    atmospheric_loss: float         # in dB
    receiver_antenna_gain: float    # in dB
    reciever_input_loss: float      # in dB
    pointing_loss: float            # in dB
    receiver_NF: float              # in dB
    modulation_rate: float          # dimless
    computer_imp_efficiency: float  # dimless
    Eb_N0_req: float                # in dB
    link_margin_req: float          # in dB

class RadioType(Enum):
    Rx = 0, "Transmit"
    Tx = 1, "Receive"
    TwoWay = 2, "Two Way"

class Antenna:
    radio_type = RadioType.TwoWay
    hpbw = 0 # half power beam width angle (https://www.exfo.com/en/resources/glossary/hpbw/), degrees
    gain = 0 # in dB
    name = ""
    freq = 0 # in Mhz
    sensitvity = 0 # in dBm
    transmit_power = 0 # in dBm
    
    def __init__(self, radio_type, hpbw, gain, name, freq, sensitivity, tpwr):
        self.radio_type = radio_type
        self.hpbw = hpbw
        self.gain = gain # in dBi
        self.name = name
        self.freq = freq * 1e6
        self.sensitivity = sensitivity
        self.transmit_power = tpwr
        
class NetworkAnalyzer:
    _balloons = []

    def show_pointing(self, time, *args):
        _dir_plot = plt.figure().add_subplot(projection='3d')
        
        for balloon in args:
            attitude_vector = spherical_to_vector(balloon.attitudes[time])
            plt.quiver(0, 0, 0, attitude_vector[0], attitude_vector[1], attitude_vector[2], length=1, normalize=True, label=balloon.name, color=balloon.color)

        _dir_plot.set_xlim(-1, 1)
        _dir_plot.set_ylim(-1, 1)
        _dir_plot.set_zlim(-1, 1)
        plt.title("Direction of antenna of all balloons")
        plt.legend()
        plt.show()

    # b1 is balloon 1, b2 is balloon 2
    def _calculate_distance(self, time, b1, b2):
        if time > len(b1.coordinates)-1 or time > len(b2.coordinates)-1:
            return 10000
        xyz_b1 = b1.coordinates[time]
        xyz_b2 = b2.coordinates[time]

        distance = np.sqrt((xyz_b1[0] - xyz_b2[0])**2 + (xyz_b1[1] - xyz_b2[1])**2 + (xyz_b1[2] - xyz_b2[2])**2)
        return distance

    def _free_space_loss(self, time, b1, b2):
        # if not isinstance(b1.antenna, Antenna):
        #     raise Exception("Antenna not attached to balloon", b1.name)
        # if not isinstance(b2.antenna, Antenna):
        #     raise Exception("Antenna not attached to balloon", b2.name)

        distance_between = self._calculate_distance(time, b1, b2)

        if b1.antenna.freq != b2.antenna.freq:
            return print("Balloon", b1.name, "and Balloon", b2.name, "are not on the same frequency")

        # thanks SMAD
        fspl = 20*np.log10(distance_between) + 20*np.log10(b1.antenna.freq) + 20*np.log10((4*np.pi)/SPEED_OF_LIGHT) - b1.antenna.gain - b2.antenna.gain
        return fspl

    def _pointing_loss(self, time, b1, b2):
        # if not isinstance(b1.antenna, Antenna):
        #     print(b1.antenna)
        #     raise Exception("Antenna not attached to balloon", b1.name)
        # if not isinstance(b2.antenna, Antenna):
        #     print(b2.antenna)
        #     raise Exception("Antenna not attached to balloon", b2.name)

        if time > len(b1.attitudes)-1 or time > len(b2.attitudes)-1:
            pl = 100
            return pl

        b1_att = spherical_to_vector(b1.attitudes[time])
        b2_att = spherical_to_vector(b2.attitudes[time])
            
        dot_product = np.dot(b1_att, b2_att)
        angle = np.arccos(dot_product) * 180/np.pi
        
        # thanks https://www.fxsolver.com/browse/formulas/Loss+due+to+Antenna+Misalignment
        pl = 12 * (angle/b1.antenna.hpbw) ** 2
        return pl

    def rp_all(self, time):
        network_graph = nx.DiGraph()
        for tx in self._balloons:
            for rx in self._balloons:
                if tx == rx:
                    continue
                rp = tx.antenna.transmit_power + tx.antenna.gain + rx.antenna.gain - self._pointing_loss(time, tx, rx) - self._free_space_loss(time, tx, rx)
                print("[Tx] Balloon", tx.name, "--> [Rx] Balloon", rx.name)
                print("\t", rp, "dBm, receiver power")
                print("\t", self._calculate_distance(time, tx, rx), "m distance")
                if rp < rx.antenna.sensitivity:
                    print("\t [!!] Wp LESS THAN SENSITIVITY")
                else:
                    network_graph.add_edge(tx.name, rx.name, weight=rp)

    def rp(self, time, tx, rx):
        rp = tx.antenna.transmit_power + tx.antenna.gain + rx.antenna.gain - self._pointing_loss(time, tx, rx) - self._free_space_loss(time, tx, rx)
        return rp
    
    # variable data rate calculation
    def data_rate(self, tx, rx, time, desired_link_margin):
        params = LinkBudgetParams(
            transmitter_frequency = tx.antenna.freq / 1e9,
            transmitter_power = (10 ** (tx.antenna.transmit_power/10))/1000,          
            transmitter_antenna_gain = tx.antenna.gain,  
            transmitter_line_loss = 0.0001,
            distance = self._calculate_distance(time, tx, rx),
            freespace_loss = self._free_space_loss(time, tx, rx),                
            atmospheric_loss = 0.05,
            receiver_antenna_gain = rx.antenna.gain,   
            reciever_input_loss = 0.0001,
            pointing_loss = self._pointing_loss(time, tx, rx),    
            receiver_NF = 5,                
            modulation_rate = 0.8,          
            computer_imp_efficiency = 0.95, 
            Eb_N0_req = 5.41,      
            link_margin_req = 3.0         
        )
                
        return data_rate_for_desired_link_margin(params, desired_link_margin)        
        
    def __init__(self, *args):
        self._balloons = []
        for balloon in args:
            self._balloons.append(balloon)