from multiprocessing import Process, Queue
import easyocr
import cv2
import time
import Levenshtein
import numpy as np
import cv2
import json
list = ['BOT Dennis', 'BOT Bill', 'Bot Martin', 'BOT Colin', 'BOT Keith', 'ztdtwy', 'BOT Elliot']
weapon_list = ['AWP', 'G3SG1', 'Galil AR', 'M4A4', 'M4A1-S', 'SCAR-20', 'SG 553', 'SSG 08', '	FAMAS',
               'AUG', 'AK-47', 'USP-S', 'Tec-9', 'Glock-18', 'Desert Eagle', 'P250', 'Dual Berettas', 'XM1014',
               'Sawed-Off', 'M249', 'Negev', 'Riot Shield', 'Nova', 'MAC-10', 'MP7', 'UMP-45', 'P90', 'PP-Bizon',
               'Zeus x27', 'Molotov', 'Decoy Grenade', 'Flashbang', 'High Explosive Grenade', 'Smoke Grenade',
               'P2000', 'MP5-SD', 'MAG-7', 'MP9', 'Five-SeveN', 'CZ75-Auto', 'R8 Revolver', 'Knife', 'C4 Explosive']

# average frame reading time: 0.0014 sec
# average ocr processing time: 0.1 sec


def read_frames(frame_queue, index):
    # this function will read frames from the video
    time_list = []
    cap = cv2.VideoCapture('rtmp://localhost/live/stream')

    while True:
        ret, image = cap.read()
        current = time.time()
        time_list.append(current)

        if not ret:
            break

        # put the frame into the queue to be processed
        frame_queue.put(image)
        index += 1
        if index == 100:
            frame_queue.put(None)  # signal that we are done reading frames
            # print("Reading frame time is ")
            # print(time_list)
            break
    cap.release()
    cv2.destroyAllWindows()
# Perform OCR using EasyOCR
# Create a VideoCapture object


def process_frame(frame_queue):
    reader = easyocr.Reader(['en'], gpu=True)  # Initialize the EasyOCR reader with desired languages
    data_dict = {}
    hp_ac = []
    updated_killers = []
    updated_killees = []
    while True:
        image = frame_queue.get()  # get a frame from the queue
        if image is None:
            break
        # Capture frame-by-frame
        ctime = time.time()

        name = 'result/' +  str(ctime) + '.png'
        cv2.imwrite(name, image)

            # Do image processing here
        # if index % 600 == 0:
        # name = 'result/Frame'+str(index)+'.png'
        # cv2.imwrite(name, image)
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
        # part1_concate = cv2.cvtColor(part1_concate, cv2.COLOR_BGR2GRAY)
        # ret, part1_concate = cv2.threshold(part1_concate, 200, 255, cv2.THRESH_BINARY)
        name = 'result/' + str(ctime) + 'part1.png'
        cv2.imwrite(name, part1_concate)

        results = reader.readtext(part1_concate, allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                                paragraph=True, batch_size=8)
        
        data_dict[str(ctime)] = {}
        weapon_name = ' '.join([result[1] for result in results])
        data_dict[str(ctime)]['weapon o'] = weapon_name
        distances = [Levenshtein.distance(weapon_name, target) for target in weapon_list]
        min_distance_index = distances.index(min(distances))
        weapon_name = weapon_list[min_distance_index]
        # print(weapon_name)

        data_dict[str(ctime)]['weapon'] = weapon_name


        # HP and AC
        part2_hp = np.pad(cv2.cvtColor(image[int(1380 * height / 1440):int(1428 * height / 1440),
                int(78 * width / 2560):int(153 * width / 2560)], cv2.COLOR_BGR2GRAY), ((20, 20), (20, 20)), mode='edge')
        part2_ac = np.pad(cv2.cvtColor(image[int(1380 * height / 1440):int(1428 * height / 1440),
                int(354 * width / 2560):int(429 * width / 2560)], cv2.COLOR_BGR2GRAY), ((20, 20), (20, 20)), mode='edge')


        part2_hp = cv2.adaptiveThreshold(part2_hp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 7)
        part2_ac = cv2.adaptiveThreshold(part2_ac, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 7)

        # part2_concate = np.concatenate((part2_hp, part2_ac), axis=0)
        # ret, part2_hp = cv2.threshold(part2_hp, 200, 255, cv2.THRESH_BINARY)
        # ret, part2_ac = cv2.threshold(part2_ac, 200, 255, cv2.THRESH_BINARY)

        name = 'result/' + str(ctime) + 'part2.png'
        cv2.imwrite(name, part2_hp)

        results_hp = reader.readtext(part2_hp, allowlist='0123456789',
                                paragraph=True)
        results_ac = reader.readtext(part2_ac, allowlist='0123456789',
                                paragraph=True)
        
        if not results_ac or not results_hp:
            pass
        else:
            hp_ac.append([ctime, results_hp[0][1], results_ac[0][1]])
            data_dict[str(ctime)]['hp_ac'] = [results_hp[0][1], results_ac[0][1]]
        # print(' '.join([result[1] for result in results]))

        part3_money = image[int(470 * height / 1440):int(530 * height / 1440),
                    int(60 * width / 2560):int(190 * width / 2560)]

        results = reader.readtext(part3_money, allowlist='0123456789',
                                paragraph=True, batch_size=8)

        # print(' '.join([result[1] for result in results]))

        money = ' '.join([result[1] for result in results])
        data_dict[str(ctime)]['money'] = money

        part4_magaz = image[int(1382 * height / 1440):int(1420 * height / 1440),
                    int(2280 * width / 2560):int(2445 * width / 2560)]

        results = reader.readtext(part4_magaz, allowlist='0123456789/',
                                paragraph=True, batch_size=8)
        
        magaz = ' '.join([result[1] for result in results])
        data_dict[str(ctime)]['magaz'] = magaz

        # print(' '.join([result[1] for result in results]))

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

        cv2.imwrite("part1.png", part1_concate)
        cv2.imwrite("part2.png", part2_hp)
        cv2.imwrite("part3.png", part3_money)
        cv2.imwrite("part4.png", part4_magaz)
        cv2.imwrite("part5.png", part5_concate)
        cv2.imwrite("image.png", image)
        
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
        data_dict[str(ctime)]['kill_info'] = kill_list


        # print("\n\n********Next Image")

        # Exit if ESC key is pressed
        # if cv2.waitKey(20) & 0xFF == 27:
        # break

    np.save('hp_record.npy', np.array(hp_ac))
    # print(updated_killers)
    # print(updated_killees)
    with open('data.json', 'w') as f:
    # Use json.dump to write dict_data to the file
        json.dump(data_dict, f, indent=4)
# When everything done, release the VideoCapture object

# end = time.time()
# print(sta-end)
# Close all the frames
if __name__ == '__main__':
    index = 0
    frame_queue = Queue()

    # create two processes
    p1 = Process(target=read_frames, args=(frame_queue, index,))
    p2 = Process(target=process_frame, args=(frame_queue,))

    # start the processes
    p1.start()
    p2.start()

    # wait for both processes to finish
    # p1.terminate()
    p1.join()
    # p2.terminate()
    p2.join()
    p1.terminate()
    p2.terminate()


