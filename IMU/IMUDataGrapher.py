import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['r', 'b', 'y'])

l1_g_data = []
l1_a_data = []
r1_g_data = []
r1_a_data = []
l2_g_data = []
l2_a_data = []
r2_g_data = []
r2_a_data = []
l3_g_data = []
l3_a_data = []
r3_g_data = []
r3_a_data = []

with open("IMUdata.txt", 'r') as file:
    data = file.readlines()
    for i in data[1:]:
        temp = i.strip().split(",")
        tempfloat = []
        for i in range (len(temp)):
            if (i % 6) > 2:
                if(float(temp[i]) > 40):
                    tempfloat.append(40)
                elif(float(temp[i]) < -40):
                    tempfloat.append(-40)
                else:
                    tempfloat.append(float(temp[i]))
            else:
                if(float(temp[i]) > 34.9):
                    tempfloat.append(34.91)
                elif(float(temp[i]) < -34.9):
                    tempfloat.append(-34.91)
                else:
                    tempfloat.append(float(temp[i]))

        l1_g_data.append(tempfloat[0:3])
        l1_a_data.append(tempfloat[3:6])
        r1_g_data.append(tempfloat[6:9])
        r1_a_data.append(tempfloat[9:12])
        l2_g_data.append(tempfloat[12:15])
        l2_a_data.append(tempfloat[15:18])
        r2_g_data.append(tempfloat[18:21])
        r2_a_data.append(tempfloat[21:24])
        l3_g_data.append(tempfloat[24:27])
        l3_a_data.append(tempfloat[27:30])
        r3_g_data.append(tempfloat[30:33])
        r3_a_data.append(tempfloat[33:])

# print(l1_a_data)
# print(x)
time_in_seconds = [i * 0.25 for i in range(len(l1_g_data))]
labels = ['x', 'y', 'z']

figure, axis = plt.subplots(3,4)

axis[0, 0].plot(time_in_seconds, l1_g_data)
axis[0, 0].set_title("Left Wrist Gyro")
axis[0, 1].plot(time_in_seconds, l1_a_data)
axis[0, 1].set_title("Left Wrist Accel")
axis[0, 2].plot(time_in_seconds, r1_g_data)
axis[0, 2].set_title("Right Wrist Gyro")
axis[0, 3].plot(time_in_seconds, r1_a_data)
axis[0, 3].set_title("Right Wrist Accel")
axis[1, 0].plot(time_in_seconds, l2_g_data)
axis[1, 0].set_title("Left Forearm Gyro")
axis[1, 1].plot(time_in_seconds, l2_a_data)
axis[1, 1].set_title("Left Forearm Accel")
axis[1, 2].plot(time_in_seconds, r2_g_data)
axis[1, 2].set_title("Right Forearm Gyro")
axis[1, 3].plot(time_in_seconds, r2_a_data)
axis[1, 3].set_title("Right Forearm Accel")
axis[2, 0].plot(time_in_seconds, l3_g_data)
axis[2, 0].set_title("Left Shoulder Gyro")
axis[2, 1].plot(time_in_seconds, l3_a_data)
axis[2, 1].set_title("Left Shoulder Accel")
axis[2, 2].plot(time_in_seconds, r3_g_data)
axis[2, 2].set_title("Right Shoulder Gyro")
axis[2, 3].plot(time_in_seconds, r3_a_data)
axis[2, 3].set_title("Right Shoulder Accel")
figure.legend(labels, loc='lower right', prop={'size': 6})
figure.tight_layout()


plt.setp(axis, ylim=(-40, 40))
plt.show()