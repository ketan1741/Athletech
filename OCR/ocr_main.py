from multiprocessing import Process, Queue
import easyocr
import cv2
import time
import Levenshtein
import numpy as np
from datetime import datetime
import cv2
import json
list = ['BOT Dennis', 'BOT Bill', 'Bot Martin', 'BOT Colin', 'BOT Keith', 'ztdtwy', 'BOT Elliot', 'athletechyinzcam']
weapon_list = ['AWP', 'G3SG1', 'Galil AR', 'M4A4', 'M4A1-S', 'SCAR-20', 'SG 553', 'SSG 08', '	FAMAS',
               'AUG', 'AK-47', 'USP-S', 'Tec-9', 'Glock-18', 'Desert Eagle', 'P250', 'Dual Berettas', 'XM1014',
               'Sawed-Off', 'M249', 'Negev', 'Riot Shield', 'Nova', 'MAC-10', 'MP7', 'UMP-45', 'P90', 'PP-Bizon',
               'Zeus x27', 'Molotov', 'Decoy Grenade', 'Flashbang', 'High Explosive Grenade', 'Smoke Grenade',
               'P2000', 'MP5-SD', 'MAG-7', 'MP9', 'Five-SeveN', 'CZ75-Auto', 'R8 Revolver', 'Knife', 'C4 Explosive']

# average frame reading time: 0.0014 sec
# average ocr processing time: 0.1 sec

