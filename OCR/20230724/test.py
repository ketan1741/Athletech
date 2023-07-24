import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import cv2
import time
import easyocr
# from flask import Flask, request
# app = Flask(__name__)

# @app.route('/', methods=['POST'])
# def handle_post():
#     print(request.json)  # Prints the JSON received from CS:GO to the console.
#     return '', 204  # Return a 204 No Content response.

# if __name__ == '__main__':
#     app.run(port=3000)


# hp = np.load('hp_record.npy')

# time = hp[:, 0].astype(float)  # convert to float

# hp_values = np.char.split(hp[:, 1], ' ')  # split the hp and ac values

# hp_values = np.array(hp_values.tolist(), dtype=int)  # convert list of lists to 2D numpy array

# hp = hp_values[:, 0]  # HP values
# ac = hp_values[:, 1]  # AC values

image = cv2.imread('picture/image4.png')
height, width, _ = image.shape
reader = easyocr.Reader(['en'], gpu=True) 
score1 = image[int(40 * height / 1440):int(75 * height / 1440),int(1225 * width / 2560):int(1280 * width / 2560)]
score2 = image[int(40 * height / 1440):int(75 * height / 1440),int(1285 * width / 2560):int(1336 * width / 2560)]
score1 = cv2.resize(score1, (score1.shape[1]*9, score1.shape[0]*9), interpolation=cv2.INTER_LINEAR)
score2 = cv2.resize(score2, (score2.shape[1]*9, score2.shape[0]*9), interpolation=cv2.INTER_LINEAR)
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
score1 = cv2.filter2D(score1, -1, kernel)
score2 = cv2.filter2D(score2, -1, kernel)

# score1 = cv2.resize(score1, (score1.shape[1]*12, score1.shape[0]*12), interpolation=cv2.INTER_LINEAR)
# score2 = cv2.resize(score2, (score2.shape[1]*12, score2.shape[0]*12), interpolation=cv2.INTER_LINEAR)
result1 = reader.readtext(score1, allowlist='0123456789')
score_1 = ' '.join([result[1] for result in result1])
for i in range(1000):
    result2 = reader.readtext(score2, allowlist='0123456789')
    score_2 = ' '.join([result[1] for result in result2])
    print(score_2)
print(score_1)
cv2.imwrite('res1.png', score1)
cv2.imwrite('res2.png', score2)










# for data in hp_values:
#     print(data)
#     if int(data[0]) > 100:
#         hp.append(100)
#     else:
#         hp.append(int(data[0]))
#     if len(data) == 1:
#         ac.append(100)
#     else:
#         if int(data[1]) > 100:
#             ac.append(100)
#         else:
#             ac.append(int(data[1]))

# plt.plot(hp)
# plt.plot(ac)
# plt.legend(['hp', 'ac'])
# plt.savefig('hp_ac.png')
# plt.show()

# dt_object1 = datetime.fromtimestamp(time[0])
# dt_object2 = datetime.fromtimestamp(time[-1])
# i = 0
# for sec in time:
#     date = datetime.fromtimestamp(sec)
#     # print("time:{} - HP:{}".format(date.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dt_object1.microsecond // 1000:03}', hp[i]))
#     print("time:{} - HP:{}".format(sec, hp[i]))
#     i = i + 1

# np.save('hp.npy', hp)
# np.save('ac.npy', ac)


