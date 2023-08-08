import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import json
import pytz

with open('data.json', 'r') as f:
        data = json.load(f)

target_value = 1  # Replace this with the value you're looking for

matching_death_times = []
matching_kills_times = []

est_tz = pytz.timezone('US/Eastern')

# Search for the outer key that corresponds to the target value within the inner dictionary
for outer_key, inner_dict in data.items():
    if "player_get_killed" in inner_dict and inner_dict["player_get_killed"] == target_value:
        utc_datetime = datetime.datetime.utcfromtimestamp(float(outer_key))
        datetime_est_string = utc_datetime.replace(tzinfo=pytz.utc).astimezone(est_tz).strftime('%Y-%m-%d %H:%M:%S')
        datetime_est = datetime.datetime.strptime(datetime_est_string, '%Y-%m-%d %H:%M:%S')
        matching_death_times.append(datetime_est)
    if "player_kill_other" in inner_dict and inner_dict["player_kill_other"] == target_value:
        utc_datetime = datetime.datetime.utcfromtimestamp(float(outer_key))
        datetime_est_string = utc_datetime.replace(tzinfo=pytz.utc).astimezone(est_tz).strftime('%Y-%m-%d %H:%M:%S')
        datetime_est = datetime.datetime.strptime(datetime_est_string, '%Y-%m-%d %H:%M:%S')
        matching_kills_times.append(datetime_est)

mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['r', 'b', 'y'])

times = []
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

with open("imu_data.txt", 'r') as file:
    data = file.readlines()
    for i in data:
        temp = i.strip().split(",")
        tempfloat = []
        for j in range(len(temp)):
            if j == 0:
                time_str = temp[j]

                date = datetime.datetime(2023, 8, 4, 12, 30, 0)  #Change the date if data.json change
                date = date.date()

                time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")

                # Combine the date with the time
                combined_datetime = datetime.datetime.combine(date, time_obj.time())
                times.append(combined_datetime)
            elif ((j % 6)-1) > 3:
                if(float(temp[j]) > 40):
                    tempfloat.append(40)
                elif(float(temp[j]) < -40):
                    tempfloat.append(-40)
                else:
                    tempfloat.append(float(temp[j]))
            else:
                if(float(temp[j]) > 34.9):
                    tempfloat.append(34.91)
                elif(float(temp[j]) < -34.9):
                    tempfloat.append(-34.91)
                else:
                    tempfloat.append(float(temp[j]))

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
avgtime = 0
for i in range(len(times)-1):
    avgtime += (times[i+1] - times[i]).total_seconds()
avgtime /= (len(times)-1)
print("Avg. Time between samples: ", avgtime)

labels = ['x', 'y', 'z', 'Dead time', 'Kill time']

# Create three figures, each with four subplots
fig1, axs1 = plt.subplots(2, 2, figsize=(10, 8))
fig2, axs2 = plt.subplots(2, 2, figsize=(10, 8))
fig3, axs3 = plt.subplots(2, 2, figsize=(10, 8))

axs1[0, 0].plot(times, l1_g_data)
axs1[0, 0].set_title("Left Wrist Gyro")
axs1[0, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs1[0, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs1[0, 0].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs1[0, 0].axvline(kill_time, color='r', linestyle='--')

axs1[0, 1].plot(times, l1_a_data)
axs1[0, 1].set_title("Left Wrist Accel")
axs1[0, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs1[0, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs1[0, 1].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs1[0, 1].axvline(kill_time, color='r', linestyle='--')

axs1[1, 0].plot(times, r1_g_data)
axs1[1, 0].set_title("Right Wrist Gyro")
axs1[1, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs1[1, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs1[1, 0].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs1[1, 0].axvline(kill_time, color='r', linestyle='--')

axs1[1, 1].plot(times, r1_a_data)
axs1[1, 1].set_title("Right Wrist Accel")
axs1[1, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs1[1, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs1[1, 1].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs1[1, 1].axvline(kill_time, color='r', linestyle='--')

axs2[0, 0].plot(times, l2_g_data)
axs2[0, 0].set_title("Left Forearm Gyro")
axs2[0, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs2[0, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs2[0, 0].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs2[0, 0].axvline(kill_time, color='r', linestyle='--')

axs2[0, 1].plot(times, l2_a_data)
axs2[0, 1].set_title("Left Forearm Accel")
axs2[0, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs2[0, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs2[0, 1].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs2[0, 1].axvline(kill_time, color='r', linestyle='--')

axs2[1, 0].plot(times, r2_g_data)
axs2[1, 0].set_title("Right Forearm Gyro")
axs2[1, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs2[1, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs2[1, 0].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs2[1, 0].axvline(kill_time, color='r', linestyle='--')

axs2[1, 1].plot(times, r2_a_data)
axs2[1, 1].set_title("Right Forearm Accel")
axs2[1, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs2[1, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs2[1, 1].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs2[1, 1].axvline(kill_time, color='r', linestyle='--')

axs3[0, 0].plot(times, l3_g_data)
axs3[0, 0].set_title("Left Shoulder Gyro")
axs3[0, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs3[0, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs3[0, 0].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs3[0, 0].axvline(kill_time, color='r', linestyle='--')

axs3[0, 1].plot(times, l3_a_data)
axs3[0, 1].set_title("Left Shoulder Accel")
axs3[0, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs3[0, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs3[0, 1].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs3[0, 1].axvline(kill_time, color='r', linestyle='--')

axs3[1, 0].plot(times, r3_g_data)
axs3[1, 0].set_title("Right Shoulder Gyro")
axs3[1, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs3[1, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs3[1, 0].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs3[1, 0].axvline(kill_time, color='r', linestyle='--')

axs3[1, 1].plot(times, r3_a_data)
axs3[1, 1].set_title("Right Shoulder Accel")
axs3[1, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
axs3[1, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
for death_time in matching_death_times:
    axs3[1, 1].axvline(death_time, color='black', linestyle='--')
for kill_time in matching_kills_times:
    axs3[1, 1].axvline(kill_time, color='r', linestyle='--')

fig1.legend(labels, loc='lower right', prop={'size': 6})
fig2.legend(labels, loc='lower right', prop={'size': 6})
fig3.legend(labels, loc='lower right', prop={'size': 6})
fig1.tight_layout()
fig2.tight_layout()
fig3.tight_layout()


plt.setp(axs1, ylim=(-50, 50))
plt.setp(axs2, ylim=(-50, 50))
plt.setp(axs3, ylim=(-50, 50))
plt.show()