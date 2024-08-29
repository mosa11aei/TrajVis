from TrajVis.components.defaults import *
import random

# Create random vector field. This is determined to be some wind pattern that could exist.

class WindMap:
    def create_windmap(self):
        for i in range(0, len(self._compass_matrix)):
            for j in range (0, len(self._compass_matrix)):
                self._create_compass(i, j)
                self._create_scalar(i, j)
        return

    def compass(self):
        return self._compass_matrix

    def scalar(self):
        return self._scalar_matrix

    def _create_compass(self, x, y):
        if x == 0 and y == 0:
            self._compass_matrix[x][y] = random.randrange(0, 359)

        wind_avg = 0
        wind_avg_contributions = 0

        for i in range(x-1, x+1):
            for j in range(y-1, y+1):
                if i < 0 or i > len(self._compass_matrix) or j < 0 or j > len(self._compass_matrix[0]):
                    continue
                if int(self._compass_matrix[i][j]) != 0:
                    # print(self._compass_matrix[i][j])
                    wind_avg += self._compass_matrix[i][j]
                    wind_avg_contributions += 1

        if(wind_avg_contributions == 0):
            self._compass_matrix[x][y] = random.randrange(0, 359)
            return 
            
        self._compass_matrix[x][y] = ((wind_avg + random.randrange(-WIND_COMPASS_DEVIATION, WIND_COMPASS_DEVIATION)))/wind_avg_contributions

    def _create_scalar(self, x, y):
        if x == 0 and y == 0:
            self._scalar_matrix[x][y] = random.uniform(0.5, 1)

        wind_avg = 0
        wind_avg_contributions = 0

        for i in range(x-1, x+1):
            for j in range(y-1, y+1):
                if i < 0 or i > len(self._scalar_matrix) or j < 0 or j > len(self._scalar_matrix[0]):
                    continue
                if int(self._scalar_matrix[i][j]) != 0:
                    # print(self._compass_matrix[i][j])
                    wind_avg += self._scalar_matrix[i][j]
                    wind_avg_contributions += 1

        if(wind_avg_contributions == 0):
            self._scalar_matrix[x][y] = random.uniform(0.5, 1)
            return 
            
        self._scalar_matrix[x][y] = ((wind_avg))/wind_avg_contributions

    def bound(self, border):
        for i in range(1, border-1):
            self._compass_matrix[i, :] = 0
            self._scalar_matrix[i, :] = len(self._compass_matrix)/4
            self._compass_matrix[len(self._compass_matrix) - i, :] = 180
            self._scalar_matrix[len(self._compass_matrix) - i, :] = len(self._compass_matrix)/4
            self._compass_matrix[:, i] = 90
            self._scalar_matrix[:, i] = len(self._compass_matrix)/4
            self._compass_matrix[:, len(self._compass_matrix) - i] = 270
            self._scalar_matrix[:, len(self._compass_matrix) - i] = len(self._compass_matrix)/4
    
    def __init__(self, x, y, step):
        # set to defaults
        self._dimensions = [0,0] # wind map dimensions x,y
        self.step = 1 # step between each point on the wind map
        self._compass_matrix = [] # matrix of compass directions per point on windmap (wind direction)
        self._scalar_matrix = [] # matrix of scalar value per point on windmap (wind strength)
        
        # actual values
        self._dimensions = [x, y]
        self.step = step

        xdir_w_steps = np.ceil(x/step)
        ydir_w_steps = np.ceil(y/step)
        
        self._compass_matrix = np.zeros((int(xdir_w_steps), int(xdir_w_steps)))
        self._scalar_matrix = np.zeros((int(ydir_w_steps), int(ydir_w_steps)))        