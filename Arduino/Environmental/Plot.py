import matplotlib.pyplot as plt

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
            time = sum(float(t) * 60 ** i for i, t in enumerate(reversed(values[0].split(':'))))
            time_values.append(time)

            # Extract other values
            temperature_values.append(float(values[1]))
            pressure_values.append(float(values[2]))
            altitude_values.append(float(values[3]))
            humidity_values.append(float(values[4]))
            light_values.append(float(values[5]))
            co2_values.append(float(values[6]))

    return time_values, temperature_values, pressure_values, altitude_values, humidity_values, light_values, co2_values

# Read data from the file
file_name = 'env_data.txt'
time_values, temperature_values, pressure_values, altitude_values, humidity_values, light_values, co2_values = read_data_from_file(file_name)

# Create subplots for each parameter
fig, axs = plt.subplots(3, 2, figsize=(12, 10))
fig.suptitle('Sensor Data over Time', fontsize=16)

# Plot each parameter on its respective subplot
axs[0, 0].plot(time_values, temperature_values, 'b-', label='Temperature (°C)')
axs[0, 0].set_xlabel('Time (s)')
axs[0, 0].set_ylabel('Temperature (°C)')
axs[0, 0].legend()

axs[0, 1].plot(time_values, pressure_values, 'g-', label='Pressure (hPa)')
axs[0, 1].set_xlabel('Time (s)')
axs[0, 1].set_ylabel('Pressure (hPa)')
axs[0, 1].legend()

axs[1, 0].plot(time_values, altitude_values, 'r-', label='Altitude (m)')
axs[1, 0].set_xlabel('Time (s)')
axs[1, 0].set_ylabel('Altitude (m)')
axs[1, 0].legend()

axs[1, 1].plot(time_values, humidity_values, 'm-', label='Humidity (%)')
axs[1, 1].set_xlabel('Time (s)')
axs[1, 1].set_ylabel('Humidity (%)')
axs[1, 1].legend()

axs[2, 0].plot(time_values, light_values, 'c-', label='Light (lux)')
axs[2, 0].set_xlabel('Time (s)')
axs[2, 0].set_ylabel('Light (lux)')
axs[2, 0].legend()

axs[2, 1].plot(time_values, co2_values, 'y-', label='CO2 Concentration (ppm)')
axs[2, 1].set_xlabel('Time (s)')
axs[2, 1].set_ylabel('CO2 Concentration (ppm)')
axs[2, 1].legend()

# Adjust layout and display the plot
plt.tight_layout()
plt.show()
