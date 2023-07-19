import easyocr
import cv2
import time
import Levenshtein
import numpy as np
import cv2
list = ['BOT Dennis', 'BOT Bill', 'Bot Martin', 'BOT Colin', 'BOT Keith', 'ztdtwy', 'BOT Elliot']
weapon_list = ['AWP', 'G3SG1', 'Galil AR', 'M4A4', 'M4A1-S', 'SCAR-20', 'SG 553', 'SSG 08', '	FAMAS',
               'AUG', '	AK-47', 'USP-S', 'Tec-9', 'Glock-18', 'Desert Eagle', 'P250', 'Dual Berettas', 'XM1014',
               'Sawed-Off', 'M249', 'Negev', 'Riot Shield', 'Nova', 'MAC-10', 'MP7', 'UMP-45', 'P90', 'PP-Bizon',
               'Zeus x27', 'Molotov', 'Decoy Grenade', 'Flashbang', 'High Explosive Grenade', 'Smoke Grenade',
               'P2000', 'MP5-SD', 'MAG-7', 'MP9', 'Five-SeveN', 'CZ75-Auto', 'R8 Revolver']

# average frame reading time: 0.0014 sec
# average ocr processing time: 0.1 sec


# Perform OCR using EasyOCR
# Create a VideoCapture object
cap = cv2.VideoCapture('rtmp://localhost/live/stream')
index = 0

# Change 1
data_dict = {}

hp_ac = []
updated_killers = []
updated_killees = []
index = 0

