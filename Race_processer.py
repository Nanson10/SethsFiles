import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Load the .xlsx file without headers (since there are no column labels)
file_path = r"./1_Purdue.xlsx"

# Reading the .xlsx file without headers, setting header=None to treat first row as data
df = pd.read_excel(file_path, header=None)

# Assign columns to variables based on their order (index starts at 0)
time = pd.to_datetime(df[0])  # First column (index 0), convert to datetime
speed = df[4].tolist()        # Fifth column (index 4), speed data

# Calculate change in time (in seconds) and change in speed
time_deltas = np.diff(time) / np.timedelta64(1, 's')  # Convert timedelta to seconds
speed_deltas = np.diff(speed)

# Calculate acceleration as change in speed over time (Δv / Δt)
acceleration = speed_deltas / time_deltas

# Plotting the acceleration over time (excluding the first time point since diff reduces size by 1)
plt.figure(figsize=(10, 6))
plt.plot(time[1:], acceleration, label='Acceleration (m/s²)', color='b')
plt.xlabel('Time')
plt.ylabel('Acceleration (m/s²)')
plt.title('Acceleration over Time')
plt.grid(True)
plt.legend()
plt.show()


plt.figure(figsize=(10, 6))
n, bins, patches = plt.hist(acceleration, bins=200, density=True, alpha=0.6, color='g', label='Acceleration Histogram')
(mu, sigma) = norm.fit(acceleration)
y = norm.pdf(bins, mu, sigma)
plt.plot(bins, y, 'r--', linewidth=2, label=f'Gaussian Fit\n$\\mu={mu:.2f}$, $\\sigma={sigma:.2f}$')
plt.xlabel('Acceleration (m/s²)')
plt.ylabel('Frequency (Density)')
plt.title('Histogram and Gaussian Fit of Acceleration Values')
plt.legend()
plt.grid(True)
plt.show()