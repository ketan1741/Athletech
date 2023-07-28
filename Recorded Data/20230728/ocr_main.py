import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from multiprocessing import Process, Queue
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
list = ['BOT Dennis', 'BOT Bill', 'Bot Martin', 'BOT Colin', 'BOT Keith', 'BOT Elliot', 'athletechyinzcam']
weapon_list = ['AWP', 'G3SG1', 'Galil AR', 'M4A4', 'M4A1-S', 'SCAR-20', 'SG 553', 'SSG 08', '	FAMAS',
               'AUG', 'AK-47', 'USP-S', 'Tec-9', 'Glock-18', 'Desert Eagle', 'P250', 'Dual Berettas', 'XM1014',
               'Sawed-Off', 'M249', 'Negev', 'Riot Shield', 'Nova', 'MAC-10', 'MP7', 'UMP-45', 'P90', 'PP-Bizon',
               'Zeus x27', 'Molotov', 'Decoy Grenade', 'Flashbang', 'High Explosive Grenade', 'Smoke Grenade',
               'P2000', 'MP5-SD', 'MAG-7', 'MP9', 'Five-SeveN', 'CZ75-Auto', 'R8 Revolver', 'Knife', 'C4 Explosive']

# average frame reading time: 0.0014 sec
# average ocr processing time: 0.1 sec
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 5)
        self.conv2 = nn.Conv2d(32, 64, 5)
        self.conv3 = nn.Conv2d(64, 128, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 8 * 8, 1024)
        self.fc2 = nn.Linear(1024, 512)
        self.fc3 = nn.Linear(512, 3) 

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 8 * 8)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    

