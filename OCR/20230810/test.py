import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from multiprocessing import Process, Queue
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
import matplotlib.pyplot as plt
import easyocr
import torch
import cv2
import time
import Levenshtein
import numpy as np
from datetime import datetime
import cv2
import json

from skimage.segmentation import slic
from skimage.color import label2rgb

def remove_uniform_colors(image, background, threshold=20):
    diff = np.ptp(image, axis=-1)
    mask = diff < threshold
    image[mask] = background
    return image


name_list = ["athletechyinzcam", "Albert", "Allen", "Bert", "Bob", "Cecil", "Clarence", "Elliot", "Elmer", "Ernie", "Eugene", "Fergus", "Ferris", "Frank", "Frasier", "Fred", "George", "Graham", "Harvey", "Irwin", "Larry", "Lester", "Marvin", "Neil", "Niles", "Oliver", "Opie", "Ryan", "Toby", "Ulric", "Ulysses", "Uri", "Waldo", "Wally", "Walt", "Wesley", "Yanni", "Yogi", "Yuri", "Alfred", "Bill", "Brandon", "Calvin", "Dean", "Dustin", "Ethan", "Harold", "Henry", "Irving", "Jason", "Jenssen", "Josh", "Martin", "Nick", "Norm", "Orin", "Pat", "Perry", "Ron", "Shawn", "Tim", "Will", "Wyatt", "Adam", "Andy", "Chris", "Colin", "Dennis", "Doug", "Duffy", "Gary", "Grant", "Greg", "Ian", "Jerry", "Jon", "Keith", "Mark", "Matt", "Mike", "Nate", "Paul", "Scott", "Steve", "Tom", "Yahn", "Adrian", "Bank", "Brad", "Connor", "Dave", "Dan", "Derek", "Don", "Eric", "Erik", "Finn", "Jeff", "Kevin", "Reed", "Rick", "Ted", "Troy", "Wade", "Wayne", "Xander", "Xavier", "Brian", "Chad", "Chet", "Gabe", "Hank", "Ivan", "Jim", "Joe", "John", "Tony", "Tyler", "Victor", "Vladimir", "Zane", "Zim", "Cory", "Quinn", "Seth", "Vinny", "Arnold", "Brett", "Kurt", "Kyle", "Moe", "Quade", "Quintin", "Ringo", "Rip", "Zach", "Cliffe", "Crusher", "Gunner", "Minh", "Garret", "Phoenix", "Ridgway", "Rock", "Shark", "Steel", "Stone", "Wolf", "Vitaliy", "Zed" ]
image = cv2.imread('1691177512.8965952frame.png')
height, width, _ = image.shape

# reader = easyocr.Reader(['en'], gpu=True)
part5_kill1 = image[int(100 * height / 1440):int(143 * height / 1440),
              int(2000 * width / 2560):int(2550 * width / 2560)]
part5_kill2 = image[int(147 * height / 1440):int(190 * height / 1440),
              int(2000 * width / 2560):int(2550 * width / 2560)]
part5_kill3 = image[int(194 * height / 1440):int(237 * height / 1440),
              int(2000 * width / 2560):int(2550 * width / 2560)]
part5_kill4 = image[int(241 * height / 1440):int(284 * height / 1440),
              int(2000 * width / 2560):int(2550 * width / 2560)]
part5_kill5 = image[int(288 * height / 1440):int(331 * height / 1440),
              int(2000 * width / 2560):int(2550 * width / 2560)]

# part5_concate = np.concatenate((part5_kill1, part5_kill2, part5_kill3, part5_kill4, part5_kill5),
#                             axis=0)  # vertical

part5_list = [part5_kill1, part5_kill2, part5_kill3, part5_kill4, part5_kill5]
reader = easyocr.Reader(['en'])  # Initialize the EasyOCR reader with desired languages

