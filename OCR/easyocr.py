import easyocr
import cv2
import time
import Levenshtein
import numpy as np

list = ['BOT Dennis', 'BOT Bill', 'Bot Martin', 'BOT Colin', 'BOT Keith', 'ztdtwy', 'BOT Elliot']

# Perform OCR using EasyOCR
sta = time.time()


# part1 = image[int(height*(19/20)):height, int(width*(1/30)):int(width*(2/30))] # left bottom life
# part2 = image[int(height*(19/20)):height, int(width*(4/30)):int(width*(5/30))] # left bottom armor
# part3 = image[int(height*(6/10)):height, int(width*(15/20)):width] # right bottom
#part4 = image[0:int(height*(3/10)), int(width*(15/20)):width] # right top


# results = reader.readtext(part1, allowlist='0123456789')
# text = ' '.join([result[1] for result in results])
# print(text)
#
# results = reader.readtext(part2)
# text = ' '.join([result[1] for result in results])
# print(text)
#
# results = reader.readtext(part3)
# text = ' '.join([result[1] for result in results])
# print(text)

updated_killers = []
updated_killees = []

for j in range(2):

    image = cv2.imread(f'./picture/image{j+1}.png')
    height, width, _ = image.shape

    part4_kill1 = image[int(100 * height / 1440):int(143 * height / 1440),
                  int(2000 * width / 2560):int(2550 * width / 2560)]
    part4_kill2 = image[int(147 * height / 1440):int(190 * height / 1440),
                  int(2000 * width / 2560):int(2550 * width / 2560)]
    part4_kill3 = image[int(194 * height / 1440):int(237 * height / 1440),
                  int(2000 * width / 2560):int(2550 * width / 2560)]
    part4_kill4 = image[int(241 * height / 1440):int(284 * height / 1440),
                  int(2000 * width / 2560):int(2550 * width / 2560)]
    part4_kill5 = image[int(288 * height / 1440):int(331 * height / 1440),
                  int(2000 * width / 2560):int(2550 * width / 2560)]

    part4_concate = np.concatenate((part4_kill1, part4_kill2, part4_kill3, part4_kill4, part4_kill5),
                                   axis=0)  # vertical
    reader = easyocr.Reader(['en'])  # Initialize the EasyOCR reader with desired languages

    killers = []
    killees = []
    previous = 0


    results = reader.readtext(part4_concate, allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ', paragraph=True)
    # text = ' '.join([result[1] for result in results])


    i = 0
    for result in results:
        if i % 2 == 0:
            killers.append(result[1])
        if i % 2 == 1:
            killees.append(result[1])
        i = i + 1



    for killer in killers:
        split_killers = killer.split()

        closest_string = ''
        count = 0
        for split_killer in split_killers:
            if split_killer.lower() == 'bot':
                count = count + 1
                continue
            distances = [Levenshtein.distance(split_killer, target) for target in list]
            min_distance_index = distances.index(min(distances))

            if count >= 2:
                closest_string += " and "
            closest_string += list[min_distance_index]


        updated_killers.append(closest_string)


    for killee in killees:
        split_killees = killee.split()
        for split_killee in split_killees:
            if split_killee.lower() == 'bot':
                continue
            distances = [Levenshtein.distance(split_killee, target) for target in list]
            min_distance_index = distances.index(min(distances))
            closest_string = list[min_distance_index]
            updated_killees.append(closest_string)

print(updated_killers)
print(updated_killees)



end = time.time()
print(end-sta)
