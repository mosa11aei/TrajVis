import matplotlib.pyplot as plt

class DataHandler:    
    def __init__(self, network):
        self.network = None
        
        # set value
        self.network = network
        
    # NOTE: path1 is determined as the reconfigurable path if plotting meaningfuls    
    def plot_trp_comparison(self, path1, path2, generic_sensitivities, path1_name="Generic", path2_name="Current", plot_meaningfuls=False, system=1):
        # generate a plot using matplotlib from reconfig_rp, generic_rp, and time 1-8000
        x_axis = range(1, 8000)

        reconfigures = []
        reconfigures_time = []

        for reconfig in self.network.reconfigures:
            if len(path1) > reconfig["time"]:
                reconfigures_time.append(reconfig["time"])
                reconfigures.append(path1[reconfig["time"]])

        fig, ax = plt.subplots()
        ax.plot(x_axis, path1, label=path1_name)
        ax.plot(x_axis, path2, label=path2_name)
        
        if plot_meaningfuls:
            ax.scatter(reconfigures_time, reconfigures, label="Meaningful", color="green")
            
        ax.scatter(generic_sensitivities[0], generic_sensitivities[1], label="< rx_sensitivity", color="red")
        
        ax.legend()

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("E2E Receiver Power (dBm)")
        ax.set_title(f"E2E Receiver Power Comparison (System #{system})")