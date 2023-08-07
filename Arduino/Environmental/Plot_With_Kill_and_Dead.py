import matplotlib.pyplot as plt
import datetime
import json
import pytz

# Function to read data from the file
def read_data_from_file(file_name):
    time_values = []
    temperature_values = []
    pressure_values = []
    altitude_values = []
    humidity_values = []
    light_values = []
    co2_values = []

    with open(file_name, 'r') as file:
        for line in file:
            # Split the line by commas
            values = line.strip().split(',')
            
            # Extract the time value and convert it to seconds
            # Input time value
            time_str = values[0]

            # Current date or a specific date you want to associate with the time
            date = datetime.datetime(2023, 8, 4, 12, 30, 0)  # Year, Month, Day, Hour, Minute, Second
            date = date.date()  # You can replace this with a specific date if needed

            # Parse the input time value and create a datetime object
            time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")

            # Combine the date with the time
            combined_datetime = datetime.datetime.combine(date, time_obj.time())
            time_values.append(combined_datetime)

            # Extract other values
            temperature_values.append(float(values[1]))
            pressure_values.append(float(values[2]))
            altitude_values.append(float(values[3]))
            humidity_values.append(float(values[4]))
            light_values.append(float(values[5]))
            co2_values.append(float(values[6]))

    return time_values, temperature_values, pressure_values, altitude_values, humidity_values, light_values, co2_values

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

# Read data from the file
file_name = 'env_data.txt'
time_values, temperature_values, pressure_values, altitude_values, humidity_values, light_values, co2_values = read_data_from_file(file_name)

# Create subplots for each parameter
fig, axs = plt.subplots(3, 2, figsize=(12, 10))
fig.suptitle('Sensor Data over Time', fontsize=16)

# Plot each parameter on its respective subplot
axs[0, 0].plot(time_values, temperature_values, 'b-', label='Temperature (°C)')
for death_time in matching_death_times:
    axs[0, 0].axvline(death_time, color='black', linestyle='--')
axs[0, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
for kill_time in matching_kills_times:
    axs[0, 0].axvline(kill_time, color='r', linestyle='--')
axs[0, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
axs[0, 0].set_xlabel('Time (s)')
axs[0, 0].set_ylabel('Temperature (°C)')
axs[0, 0].legend()

axs[0, 1].plot(time_values, pressure_values, 'g-', label='Pressure (hPa)')
for death_time in matching_death_times:
    axs[0, 1].axvline(death_time, color='black', linestyle='--')
axs[0, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
for kill_time in matching_kills_times:
    axs[0, 1].axvline(kill_time, color='r', linestyle='--')
axs[0, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
axs[0, 1].set_xlabel('Time (s)')
axs[0, 1].set_ylabel('Pressure (hPa)')
axs[0, 1].legend()

axs[1, 0].plot(time_values, altitude_values, 'r-', label='Altitude (m)')
for death_time in matching_death_times:
    axs[1, 0].axvline(death_time, color='black', linestyle='--')
axs[1, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
for kill_time in matching_kills_times:
    axs[1, 0].axvline(kill_time, color='r', linestyle='--')
axs[1, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
axs[1, 0].set_xlabel('Time (s)')
axs[1, 0].set_ylabel('Altitude (m)')
axs[1, 0].legend()

axs[1, 1].plot(time_values, humidity_values, 'm-', label='Humidity (%)')
for death_time in matching_death_times:
    axs[1, 1].axvline(death_time, color='black', linestyle='--')
axs[1, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
for kill_time in matching_kills_times:
    axs[1, 1].axvline(kill_time, color='r', linestyle='--')
axs[1, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
axs[1, 1].set_xlabel('Time (s)')
axs[1, 1].set_ylabel('Humidity (%)')
axs[1, 1].legend()

axs[2, 0].plot(time_values, light_values, 'c-', label='Light (lux)')
for death_time in matching_death_times:
    axs[2, 0].axvline(death_time, color='black', linestyle='--')
axs[2, 0].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
for kill_time in matching_kills_times:
    axs[2, 0].axvline(kill_time, color='r', linestyle='--')
axs[2, 0].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
axs[2, 0].set_xlabel('Time (s)')
axs[2, 0].set_ylabel('Light (lux)')
axs[2, 0].legend()

axs[2, 1].plot(time_values, co2_values, 'y-', label='CO2 Concentration (ppm)')
for death_time in matching_death_times:
    axs[2, 1].axvline(death_time, color='black', linestyle='--')
axs[2, 1].axvline(matching_death_times[0], color='black', linestyle='--', label='Dead time')
for kill_time in matching_kills_times:
    axs[2, 1].axvline(kill_time, color='r', linestyle='--')
axs[2, 1].axvline(matching_kills_times[0], color='r', linestyle='--', label='Kill time')
axs[2, 1].set_xlabel('Time (s)')
axs[2, 1].set_ylabel('CO2 Concentration (ppm)')
axs[2, 1].legend()

# Adjust layout and display the plot
plt.tight_layout()
plt.show()
