"""
Thank you Daniil Voloshin (Github: @gorsheep) for this code.

Calculate data rate using link margin parameters. This allows us to estimate the data rate given two nodes at a given time, providing a view of how the data rate can improve/decline over the time of simulation (flight).
"""

import numpy as np
from scipy.optimize import fsolve
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


def calculate_link_margin(link_params: LinkBudgetParams, data_rate: float) -> float:

    P_t_db = 10 * np.log10(link_params.transmitter_power)
    EIRP = P_t_db + link_params.transmitter_antenna_gain - link_params.transmitter_line_loss
    FSL = link_params.freespace_loss
    path_losses = link_params.transmitter_line_loss + FSL + link_params.atmospheric_loss + link_params.reciever_input_loss + link_params.pointing_loss
    P_total = EIRP + link_params.receiver_antenna_gain - path_losses
    T_N = (10**(link_params.receiver_NF/10) - 1)*290
    T_A = 290
    T = 10 * np.log10(T_N+T_A)
    G_T = link_params.receiver_antenna_gain - T
    C_N0 = P_total + G_T - link_params.receiver_antenna_gain + 228.6
    R_e = data_rate / link_params.modulation_rate / link_params.computer_imp_efficiency
    Eb_N0_pred = C_N0 - 10 * np.log10(R_e)
    M_p = Eb_N0_pred - link_params.Eb_N0_req
    
    return M_p

def data_rate_for_desired_link_margin(link_params: LinkBudgetParams, desired_link_margin: float) -> float:
    
    # Define a function to represent the difference between current and desired Eb/N0
    def margin_residual(data_rate):
        current_margin = calculate_link_margin(link_params, data_rate)
        return current_margin - desired_link_margin
    
    # Find the data rate that satisfies the residual function
    initial_guess = 1e6  # Starting with a guess of 1 Mbps
    data_rate_solution = fsolve(margin_residual, initial_guess)

    return data_rate_solution[0]