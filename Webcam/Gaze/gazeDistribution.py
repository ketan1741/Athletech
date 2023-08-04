import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('gaze_data.csv')

# Convert the 'Timestamp' column to pandas datetime format with the appropriate format specified
data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit = 's')

# Create a recursive 5-second interval column
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

# Group the data by '5s Interval' and create separate distribution graphs
for interval, group in data.groupby('5s Interval'):
    # Filter out rows with 'None' in 'Eye Center'
    valid_group = group.dropna(subset=['Eye Center'])  # Drop rows with missing eye center data
    
    if not valid_group.empty:
        X = np.vstack(valid_group['Eye Center'])  # Convert the tuples to a 2D NumPy array
        X = X.astype(float)  # Convert the elements to float to avoid the 'ValueError'
        
        # Plot the eye center distribution without CS:GO image
        plt.scatter(X[:, 0], X[:, 1], s=50)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title(f'Eye Center Distribution (Interval {interval*5}-{(interval+1)*5} seconds)')
        
        # Save the figure directly into the "clustering_graph" folder
        plt.savefig(f"distribution_graph/eye_center_distribution_interval_{interval}.png")
        plt.close()
    else:
        print(f"Skipping interval {interval*5}-{(interval+1)*5} seconds due to insufficient data for visualization.")
