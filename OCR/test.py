import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# from flask import Flask, request
# app = Flask(__name__)

# @app.route('/', methods=['POST'])
# def handle_post():
#     print(request.json)  # Prints the JSON received from CS:GO to the console.
#     return '', 204  # Return a 204 No Content response.

# if __name__ == '__main__':
#     app.run(port=3000)
hp = np.load('hp_record.npy')

time = hp[:, 0].astype(float)  # convert to float

hp_values = np.char.split(hp[:, 1], ' ')  # split the hp and ac values

# hp_values = np.array(hp_values.tolist(), dtype=int)  # convert list of lists to 2D numpy array

# hp = hp_values[:, 0]  # HP values
# ac = hp_values[:, 1]  # AC values

hp = []
ac = []

print(hp_values)
for data in hp_values:
    print(data)
    if int(data[0]) > 100:
        hp.append(100)
    else:
        hp.append(int(data[0]))
    if len(data) == 1:
        ac.append(100)
    else:
        if int(data[1]) > 100:
            ac.append(100)
        else:
            ac.append(int(data[1]))

plt.plot(hp)
plt.plot(ac)
plt.legend(['hp', 'ac'])
plt.savefig('hp_ac.png')
plt.show()

dt_object = datetime.fromtimestamp(time[3])
formatted_time = dt_object.strftime('%Y-%m-%d-%H-%M-%S-') + f'{dt_object.microsecond // 1000:03}'

np.save('hp.npy', hp)
np.save('ac.npy', ac)
