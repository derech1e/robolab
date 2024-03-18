
from __future__ import print_function
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
import mpl_interactions.ipyplot as iplt
import math
from math import sin, cos

from os import listdir
from os.path import isfile, join






from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.pyplot as plt






def series(dots, colr):
    a,b=[],[]
    for i in range(dots):
        a.append(random.randint(1,100))
        b.append(random.randint(1,100))
    plt.scatter(a,b, c=colr)
    return()
interact(series, dots=(1,100,1), colr=["red","orange","brown"]);
# x = np.linspace(0, np.pi, 100)
# tau = np.linspace(0.5, 10, 100)
#
# def f1(x, tau, beta):
#     return np.sin(x * tau) * x * beta
# def f2(x, tau, beta):
#     return np.sin(x * beta) * x * tau
#
#
# fig, ax = plt.subplots()
# controls = iplt.plot(x, f1, tau=tau, beta=(1, 10, 100), label="f1")
# iplt.plot(x, f2, controls=controls, label="f2")


#----------- Constants ----------------
a = 10
# MAGIC_VALUE = 0.9945 
MAGIC_VALUE = 1
rot = 0.04884


#----------- Odometry function ----------------

def get_diff_in_cm(ROT_TO_CM, magic_value, tu1:Tuple[int,int], tu2:Tuple[int,int]) -> Tuple[float, float]:
    return((tu1[0]-tu2[0]) * ROT_TO_CM * magic_value, (tu1[1]-tu2[1]) * ROT_TO_CM / magic_value)


drive_data = np.genfromtxt('data/test1/path.csv', delimiter=',')

def update_position( AXLE_LENGTH, ROT_TO_CM, local_x_coordinat = 0, local_y_coordinat = 0, local_oriantation:float = 0):
    list_of_coords = []
    list_np = np.zeros((len(drive_data), 2))
    alpha = 0
    for i in range(6, len(drive_data)-6):
        dl, dr = get_diff_in_cm(ROT_TO_CM,MAGIC_VALUE, drive_data[i+1], drive_data[i])

        if dl == dr:
            alpha = 0
            s = dl
        else:
            alpha = (dr - dl) / AXLE_LENGTH
            s = AXLE_LENGTH * (dr + dl) / (dr - dl) * math.sin((dr - dl) / (2 * AXLE_LENGTH))


        local_oriantation = local_oriantation + alpha
            # print(alpha)

        delta_x = s * (-1) * sin(local_oriantation)
        delta_y = s * cos(local_oriantation)


        local_x_coordinat += delta_x
        local_y_coordinat += delta_y

        list_of_coords.append((local_x_coordinat, local_y_coordinat))
        list_np[i] = [local_x_coordinat, local_y_coordinat]
    print(list_np)

    return np.array(list_np)


def plot_coords_2(AXLE_LENGTH, ROT_TO_CM):
    data = update_position(AXLE_LENGTH, ROT_TO_CM)
    plt.plot(data[:,0], data[:,1])


# import data:

def update_y( AXLE_LENGTH, ROT_TO_CM, local_x_coordinat = 0, local_y_coordinat = 0, local_oriantation:float = 0):
    return update_position( AXLE_LENGTH, ROT_TO_CM, local_x_coordinat, local_y_coordinat, local_oriantation)[:,0]
    # return [i[1] for i in update_position( AXLE_LENGTH, ROT_TO_CM, local_x_coordinat, local_y_coordinat, local_oriantation)]

def update_x( AXLE_LENGTH, ROT_TO_CM, local_x_coordinat = 0, local_y_coordinat = 0, local_oriantation:float = 0):
    return update_position(AXLE_LENGTH, ROT_TO_CM, local_x_coordinat, local_y_coordinat, local_oriantation)[:,1]
    # return [i[0] for i in update_position( AXLE_LENGTH, ROT_TO_CM, local_x_coordinat, local_y_coordinat, local_oriantation)]
    


#----------- Plotting functions ----------------
def plot_difference(path:np.ndarray):
    x = np.arange(0, len(path), 1)

    plt.plot(x[:], path[:,1], 'r', label='right')
    plt.plot(x[:], path[:,0], 'b', label='left')

    diff = path[:,0]-path[:,1]
    plt.plot(x[:], diff[:], 'b', label='differnece')


#----------- Plotting coordinates ----------------
def plot_coords(): #path:np.ndarray
    #eddid path name
    fig, ax = plt.subplots()

    data_list = [f for f in listdir('data/test1') if isfile(join('data/test1', f))]
    for data in data_list:
        drive_data = np.genfromtxt('data/test1/'+data, delimiter=',')
        # print(update_y(drive_data, 11, 0.005))
        

        controls = iplt.plot(update_x, update_y, AXLE_LENGTH=np.linspace(5,20,100), ROT_TO_CM=np.linspace(0.004, 0.006, 100), label="f1")
        iplt.plot(update_x, update_y, controls=controls, label="f2")


    pass


interact(plot_coords_2, AXLE_LENGTH=np.linspace(5,20,100), ROT_TO_CM=np.linspace(0.004, 0.006, 100))
#
# plot_coords()
#
# _ = plt.legend()
plt.show()