def read_frames(frame_queue, index):
    try:
        # this function will read frames from the video
        time_list = []
        cap = cv2.VideoCapture('rtmp://localhost/live/stream')
        sta = time.time()
        dat = datetime.fromtimestamp(sta)
        print('start streaming:{}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
        while True:
            ret, image = cap.read()
            current = time.time()
            time_list.append(current)
            
            if not ret:
                break

            # put the frame into the queue to be processed
            frame_queue.put(image)
            index += 1
            if index == 1000:
                end = time.time()
                dat = datetime.fromtimestamp(end)
                frame_queue.put(None)  # signal that we are done reading frames
                print('streaming process end in: {}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
                # print("Reading frame time is ")
                # print(time_list)
                break
        cap.release()
        cv2.destroyAllWindows()
    except KeyboardInterrupt:
        pass
# Perform OCR using EasyOCR

def process_frame(frame_queue):
    try:
        # Initiation OCR Engine
        data_dict = {}
        hp_ac = []
        reader = easyocr.Reader(['en'], gpu=True) 
        sta = time.time()
        dat = datetime.fromtimestamp(sta)
        print('start processing:{}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
        # --------------------------------------------------------Player Status--------------------------------------------------------#
        player_alive = True # Live -> 1  Death -> 0
        new_round = False
        last_hp = 100
        last_ac = 100
        cs_score = 0
        ss_score = 0
        # --------------------------------------------------------Player Status--------------------------------------------------------#
        while True:
            # -------------------------------------------------------image load--------------------------------------------------------#
            image = frame_queue.get()  # get a frame from the queue
            if image is None:
                break
            # Capture frame-by-frame
            ctime = time.time()
                # Do image processing here
            # if index % 600 == 0:
            name = 'result/Frame' +  str(ctime) + '.png'
            cv2.imwrite(name, image)
            # name = 'result/Frame'+str(index)+'.png'
            # cv2.imwrite(name, image)
            height, width, _ = image.shape
            data_dict[str(ctime)] = {}
            # ----------------------------------------------------------score----------------------------------------------------------#
            scores = image[int(40 * height / 1440):int(75 * height / 1440),int(1222 * width / 2560):int(1338 * width / 2560)]
            cs = np.array([238, 212, 181]) 
            ss = np.array([138, 209, 234])
            mask1 = cv2.inRange(scores, cs, cs)
            mask2 = cv2.inRange(scores, ss, ss)
            mask = cv2.bitwise_or(mask1, mask2)
            scores = np.zeros((scores.shape[0], scores.shape[1]))
            scores[mask > 0] = 255

            results = reader.readtext(scores, allowlist='0123456789', paragraph=True, contrast_ths=0.4)
            score = ' '.join([result[1] for result in results])

            if int(results[0][1]) > cs_score:
                if cs_score != 0:
                    cs_score = int(results[0][1])
                    player_alive = True
                else:
                    cs_score = 1
                    player_alive = True
            
            if int(results[0][1]) > cs_score:
                if cs_score != 0:
                    cs_score = int(results[0][1])
                    player_alive = True
                else:
                    cs_score = 1
                    player_alive = True

            data_dict[str(ctime)]['score'] = [cs_score, ss_score]
            data_dict[str(ctime)]['score'] = score
            
            # name = 'result/'+str(ctime)+'.png'
            # cv2.imwrite(name, scores
            # ----------------------------------------------------------score--------------------------------------------------------#
            # -------------------------------------------------------image load------------------------------------------------------#
            if player_alive:
            # ---------------------------------------------------------weapon--------------------------------------------------------#
       
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
                # name = 'result/' + str(ctime) + 'part1.png'
                # cv2.imwrite(name, part1_concate)

                results = reader.readtext(part1_concate, allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                                        paragraph=True, batch_size=8)
                
                weapon_name = ' '.join([result[1] for result in results])

                if weapon_name != "":
                    data_dict[str(ctime)]['weapon o'] = weapon_name
                    distances = [Levenshtein.distance(weapon_name, target) for target in weapon_list]
                    min_distance_index = distances.index(min(distances))
                    weapon_name = weapon_list[min_distance_index]
                # print(weapon_name)

                    data_dict[str(ctime)]['weapon'] = weapon_name
                
                else:
                    data_dict[str(ctime)]['weapon'] = ""
            # ---------------------------------------------------------weapon---------------------------------------------------------#

            # -------------------------------------------------------HP and AC--------------------------------------------------------#
                part2_hp = image[int(1399 * height / 1440):int(1413 * height / 1440),int(166 * width / 2560):int(273 * width / 2560)]
                b, g, r = cv2.split(part2_hp)
                r[r > 180] = 255
                r[r <= 180] = 0
                hp = int(np.round((100*np.count_nonzero(r[5] == 255)/107))/(width / 2560))
                if hp > last_hp:
                    hp = last_hp
                else:
                    last_hp = hp
                part2_ac = image[int(1399 * height / 1440):int(1413 * height / 1440),int(442 * width / 2560):int(549 * width / 2560)]
                part2_ac = cv2.inRange(part2_ac, 0, 160)
                part2_ac = cv2.bitwise_not(part2_ac)
                ac = int(np.round((100*np.count_nonzero(part2_ac[0] == 255)/107))/(width / 2560))
                if ac > last_ac:
                    ac = last_ac
                else:
                    last_ac = ac
                data_dict[str(ctime)]['hp_ac'] = [hp, ac]
                hp_ac.append([ctime, hp, ac])
            # ----------------------------------------------------important!!!!player died--------------------------------------------#
                if hp == 0: # ???
                    player_alive = False
            # ----------------------------------------------------important!!!!player died--------------------------------------------#

                # part2_hp = np.pad(cv2.cvtColor(image[int(1380 * height / 1440):int(1428 * height / 1440),
                #         int(78 * width / 2560):int(153 * width / 2560)], cv2.COLOR_BGR2GRAY), ((20, 20), (20, 20)), mode='edge')
                # part2_ac = np.pad(cv2.cvtColor(image[int(1380 * height / 1440):int(1428 * height / 1440),
                #         int(354 * width / 2560):int(429 * width / 2560)], cv2.COLOR_BGR2GRAY), ((20, 20), (20, 20)), mode='edge')
                # part2_concate = np.concatenate((part2_hp, part2_ac), axis=0)

                # part2_hp = image[int(1380 * height / 1440):int(1428 * height / 1440), int(78 * width / 2560):int(153 * width / 2560)]
                # part2_ac = image[int(1380 * height / 1440):int(1428 * height / 1440), int(354 * width / 2560):int(429 * width / 2560)]
                # part2_concate = np.concatenate((part2_hp, part2_ac), axis=0)
                
                # results_hp = reader.readtext(part2_hp, allowlist='0123456789',
                #                         paragraph=True)
                # results_ac = reader.readtext(part2_ac, allowlist='0123456789',
                #                         paragraph=True)
                
                # integer_list = []
                # if not results_ac or not results_hp:
                #     pass
                # else:
                #     hp_ac.append([ctime, results_hp[0][1], results_ac[0][1]])
                #     data_dict[str(ctime)]['hp_ac'] = [results_hp[0][1], results_ac[0][1]]
            # -------------------------------------------------------HP and AC--------------------------------------------------------#

            # ---------------------------------------------------------Money----------------------------------------------------------#
                part3_money = image[int(470 * height / 1440):int(530 * height / 1440),
                            int(60 * width / 2560):int(190 * width / 2560)]

                results = reader.readtext(part3_money, allowlist='0123456789',
                                        paragraph=True, batch_size=8)

                # print(' '.join([result[1] for result in results]))

                money = ' '.join([result[1] for result in results])
                data_dict[str(ctime)]['money'] = money
            # ---------------------------------------------------------Money----------------------------------------------------------#

            # --------------------------------------------------------Magazine--------------------------------------------------------#
                part4_magaz = image[int(1382 * height / 1440):int(1420 * height / 1440),
                            int(2280 * width / 2560):int(2445 * width / 2560)]

                results = reader.readtext(part4_magaz, allowlist='0123456789/',
                                        paragraph=True, batch_size=8)
                
                magaz = ' '.join([result[1] for result in results])
                data_dict[str(ctime)]['magaz'] = magaz
            # --------------------------------------------------------Magazine--------------------------------------------------------#

            # ----------------------------------------------------------Kill----------------------------------------------------------#
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

                results = reader.readtext(part5_concate, allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ', batch_size=16, width_ths=1)
                # text = ' '.join([result[1] for result in results])
                
                i = 0
                print(ctime, ":")
                for result in results:
                    print(result[1])
                    if i % 2 == 0:
                        if len(result[1]) <= 2:
                            i = i - 1
                            continue
                        killers.append(result[1])
                    if i % 2 == 1:
                        if len(result[1]) <= 2:
                            i = i - 1
                            continue
                        killees.append(result[1])
                    i = i + 1
                
                closest_string_killer = ''
                closest_string_killee = ''
                updated_killers = []
                updated_killees = []

                for killer in killers:

                    split_killers = killer.split()
                    # count = 0

                    
                    for split_killer in split_killers:
                        if split_killer.lower() == 'bot':
                            # count = count + 1
                            continue
                        distances = [Levenshtein.distance(split_killer, target) for target in list]
                        min_distance_index = distances.index(min(distances))
                        closest_string_killer = list[min_distance_index]

                        # if count >= 2:
                        #     closest_string_killer += " and "
                        # closest_string_killer += list[min_distance_index]
                        updated_killers.append(closest_string_killer)
                    

                for killee in killees:
                    split_killees = killee.split()
                    for split_killee in split_killees:
                        if split_killee.lower() == 'bot':
                            continue

                        distances = [Levenshtein.distance(split_killee, target) for target in list]
                        min_distance_index = distances.index(min(distances))
                        closest_string_killee = list[min_distance_index]
                        updated_killees.append(closest_string_killee)
                
                kill_list = []
                for k in range(min(len(updated_killees), len(updated_killers))):

                    if "athletechyinzcam" in updated_killers[k] or "athletechyinzcam" in updated_killees[k]:
                        kill_list.append({updated_killers[k] : updated_killees[k]})
                        data_dict[str(ctime)]['kill_info'] = kill_list
        # ----------------------------------------------------------Kill----------------------------------------------------------#
            else:
                data_dict[str(ctime)]['kill_info'] = 'None'
                data_dict[str(ctime)]['magaz'] = 'None'
                data_dict[str(ctime)]['money'] = 'None'
                data_dict[str(ctime)]['score'] = [cs_score, ss_score]
                data_dict[str(ctime)]['HP_AC'] = [hp, ac]
                data_dict[str(ctime)]['weapon'] = 'None'
                

        end = time.time()
        dat = datetime.fromtimestamp(end)
        print('process end in: {}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
        np.save('hp_record.npy', np.array(hp_ac))
        with open('data.json', 'w') as f:
        # Use json.dump to write dict_data to the file
            json.dump(data_dict, f, indent=4)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    try:
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
    except KeyboardInterrupt:
        p1.join()
        # p2.terminate()
        p2.join()
        p1.terminate()
        p2.terminate()
        

