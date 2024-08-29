from TrajVis.components.defaults import *
import matplotlib.pyplot as plt

class PlotHelper:
    def __init__(self, wm):
        # set default values
        self._compass_matrix = []
        self._scalar_matrix = []
        self.step = 1
        self._plot = plt
        self._plot_balloons = plt

        self.plt_x = np.zeros(1)
        self.plt_y = np.zeros(1)
        self.plt_vec_x = np.zeros(1)
        self.plt_vec_y = np.zeros(1)
        
        # actual values
        self._compass_matrix = wm.compass()
        self._scalar_matrix = wm.scalar()
        self.step = wm.step

        self.plt_x = np.zeros(np.power(len(self._compass_matrix), 2))
        self.plt_y = np.zeros(np.power(len(self._compass_matrix), 2))
        self.plt_vec_x = np.zeros(np.power(len(self._compass_matrix), 2))
        self.plt_vec_y = np.zeros(np.power(len(self._compass_matrix), 2))

    def _calculate_vector(self, i, show_scale):
        row_from_i = int(np.floor(i/len(self._compass_matrix)))
        col_from_i = i % len(self._compass_matrix[0])

        self.plt_vec_y[i] = np.sin(self._compass_matrix[row_from_i][col_from_i] * np.pi/180)
        self.plt_vec_x[i] = np.cos(self._compass_matrix[row_from_i][col_from_i] * np.pi/180)

        if(show_scale):
            self.plt_vec_y[i] = self.plt_vec_y[i] * self._scalar_matrix[row_from_i][col_from_i]
            self.plt_vec_x[i] = self.plt_vec_x[i] * self._scalar_matrix[row_from_i][col_from_i]

    def populate(self, show_scale):
        step_ctr_x = -1
        for i in range(0, np.power(len(self._compass_matrix), 2)):
            step_ctr_y = i % len(self._compass_matrix)
            if not step_ctr_y:
                step_ctr_x += 1
            self.plt_x[i] = -len(self._compass_matrix)*self.step/2 + self.step*step_ctr_x
            self.plt_y[i] = -len(self._compass_matrix)*self.step/2 + self.step*step_ctr_y

            self._calculate_vector(i, show_scale)

    def get_plot(self):
        return self._plot

    def plot(self):
        self._plot = plt.figure()
        plt.quiver(self.plt_x, self.plt_y, self.plt_vec_x, self.plt_vec_y, color='b', units='xy', scale=1)
        plt.xlim(-len(self._compass_matrix)*self.step/2 - 1, len(self._compass_matrix)*self.step/2 +1)
        plt.ylim(-len(self._compass_matrix[0])*self.step/2 -1, len(self._compass_matrix)*self.step/2 +1)
        plt.title("Wind Map")

    def plot_balloons(self, *args):
        self._plot_balloons = plt.figure()
        plt.quiver(self.plt_x, self.plt_y, self.plt_vec_x, self.plt_vec_y, color='gray', units='xy', scale=1)
        plt.xlim(-len(self._compass_matrix)*self.step/2 - 1, len(self._compass_matrix)*self.step/2 +1)
        plt.ylim(-len(self._compass_matrix[0])*self.step/2 -1, len(self._compass_matrix)*self.step/2 +1)
        
        for balloon in args:
            plt.plot(balloon.plt_x, balloon.plt_y, color=balloon.color, label=balloon.name)
            plt.plot(balloon.plt_x[0], balloon.plt_y[0], 'g*')
            print(balloon.pop_point[0], balloon.pop_point[1])
            plt.plot(balloon.pop_point[0], balloon.pop_point[1], 'bx')
            plt.plot(balloon.plt_x[len(balloon.plt_x)-1], balloon.plt_y[len(balloon.plt_y)-1], 'r*')
            
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Balloon Trajectory on WM") 
        plt.legend()

    def zoom_in(self, x, y):
        plt.xlim(x-len(self._compass_matrix)/10, x+len(self._compass_matrix)/10)
        plt.ylim(y-len(self._compass_matrix)/10, y+len(self._compass_matrix)/10)
        plt.title(f"Wind Map at ({x}, {y})")
            