def read_frames(frame_queue, index):
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
        if index == 6000:
            end = time.time()
            dat = datetime.fromtimestamp(end)
            frame_queue.put(None)  # signal that we are done reading frames
            print('streaming process end in: {}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
            # print("Reading frame time is ")
            # print(time_list)
            break
    cap.release()
    cv2.destroyAllWindows()
# Perform OCR using EasyOCR

def process_frame(frame_queue):
    # Initiation OCR Engine
    
    # hp_ac = []
    # data_dict = {}

    # sta = time.time()
    # dat = datetime.fromtimestamp(sta)
    

    # threshold = 0.95
    cs_icon = cv2.imread('icon/cs.png')
    ss_icon = cv2.imread('icon/ss.png')
    cs_icon = cv2.resize(cs_icon, (88, 88))
    ss_icon = cv2.resize(ss_icon, (88, 88))
    mask = np.zeros_like(cs_icon)
    cv2.circle(mask, (cs_icon.shape[1]//2, cs_icon.shape[0]//2), 44, (255,255,255), thickness=-1)
    transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)) ])
    data_dict = {}
    hp_ac = []
    reader = easyocr.Reader(['en'], gpu=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = torch.load('C:\Research\TrueTest\Athletech-main\Athletech-main\OCR\model.pth') 
    model.to(device)
    sta = time.time()
    dat = datetime.fromtimestamp(sta)
    print('start processing:{}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
    # --------------------------------------------------------Player Status--------------------------------------------------------#
    player_alive = True # Live -> 1  Death -> 0
    round_flag = False
    last_hp = 100
    last_ac = 100
    cs_score = 0
    ss_score = 0
    index = 0
    global_kill_dict = []
    # --------------------------------------------------------Player Status--------------------------------------------------------#
    while True:
        # -------------------------------------------------------image load--------------------------------------------------------#
        image = frame_queue.get()  # get a frame from the queue
        
        if image is None:
            break

        # Capture frame-by-frame
        ctime = time.time()
        name = 'result/' +  str(ctime) + 'frame.png'
        cv2.imwrite(name, image)
        height, width, _ = image.shape
        data_dict[str(ctime)] = {}
        # ----------------------------------------------------------score----------------------------------------------------------#
        if round_flag == False:
            winner = image[int(171 * height / 1440):int(288 * height / 1440), int(1222 * width / 2560):int(1339 * width / 2560)]
            winner = cv2.bitwise_and(winner, mask)
            # name = 'result/' +  str(ctime) + 'winner.png'
            # cv2.imwrite(name, winner)
            # result_cs = cv2.matchTemplate(winner, cs_icon, cv2.TM_CCORR_NORMED)
            # result_ss = cv2.matchTemplate(winner, ss_icon, cv2.TM_CCORR_NORMED)
            # data_dict[str(ctime)]['thres'] = [result_cs.tolist(), result_ss.tolist()]

            # locations_cs = np.where(result_cs > threshold)
            # locations_ss = np.where(result_ss > threshold)

            # if locations_cs[0].size != 0 and index==0:
            #     cs_flag = True
            # elif locations_ss[0].size != 0 and index==0:
            #     ss_flag = True
            i_copy = transform(winner)
            i_copy = i_copy.to(device)
            i_copy = i_copy.unsqueeze(0)
            output = model(i_copy)
            _, predicted = torch.max(output.data, 1)

            if predicted == 1 or predicted == 2:
                round_flag = True 
                win = predicted

        # else:
        #     if win == 1:
        #         cs_score += 1
        #     elif win == 2:
        #         ss_score += 1

        else:
            index += 1
            if index == 160:
                if win == 1:
                    cs_score += 1
                    player_alive = True
                elif win == 2:
                    ss_score += 1
                    player_alive = True


                index = 0
                round_flag = False
                
        data_dict[str(ctime)]['score'] = [cs_score, ss_score]
        # # ----------------------------------------------------------score--------------------------------------------------------#
        # _, image_grey = cv2.threshold(image_grey, 128, 255, cv2.THRESH_TOZERO_INV)
        # score1 = image_grey[int(40 * height / 1440):int(75 * height / 1440),int(1225 * width / 2560):int(1280 * width / 2560)]
        # score2 = image_grey[int(40 * height / 1440):int(75 * height / 1440),int(1285 * width / 2560):int(1330 * width / 2560)]
        # score1 = cv2.resize(score1, (score1.shape[1]*10, score1.shape[0]*10), interpolation=cv2.INTER_LINEAR)
        # score2 = cv2.resize(score2, (score2.shape[1]*10, score2.shape[0]*10), interpolation=cv2.INTER_LINEAR)
        # kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        # score1 = cv2.filter2D(score1, -1, kernel)
        # score2 = cv2.filter2D(score2, -1, kernel)

        # result1 = reader.readtext(score1, allowlist='0123456789')
        # score_1 = ' '.join([result[1] for result in result1])

        # result2 = reader.readtext(score2, allowlist='0123456789')
        # score_2 = ' '.join([result[1] for result in result2])

        # data_dict[str(ctime)]['score'] = [score_1, score_2]

        
        if player_alive == False:
            global_kill_dict = []



        # -------------------------------------------------------image load------------------------------------------------------#
        if player_alive:
            # print('At time: {}, player is alive'.format(ctime))
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
            r[r > 150] = 255
            r[r <= 180] = 0
            hp = int(np.round((100*np.count_nonzero(r[5] == 255)/107))/(width / 2560))
            # if hp > last_hp:
            #     hp = last_hp
            # else:
            #     last_hp = hp
            part2_ac = image[int(1399 * height / 1440):int(1413 * height / 1440),int(442 * width / 2560):int(549 * width / 2560)]
            part2_ac = cv2.cvtColor(part2_ac, cv2.COLOR_BGR2GRAY)
            part2_ac = cv2.inRange(part2_ac, 200, 255)
            ac = int(np.round((100*np.count_nonzero(part2_ac[0] == 255)/107))/(width / 2560))
            # if ac > last_ac:
            #     ac = last_ac
            # else:
            #     last_ac = ac
            data_dict[str(ctime)]['hp_ac'] = [hp, ac]
            hp_ac.append([ctime, hp, ac])
        # ----------------------------------------------------important!!!!player died--------------------------------------------#

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

            # part5_concate = np.concatenate((part5_kill1, part5_kill2, part5_kill3, part5_kill4, part5_kill5),
            #                             axis=0)  # vertical

            part5_list = [part5_kill1, part5_kill2, part5_kill3, part5_kill4, part5_kill5]

            killers = []
            killees = []
            

            for i in range(5):
                results = reader.readtext(part5_list[i], allowlist='+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ', width_ths=0.4, paragraph=True)
                
                # text = ' '.join([result[1] for result in results])
            
                m = 0
                for result in results:
                    print(ctime, " ", result[1])
                    
                    if (len(result[1]) <= 6):
                        continue
                    
                    if m % 2 == 0:
                        killers.append(result[1])
                    
                    if m % 2 == 1:
                        killees.append(result[1])
                    
                    m = m + 1
            
                closest_string_killer = ''
                closest_string_killee = ''
                updated_killers = []
                updated_killees = []
                
                concate_killers = ""
                concate_killees = ""
                for killer in killers:

                    split_killers = killer.split()

                    count = 0

                    for split_killer in split_killers:
                        if split_killer.lower() == 'bot':
                            continue

                        if len(split_killer) <= 2:
                            continue
                        distances = [Levenshtein.distance(split_killer, target) for target in list]
                        min_distance_index = distances.index(min(distances))
                        closest_string_killer = list[min_distance_index]
                        count = count + 1
                        
                        if count == 2:
                            concate_killers += " and " 
                            concate_killers += closest_string_killer
                            break

                        concate_killers = closest_string_killer
                    
                    updated_killers.append(concate_killers)

                for killee in killees:
                    split_killees = killee.split()
                    for split_killee in split_killees:
                        if split_killee.lower() == 'bot':
                            continue

                        distances = [Levenshtein.distance(split_killee, target) for target in list]
                        min_distance_index = distances.index(min(distances))
                        closest_string_killee = list[min_distance_index]
                        concate_killees = closest_string_killee
                        updated_killees.append(closest_string_killee)
                
                if (concate_killers != "" and concate_killees != ""):
                     
                    kill_list = []
                    if "athletechyinzcam" in concate_killers  or "athletechyinzcam" in concate_killees:
                        kill_list.append({concate_killers : concate_killees})
                        print(kill_list)

                        if {concate_killers : concate_killees} not in global_kill_dict:
                            global_kill_dict.append({concate_killers : concate_killees})
                            data_dict[str(ctime)]['kill_info'] = kill_list

                    if "athletechyinzcam" in concate_killees:
                        player_alive = False
            
    # ----------------------------------------------------------Kill----------------------------------------------------------#
        else:
            # print('At time: {}, player is died'.format(ctime))
            pass
            

    end = time.time()
    dat = datetime.fromtimestamp(end)
    print('process end in: {}'.format(dat.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dat.microsecond // 1000:03}'))
    np.save('hp_record.npy', np.array(hp_ac))
    with open('../OCR/data.json', 'w') as f:
    # Use json.dump to write dict_data to the file
        json.dump(data_dict, f, indent=4)


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
        p1.join()
        p2.join()
        p1.terminate()
        p2.terminate()
    except KeyboardInterrupt:
        p1.join()
        # p2.terminate()
        p2.join()
        p1.terminate()
        p2.terminate()
        

