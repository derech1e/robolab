import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpl_interactions.ipyplot as iplt
import math
from math import sin, cos
from typing import Tuple
color_blue = ['darkblue', 'blue', 'cornflowerblue']
color_red = ['darkred', 'red', 'lightcoral']

# AXLE_LENGTH = 11
a = 10
# MAGIC_VALUE = 0.9945 
MAGIC_VALUE = 1
rot = 0.04884


path_rigth = np.genfromtxt('pathr.csv', delimiter=',')
path = np.genfromtxt('new_mr.csv', delimiter=',')
path_left = np.genfromtxt('pathl.csv', delimiter=',')




x = np.arange(0, len(path), 1)
#plot the path
# plt.plot(x[:], path[:,1], 'r', label='right')
# plt.plot(x[:], path[:,0], 'b', label='left')
# diff = path[:,0]-path[:,1]
# plt.plot(x[:], diff[:], 'b', label='differnece')

# plt.plot(path_left[:,0], path_left[:,1], 'b', label='left')


local_x_coordinat = 0
local_y_coordinat = 0
local_oriantation = 0
# ROT_TO_CM = 0.04884
# ROT_TO_CM = 0.05


def get_diff_in_cm(ROT_TO_CM, magic_value, tu1:Tuple[int,int], tu2:Tuple[int,int]) -> Tuple[float, float]:
    return((tu1[0]-tu2[0]) * ROT_TO_CM * magic_value, (tu1[1]-tu2[1]) * ROT_TO_CM / magic_value)

def update_position(motor_positions, AXLE_LENGTH, ROT_TO_CM, local_x_coordinat = 0, local_y_coordinat = 0, local_oriantation:float = 0):
    list_of_coords = []
    list_np = np.zeros((len(motor_positions), 2))
    alpha = 0
    for i in range(6, len(motor_positions)-6):
        dl, dr = get_diff_in_cm(ROT_TO_CM,MAGIC_VALUE, motor_positions[i+1], motor_positions[i])

        if dl == dr:
            alpha = 0
            s = dl
        else:
            alpha = (dr - dl) / AXLE_LENGTH
            s = AXLE_LENGTH * (dr + dl) / (dr - dl) * math.sin((dr - dl) / (2 * AXLE_LENGTH))


        if not alpha == np.nan:
            local_oriantation = local_oriantation + alpha
            # print(alpha)

            delta_x = s * (-1) * sin(local_oriantation)
            delta_y = s * cos(local_oriantation)


            local_x_coordinat += delta_x
            local_y_coordinat += delta_y

        list_of_coords.append((local_x_coordinat, local_y_coordinat))
        list_np[i] = [local_x_coordinat, local_y_coordinat]
    return list_of_coords
    # return list_np

# def get_x(a, RTC):
#     return update_position(path_left,a,RTC)[:,0]
# def get_y(a, RTC):
#     return update_position(path_left,a,RTC)[:,1]

#update and plot path

# for i in range(3):
#     right_turn = update_position(path_rigth,a,rot, local_oriantation=math.pi/2)
#     # left_turn = update_position(path_left,a,rot)
#     plt.plot([x[0] for x in right_turn], [x[1] for x in right_turn], color=color_blue[i], label=f'right {MAGIC_VALUE}')
#     # plt.plot([x[0] for x in left_turn], [x[1] for x in left_turn], color=color_red[i], label=f'left {MAGIC_VALUE}')
#     # MAGIC_VALUE += 0.0002



# turn_turn = update(path)

#plot left and right turn


# fig, ax = plt.subplots()
# controls = iplt.plot(get_x, get_y, a=(0,20,100), RTC=(0,0.1, 100), label="left")
# iplt.plot([x[0] for x in right_turn], [x[1] for x in right_turn], controls=controls, label="right")
# _ = plt.legend()

# plt.plot([x[0] for x in path_rigth], [x[1] for x in path_rigth], 'b', label='left')

def data_plot_odo():
    path_left_nml = np.genfromtxt('left_nml.csv', delimiter=',')
    path_right_nml = np.genfromtxt('right_nml.csv', delimiter=',')
    path_left_nmr = np.genfromtxt('left_nmr.csv', delimiter=',')
    path_right_nmr = np.genfromtxt('right_nmr.csv', delimiter=',')

    right_turn_nml = update_position(path_right_nml,a,rot, local_oriantation=math.pi/2)
    right_turn_nmr = update_position(path_right_nmr,a,rot, local_oriantation=math.pi/2)
    left_turn_nml = update_position(path_left_nml,a,rot)
    left_turn_nmr = update_position(path_left_nmr,a,rot)

    plt.plot([x[0] for x in right_turn_nml], [x[1] for x in right_turn_nml], color=color_blue[0], label=f'right_turn_nml')
    plt.plot([x[0] for x in right_turn_nmr], [x[1] for x in right_turn_nmr], color=color_blue[1], label=f'right_turn_nmr')
    plt.plot([x[0] for x in left_turn_nmr], [x[1] for x in left_turn_nmr], color=color_red[0], label=f'left_turn_nmr')
    plt.plot([x[0] for x in left_turn_nml], [x[1] for x in left_turn_nml], color=color_red[1], label=f'left_turn_nml')

    right_turn = update_position(path_rigth,a,rot, local_oriantation=math.pi/2)
    left_turn = update_position(path_left,a,rot)
    plt.plot([x[0] for x in right_turn], [x[1] for x in right_turn], color=color_blue[2], label=f'right vorher')
    plt.plot([x[0] for x in left_turn], [x[1] for x in left_turn], color=color_red[2], label=f'left vorher')

data_plot_odo()
plt.legend()
#show grid
plt.grid()
plt.show()