for i in range(1):
    # Convert the image to grayscale
    part5_list[1] = cv2.cvtColor(part5_list[1], cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(part5_list[1], np.array([0, 50, 50]), np.array([10, 255, 255]))
    mask2 = cv2.inRange(part5_list[1], np.array([160, 50, 50]), np.array([100, 255, 255]))
    mask3 = cv2.bitwise_or(mask1, mask2)
    contours, _ = cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    part5_list[1] = part5_list[1][y:y+h, x:x+w]
    part5_list[1] = cv2.cvtColor(part5_list[1], cv2.COLOR_HSV2BGR)


    gray_image = cv2.cvtColor(part5_list[1], cv2.COLOR_BGR2GRAY)

    # Apply a simple binary threshold
    threshold_value = 200  # Adjust this value as needed
    _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw rectangles around detected regions

    count = 0
    boundry_list = []

    for contour in contours:
        # print(len(contour))
        x, y, w, h = cv2.boundingRect(contour)

        print(w, " ", h, " ", len(contour))
        # print(len(contour))
        if w > 15 and len(contour) > 20 and h > 10:
            boundry_list.append([x, y, w, h])
            # cv2.rectangle(part5_list[0], (x, y), (x + w, y + h), (0, 255, 0), 2)
            part5_list[1][y:y + h, x:x + w] = (255, 255, 255)

            count = count + 1
        if count >= 2:
            new_h = max(boundry_list[count-2][3], boundry_list[count-1][3])
            new_w = max(boundry_list[count-2][0], boundry_list[count-1][0]) - min(boundry_list[count-1][0], boundry_list[count-2][0]) + boundry_list[count-2][2]
            new_x = min(boundry_list[count-2][0], boundry_list[count-1][0])
            new_y = min(boundry_list[count-2][1], boundry_list[count-1][1])
            part5_list[1][new_y:new_y + new_h, new_x:new_x + new_w] = (255, 255, 255)
    # Display or save the result
    cv2.imshow('Detected Green Boxes', part5_list[1])
    # cv2.imwrite('picture3.png', part5_list[0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    results = reader.readtext(part5_list[1], allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ',
                              width_ths=0.7, paragraph=True)
    print(results)
    # killers = []
    # killees = []
    #
    # # background = image[3, 275, :]
    # # part5_list[i] = remove_uniform_colors(part5_list[i], background)
    # # cv2.imwrite("newpart.png", part5_list[0])
    # results = reader.readtext(image, allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ',
    #                           width_ths=0.4, paragraph=True)
    # print(results)
    # # text = ' '.join([result[1] for result in results])
    #
    # m = 0
    #
    # #results = [result for result in results if result[2] >= 0.2]
    # for result in results:
    #     # print(ctime, " ", result[1])
    #     if len(results) == 0:
    #         continue
    #
    #     if len(results) == 1:
    #         splitlist = result[1].split()
    #
    #         n = 0
    #         for split in splitlist:
    #             if (len(split) <= 3):
    #                 continue
    #             if n % 2 == 0:
    #                 killers.append(split)
    #             if n % 2 == 1:
    #                 killees.append(split)
    #
    #             n = n + 1
    #
    #
    #     if len(results) == 2:
    #         if (len(result[1]) <= 5):
    #             continue
    #
    #         if m % 2 == 0:
    #             killers.append(result[1])
    #
    #         if m % 2 == 1:
    #             killees.append(result[1])
    #
    #     if len(results) == 3:
    #
    #         if (len(result[1]) <= 5):
    #             continue
    #
    #         if m == 0 or m == 1:
    #             killers.append(result[1])
    #
    #         if m == 2:
    #             killees.append(result[1])
    #
    #     m = m + 1
    #
    # closest_string_killer = ''
    # closest_string_killee = ''
    # updated_killers = []
    # updated_killees = []
    #
    # concate_killers = ""
    # concate_killees = ""
    # for killer in killers:
    #
    #     split_killers = killer.split()
    #
    #     count = 0
    #
    #     for split_killer in split_killers:
    #         if split_killer.lower() == 'bot':
    #             continue
    #
    #         if len(split_killer) <= 3:
    #             continue
    #         distances = [Levenshtein.distance(split_killer, target) for target in name_list]
    #         min_distance_index = distances.index(min(distances))
    #         closest_string_killer = name_list[min_distance_index]
    #         # closest_string_killer = find_closest_name(split_killer, name_list)
    #         count = count + 1
    #
    #         if count == 2:
    #             concate_killers += " and "
    #             concate_killers += closest_string_killer
    #             break
    #
    #         concate_killers = closest_string_killer
    #
    #     updated_killers.append(concate_killers)
    # print(updated_killers)
    #
    # for killee in killees:
    #     split_killees = killee.split()
    #     for split_killee in split_killees:
    #         if split_killee.lower() == 'bot':
    #             continue
    #         if len(split_killee) <= 3:
    #             continue
    #         distances = [Levenshtein.distance(split_killee, target) for target in name_list]
    #         min_distance_index = distances.index(min(distances))
    #         closest_string_killee = name_list[min_distance_index]
    #         #closest_string_killee = find_closest_name(split_killee, name_list)
    #         concate_killees = closest_string_killee
    #         updated_killees.append(closest_string_killee)
    #
    # print(updated_killees)


        # # Step 1: Open the JSON file