reader = easyocr.Reader(['en'], gpu=True)  # Initialize the EasyOCR reader with desired languages
while True:
    index += 1
    # Capture frame-by-frame
    ret, image = cap.read()

    if not ret:
        break

        # Do image processing here
    # if index % 600 == 0:
    # name = 'result/Frame'+str(index)+'.png'
    # cv2.imwrite(name, image)
    ctime = time.time()

    height, width, _ = image.shape

    part1_weap1 = image[int(906 * height / 1440):int(925 * height / 1440),
                int(2100 * width / 2560):int(2530 * width / 2560)]  # top
    part1_weap2 = image[int(1012 * height / 1440):int(1042 * height / 1440),
                int(2100 * width / 2560):int(2530 * width / 2560)]
    part1_weap3 = image[int(1118 * height / 1440):int(1148 * height / 1440),
                int(2100 * width / 2560):int(2530 * width / 2560)]
    part1_weap4 = image[int(1224 * height / 1440):int(1254 * height / 1440),
                int(2100 * width / 2560):int(2530 * width / 2560)]
    part1_weap5 = image[int(1341 * height / 1440):int(1360 * height / 1440),
                int(2100 * width / 2560):int(2530 * width / 2560)]  # bottom
    part1_concate = np.concatenate((part1_weap1, part1_weap2, part1_weap3, part1_weap4, part1_weap5),
                                axis=0)  # vertical

    results = reader.readtext(part1_concate, allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789',
                            paragraph=True, batch_size=8)
    
    weapon_name = ' '.join([result[1] for result in results])
    distances = [Levenshtein.distance(weapon_name, target) for target in weapon_list]
    min_distance_index = distances.index(min(distances))
    weapon_name = weapon_list[min_distance_index]
    print(weapon_name)

    # Change 2
    data_dict[ctime]['weapon'] = weapon_name


    # HP and AC
    part2_hp = image[int(1380 * height / 1440):int(1428 * height / 1440),
            int(78 * width / 2560):int(153 * width / 2560)]
    part2_ac = image[int(1380 * height / 1440):int(1428 * height / 1440),
            int(354 * width / 2560):int(429 * width / 2560)]
    part2_concate = np.concatenate((part2_hp, part2_ac), axis=0)

    results = reader.readtext(part2_concate, allowlist='0123456789',
                            paragraph=True)
    
    if not results:
        pass
    else:
        hp_ac.append([ctime, results[0][1]])

    data_dict[ctime]['hp_ac'] = results[0][1]
    # print(' '.join([result[1] for result in results]))

    part3_money = image[int(470 * height / 1440):int(530 * height / 1440),
                int(60 * width / 2560):int(190 * width / 2560)]

    results = reader.readtext(part3_money, allowlist='0123456789',
                            paragraph=True, batch_size=8)

    money = ' '.join([result[1] for result in results])
    print(' '.join([result[1] for result in results]))

    data_dict[ctime]['money'] = money

    part4_magaz = image[int(1382 * height / 1440):int(1420 * height / 1440),
                int(2280 * width / 2560):int(2445 * width / 2560)]

    results = reader.readtext(part4_magaz, allowlist='0123456789/',
                            paragraph=True, batch_size=8)

    magaz = ' '.join([result[1] for result in results])
    print(magaz)
    data_dict[ctime]['magaz'] = magaz

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

    part5_concate = np.concatenate((part5_kill1, part5_kill2, part5_kill3, part5_kill4, part5_kill5),
                                axis=0)  # vertical

    killers = []
    killees = []
    previous = 0

    # cv2.imwrite("part1.png", part1_concate)
    # cv2.imwrite("part2.png", part2_concate)
    # cv2.imwrite("part3.png", part3_money)
    # cv2.imwrite("part4.png", part4_magaz)
    # cv2.imwrite("part5.png", part5_concate)
    # cv2.imwrite("image.png", image)
    
    results = reader.readtext(part5_concate, allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ', paragraph=True, batch_size=16)
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

    kill_list = []

    for i in range(len(killees)):
        kill_list.append({killers[i]:killees[i]})

    data_dict[ctime]['kill_info'] = kill_list

    if index == 4000:
        break
    print("\n\n********Next Image")

    # Exit if ESC key is pressed
    # if cv2.waitKey(20) & 0xFF == 27:
    # break

np.save('hp_record.npy', np.array(hp_ac))
print(updated_killers)
print(updated_killees)
# When everything done, release the VideoCapture object
cap.release()
# end = time.time()
# print(sta-end)
# Close all the frames

cv2.destroyAllWindows()
# updated_killers = []
# updated_killees = []
# reader = easyocr.Reader(['en'], gpu=True)  # Initialize the EasyOCR reader with desired languages

# end0 = time.time()
# print(end0-sta)

# for j in range(9):
#     sta1 = time.time()
#     image = cv2.imread(f'C:\\Research\\Athletech-main\\Athletech-main\\OCR\\picture1\\image{j+1}.png')
#     height, width, _ = image.shape

#     part1_weap1 = image[int(906 * height / 1440):int(925 * height / 1440),
#                   int(2100 * width / 2560):int(2530 * width / 2560)]  # top
#     part1_weap2 = image[int(1012 * height / 1440):int(1042 * height / 1440),
#                   int(2100 * width / 2560):int(2530 * width / 2560)]
#     part1_weap3 = image[int(1118 * height / 1440):int(1148 * height / 1440),
#                   int(2100 * width / 2560):int(2530 * width / 2560)]
#     part1_weap4 = image[int(1224 * height / 1440):int(1254 * height / 1440),
#                   int(2100 * width / 2560):int(2530 * width / 2560)]
#     part1_weap5 = image[int(1341 * height / 1440):int(1360 * height / 1440),
#                   int(2100 * width / 2560):int(2530 * width / 2560)]  # bottom
#     part1_concate = np.concatenate((part1_weap1, part1_weap2, part1_weap3, part1_weap4, part1_weap5),
#                                    axis=0)  # vertical

#     results = reader.readtext(part1_concate, allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789',
#                               paragraph=True, batch_size=8)

#     print(' '.join([result[1] for result in results]))
#     # HP and AC
#     part2_hp = image[int(1380 * height / 1440):int(1428 * height / 1440),
#                int(78 * width / 2560):int(153 * width / 2560)]
#     part2_ac = image[int(1380 * height / 1440):int(1428 * height / 1440),
#                int(354 * width / 2560):int(429 * width / 2560)]
#     part2_concate = np.concatenate((part2_hp, part2_ac), axis=0)

#     results = reader.readtext(part2_concate, allowlist='0123456789',
#                               paragraph=True, batch_size=8)

#     print(' '.join([result[1] for result in results]))

#     part3_money = image[int(470 * height / 1440):int(530 * height / 1440),
#                   int(60 * width / 2560):int(190 * width / 2560)]

#     results = reader.readtext(part3_money, allowlist='0123456789',
#                               paragraph=True, batch_size=8)

#     print(' '.join([result[1] for result in results]))

#     part4_magaz = image[int(1382 * height / 1440):int(1420 * height / 1440),
#                   int(2280 * width / 2560):int(2445 * width / 2560)]

#     results = reader.readtext(part4_magaz, allowlist='0123456789',
#                               paragraph=True, batch_size=8)

#     print(' '.join([result[1] for result in results]))

#     part4_kill1 = image[int(100 * height / 1440):int(143 * height / 1440),
#                   int(2000 * width / 2560):int(2550 * width / 2560)]
#     part4_kill2 = image[int(147 * height / 1440):int(190 * height / 1440),
#                   int(2000 * width / 2560):int(2550 * width / 2560)]
#     part4_kill3 = image[int(194 * height / 1440):int(237 * height / 1440),
#                   int(2000 * width / 2560):int(2550 * width / 2560)]
#     part4_kill4 = image[int(241 * height / 1440):int(284 * height / 1440),
#                   int(2000 * width / 2560):int(2550 * width / 2560)]
#     part4_kill5 = image[int(288 * height / 1440):int(331 * height / 1440),
#                   int(2000 * width / 2560):int(2550 * width / 2560)]

#     part4_concate = np.concatenate((part4_kill1, part4_kill2, part4_kill3, part4_kill4, part4_kill5),
#                                    axis=0)  # vertical

#     killers = []
#     killees = []
#     previous = 0


#     results = reader.readtext(part4_concate, allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ', paragraph=True, batch_size=8)
#     # text = ' '.join([result[1] for result in results])


#     i = 0
#     for result in results:
#         if i % 2 == 0:
#             killers.append(result[1])
#         if i % 2 == 1:
#             killees.append(result[1])
#         i = i + 1



#     for killer in killers:
#         split_killers = killer.split()

#         closest_string = ''
#         count = 0
#         for split_killer in split_killers:
#             if split_killer.lower() == 'bot':
#                 count = count + 1
#                 continue
#             distances = [Levenshtein.distance(split_killer, target) for target in list]
#             min_distance_index = distances.index(min(distances))

#             if count >= 2:
#                 closest_string += " and "
#             closest_string += list[min_distance_index]


#         updated_killers.append(closest_string)


#     for killee in killees:
#         split_killees = killee.split()
#         for split_killee in split_killees:
#             if split_killee.lower() == 'bot':
#                 continue
#             distances = [Levenshtein.distance(split_killee, target) for target in list]
#             min_distance_index = distances.index(min(distances))
#             closest_string = list[min_distance_index]
#             updated_killees.append(closest_string)
#     end1 = time.time()
#     print(end1-sta1)
#     print("\n\n********Next Image")
# print(updated_killers)
# print(updated_killees)



# end = time.time()
# print(end-sta)

