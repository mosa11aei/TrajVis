from TrajVis.components.defaults import *
import random
from enum import Enum
from TrajVis.components.windmap import WindMap

# Balloon class
class BalloonStatus(Enum):
    ASCENT = 0, "Ascent"
    POP = 1, "Pop"
    FALL = 2, "Fall"

class Balloon:
    name = "Balloon"
    color = "red"
    
    coordinates = []
    altitudes = []
    current_xy = [0, 0] #0 = x, 1 = y, 2 = z
    current_v = [0, 0, 0] #0 = v_x, 1 = v_y, 2 = v_z
    current_alt = 0
    current_status = BalloonStatus.ASCENT
    attitudes = []
    
    current_time = 0
    popped_at = 0
    pop_point = []

    plt_x = []
    plt_y = []

    wm = WindMap(1, 1, 1)
    antenna = 0
    
    def __init__(self, wm, name, color):
        self.wm = wm
        self.name = name
        self.color = color
        self.current_status = BalloonStatus.ASCENT
        self.altitudes = []
        self.current_v = [0, 0, 0]
        self.coordinates = []
        self.current_alt = 0
        self.attitudes = []
        return

    def _calculate_attitude(self):
        if len(self.attitudes) == 0:
            self.attitudes.append([0,0])
        else:
            old_attitude = np.array(self.attitudes[len(self.attitudes)-1])
            attitude_modifier = np.array([random.uniform(-2, 3), random.uniform(-2, 3)])
            self.attitudes.append(np.add(old_attitude, attitude_modifier) % 360)

    def distance_traveled(self, time):
        total_distance = 0;
        if time == False:    
            for coord in self.coordinates:
                total_distance += np.sqrt(coord[0]**2 + coord[1]**2 + coord[2]**2)
        else:
            for i in range(time[0], time[1]):
                coord = self.coordinates[i]
                total_distance += np.sqrt(coord[0]**2 + coord[1]**2 + coord[2]**2)
                
        return total_distance

    def diagnostic(self):
        print("Balloon name: ", self.name)
        print("Balloon status: ", self.current_status)
        print("Balloon altitude: ", self.current_alt)
        print("Balloon z-velocity: ", self.current_v[2])
        print("Balloon distance traveled: ", self.distance_traveled(time=False))
        return

    def set_start_pos(self, x, y):
        mx_lim = -len(self.wm.compass())*self.wm.step/2
        x_lim = len(self.wm.compass())*self.wm.step/2
        my_lim = -len(self.wm.compass()[0])*self.wm.step/2
        y_lim = len(self.wm.compass()[0])*self.wm.step/2

        if x < mx_lim or x > x_lim or y < my_lim or y > y_lim:
            raise Exception("x and/or y out of bounds")
        else:
            self.current_xy = [x, y, 0]
            self.coordinates = [self.current_xy]
            self.plt_x = [x]
            self.plt_y = [y]

    def _set_alt(self):
        if(len(self.altitudes)) == 0:
            self.current_alt = 0
            self.altitudes.append(self.current_alt)
            self.current_v[2] = np.abs(random.uniform(6, 8)) # given historical NEBP data
        elif self.current_status == BalloonStatus.ASCENT:
            self.current_alt += self.current_v[2] * TICK_TIME_SCALE
            self.altitudes.append(self.current_alt + random.uniform(0, 3))
            # self.current_v[2] += random.uniform(-0.1, 0.1) # given historical NEBP data
        elif self.current_status == BalloonStatus.POP:
            self.current_v[2] = random.uniform(-23, -21) # given historical NEBP data
            self.current_alt += self.current_v[2] * TICK_TIME_SCALE
            self.altitudes.append(self.current_alt)
            self.popped_at = self.current_time
        elif self.current_status == BalloonStatus.FALL:
            self.current_v[2] = after_pop_velocity(self.current_time, self.popped_at) + random.uniform(-3, 1)
            self.current_alt += self.current_v[2] * TICK_TIME_SCALE
            self.altitudes.append(self.current_alt)
        self.current_time += 0.5;

    def tick(self):
        if self.current_status == BalloonStatus.POP:
            self.current_status = BalloonStatus.FALL
            self.pop_point = [self.plt_x[len(self.plt_x)-1], self.plt_y[len(self.plt_y)-1]]
        if self.current_alt > 95000 and self.current_status == BalloonStatus.ASCENT:
            self.current_status = BalloonStatus.POP
            print(self.name, " popped at ", self.current_time)

        if np.ceil(self.plt_x[len(self.plt_x)-1]) > len(self.wm.compass())*self.wm.step/2 or \
        np.floor(self.plt_x[len(self.plt_x)-1]) < -len(self.wm.compass())*self.wm.step/2 or \
        np.ceil(self.plt_y[len(self.plt_y)-1]) > len(self.wm.compass())*self.wm.step/2 or \
        np.floor(self.plt_y[len(self.plt_y)-1]) < -len(self.wm.compass())*self.wm.step/2:
            return 0

        if self.current_alt <= 0 and self.current_status == BalloonStatus.FALL:
            print(self.name, " hit the ground at time t=", self.current_time)
            return 0
            
        act_x, act_y = point_to_matrix_coord(self.plt_x[len(self.plt_x)-1], self.plt_y[len(self.plt_y)-1], self.wm.compass(), self.wm.step)
        # print(act_x, act_y)
        avg_vec = np.array([0, 0])
        avg_vec_contributors = 0
        
        for i in range(act_x - 1, act_x + 1):
            for j in range(act_y - 1, act_y + 1):
                if i < 0 or i > len(self.wm.compass())-1 or j < 0 or j > len(self.wm.compass()[0])-1:
                    continue
                else:
                    if int(self.wm.compass()[i][j]) != 0 and int(np.ceil(self.wm.scalar()[i][j])) != 0:
                        vec = np.array([np.cos(self.wm.compass()[i][j] * np.pi/180), np.sin(self.wm.compass()[i][j] * np.pi/180)])
                        vec = vec * self.wm.scalar()[i][j]
                        #print(vec)
                        avg_vec = np.add(avg_vec, vec)
                        avg_vec_contributors += 1

        random_vec = np.array([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])
        avg_vec = np.add(avg_vec, random_vec)
        if avg_vec_contributors != 0:
            avg_vec = avg_vec / (avg_vec_contributors+1);

        self.plt_x.append(self.plt_x[len(self.plt_x)-1] + avg_vec[0])
        self.plt_y.append(self.plt_y[len(self.plt_y)-1] + avg_vec[1])

        # update balloon info
        self._set_alt()
        self._calculate_attitude()
        self.coordinates.append([self.plt_x[len(self.plt_x)-1] + avg_vec[0], self.plt_y[len(self.plt_y)-1] + avg_vec[1], self.current_alt])
        return 1

    def add_antenna(self, antenna):
        self.antenna = antenna