# with open('data.json', 'r') as file:
#     # Step 2: Read the contents of the file
#     data = file.read()
#
# # Step 3: Parse the JSON data into a Python data structure (e.g., dictionary, list)
#
# data_dict = json.loads(data)
#
# print(data_dict)
# hp_ac_values = [value['hp_ac'] for value in data_dict.values()]
# player_kills = [value['player_kill_other'] for value in data_dict.values()]
# player_death = [value['player_get_killed'] for value in data_dict.values()]
# hp_values = [item[0] for item in hp_ac_values]
# ac_values = [item[1] for item in hp_ac_values]
#
# x = list(range(len(hp_ac_values)))
# p = figure(title="Player data over time", x_axis_label='Time', y_axis_label='Values')
# p1 = figure(width=250, plot_height=250, title="HP")
# p1.line(x, hp_values, line_color="red")
#
# p2 = figure(width=250, plot_height=250, title="AC")
# p2.line(x, ac_values, line_color="blue")
#
# p3 = figure(width=250, plot_height=250, title="kills")
# p3.line(x, player_kills, line_color="green")
#
# p4 = figure(width=250, plot_height=250, title="death")
# p4.line(x, player_death, line_color="purple")
#
# grid = gridplot([[p1], [p2], [p3], [p4]])
# show(grid)
#
# # # Read the image
# # # image = cv2.imread('../picture/image4.png')
# # image = cv2.imread('image1.png')
# # height, width, _ = image.shape
# #
# # part2_hp = image[int(1397 * height / 1440):int(1411 * height / 1440),int(172 * width / 2560):int(279 * width / 2560)]
# # b, g, r = cv2.split(part2_hp)
# # print(r[5])
# # r[r > 150] = 255
# # r[r <= 150] = 0
# #
# # print(r[5])
# # hp = int(np.round((100 * np.count_nonzero(r[5] == 255) / 107)) / (width / 2560))
# # print(hp)
# #
# # cv2.imwrite('part1.png', part2_hp)
#
# # part2_ac = image[int(1049 * height / 1080):int(1060 * height / 1440), int(331 * width / 2560):int(549 * width / 2560)]
# # part2_ac = cv2.cvtColor(part2_ac, cv2.COLOR_BGR2GRAY)
# # part2_ac = cv2.inRange(part2_ac, 180, 255)
# # ac = int(np.round((100 * np.count_nonzero(part2_ac[5] == 255) / 107)) / (width / 2560))
# # print(ac)
#
# # reader = easyocr.Reader(['en'], gpu=True)
# # part3_money = image[int(470 * height / 1440):int(530 * height / 1440), int(60 * width / 2560):int(190 * width / 2560)]
# #
# # cv2.imwrite('money.png', part3_money)
# #
# # results = reader.readtext(part3_money, allowlist='0123456789', paragraph=True, batch_size=8)
# #
# # # print(' '.join([result[1] for result in results]))
# #
# # money = ' '.join([result[1] for result in results])
# # print(money)
# #
#
# # part4_magaz = image[int(1382 * height / 1440):int(1420 * height / 1440),
# #               int(2280 * width / 2560):int(2445 * width / 2560)]
# # reader = easyocr.Reader(['en'], gpu=True)
# #
# # results = reader.readtext(part4_magaz, allowlist='0123456789/',
# #                           paragraph=True, batch_size=8)
# #
# # magaz = ' '.join([result[1] for result in results])
# # print(magaz)
#

