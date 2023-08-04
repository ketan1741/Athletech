import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import warnings
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning

# Suppress the FutureWarning from sklearn
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('gaze_data.csv')

# Convert the 'Timestamp' column to pandas datetime format with the appropriate format specified
# data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%H:%M:%S.%f')
data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit = 's')

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

# Filter out rows with 'None' in 'Eye Center'
valid_data = data.dropna(subset=['Eye Center'])  # Drop rows with missing eye center data

if not valid_data.empty:
    X = np.vstack(valid_data['Eye Center'])  # Convert the tuples to a 2D NumPy array
    X = X.astype(float)  # Convert the elements to float to avoid the 'ValueError'
    
    # Perform KMeans clustering with 5 clusters (or choose your desired number of clusters)
    num_clusters = 9
    kmeans = KMeans(n_clusters=num_clusters)  
    kmeans.fit(X)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    
    # Plot the eye center distribution with clusters
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='rainbow', s=50)
    plt.scatter(centers[:, 0], centers[:, 1], c='black', marker='x', s=100)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title(f'Eye Center clustering with {num_clusters} Clusters')
    plt.colorbar()
    plt.savefig('eye_center_clustering.png')
    plt.show()
else:
    print("Insufficient data for visualization.")
