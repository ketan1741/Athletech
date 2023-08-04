import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import cv2

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('gaze_data.csv')

# Convert the 'Timestamp' column to pandas datetime format with the appropriate format specified
data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%H:%M:%S.%f')

# Create a recursive 10-second interval column
data['5s Interval'] = (data['Timestamp'] - data['Timestamp'].min()).dt.total_seconds() // 5

# Define a function to parse the pupil data from the string format
def parse_pupil_data(pupil_str):
    try:
        return literal_eval(pupil_str)
    except (ValueError, SyntaxError, TypeError):
        return None

# Apply the parsing function to 'Left Pupil' and 'Right Pupil' columns
data['Left Pupil'] = data['Left Pupil'].apply(parse_pupil_data)
data['Right Pupil'] = data['Right Pupil'].apply(parse_pupil_data)

# Calculate the eye center for each row
def calculate_eye_center(row):
    left_pupil = row['Left Pupil']
    right_pupil = row['Right Pupil']
    if left_pupil is not None and right_pupil is not None:
        return ((left_pupil[0] + right_pupil[0]) // 2, (left_pupil[1] + right_pupil[1]) // 2)
    else:
        return None

data['Eye Center'] = data.apply(calculate_eye_center, axis=1)

# Group the data by '10s Interval' and create separate distribution graphs
for interval, group in data.groupby('5s Interval'):
    # Filter out rows with 'None' in 'Eye Center'
    valid_group = group.dropna(subset=['Eye Center'])  # Drop rows with missing eye center data
    
    if not valid_group.empty:
        X = np.vstack(valid_group['Eye Center'])  # Convert the tuples to a 2D NumPy array
        X = X.astype(float)  # Convert the elements to float to avoid the 'ValueError'
        
        # Calculate the range of eye concentration data
        x_min, x_max = np.min(X[:, 0]), np.max(X[:, 0])
        y_min, y_max = np.min(X[:, 1]), np.max(X[:, 1])
        
        # Check for zero denominators to avoid division by zero
        if (x_max - x_min) == 0 or (y_max - y_min) == 0:
            print(f"Skipping interval {interval} due to zero range in eye center data.")
            continue
        
        # CS:GO captured graph resolution
        graph_width = 1920
        graph_height = 1080
        
        # Calculate the scaling factors
        x_scale = graph_width / (x_max - x_min)
        y_scale = graph_height / (y_max - y_min)
        
        # Load the CS:GO captured graph
        csgo_graph = cv2.imread("csgo.png")  # Replace "csgo.png" with the path to your CS:GO graph image
        csgo_graph = cv2.resize(csgo_graph, (graph_width, graph_height))
        
        # Overlay eye concentration markers on the CS:GO captured graph
        scaled_eye_centers = np.column_stack(((X[:, 0] - x_min) * x_scale, (X[:, 1] - y_min) * y_scale))
        
        for x, y in scaled_eye_centers:
            if np.isnan(x) or np.isnan(y):
                continue  # Skip NaN values
            cv2.circle(csgo_graph, (int(x), int(y)), 5, (0, 0, 255), -1)  # Red circle as eye concentration marker
        
        # Save the graph with eye concentration markers
        cv2.imwrite(f"csgo_covering/csgo_interval {interval*5}-{(interval+1)*5} seconds.png", csgo_graph)
    else:
        print(f"Skipping interval {interval} due to insufficient data for visualization.")
