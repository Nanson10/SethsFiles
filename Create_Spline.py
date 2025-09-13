import numpy as np
import matplotlib.pyplot as plt
import scipy as scipy
# from scipy.interpolate import *
# from scipy.integrate import simpson
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate

# Read data
file_path = r"C:\Users\schae\Documents\Purdue_Solar_Racing\Calculation_Tool\Coords2.txt"  # Change to your file path
data = np.loadtxt(file_path)

lat, lon, elev = data[:, 0], data[:, 1], data[:, 2]

m_to_miles = 1/1609

# Convert lat/lon to meters
R = 6371000  # Earth’s radius in meters
lat_ref = np.mean(lat)  # Reference latitude to reduce distortion

x_meters = (lon - lon[0]) * (np.pi / 180) * R * np.cos(np.radians(lat_ref))  # Longitude to meters
y_meters = (lat - lat[0]) * (np.pi / 180) * R  # Latitude to meters
z_meters = elev  # Elevation is already in meters

dx = np.diff(x_meters)
dy = np.diff(y_meters)
dz = np.diff(z_meters)
# print(dx)
# raise ValueError

diffs = np.array([dx, dy, dz]).T
# print(diffs)
# print(np.sum(np.sqrt(dx**2+dy**2+dz**2)))
est_arc_len = np.sum(np.linalg.norm(diffs, axis=1))

print(f"{est_arc_len * m_to_miles} miles")

spline, u = scipy.interpolate.splprep()
raise ValueError
# Parameterization
t = np.linspace(0, 1, len(lat))
t_fine = np.linspace(0, 1, 300)  # Fine grid for smoothness

# Fit splines
spline_x = make_interp_spline(t, x_meters, k=3)
spline_y = make_interp_spline(t, y_meters, k=3)
spline_z = make_interp_spline(t, z_meters, k=3)

# Compute derivatives
dx_dt = spline_x.derivative()
dy_dt = spline_y.derivative()
dz_dt = spline_z.derivative()

# Evaluate derivatives on fine grid
dx = dx_dt(t_fine)
dy = dy_dt(t_fine)
dz = dz_dt(t_fine)

# Arc length integral
ds_dt = np.sqrt(dx**2 + dy**2 + dz**2)

spline_length = simpson(ds_dt, t_fine)  # Use Simpson's rule for integration

print(f"Approximate Spline Length: {spline_length:.3f} meters")

# Plot
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Scatter original points
ax.scatter(x_meters[0], y_meters[0], z_meters[0], color='red', label='Original Points')

# Plot spline curve
x_smooth = spline_x(t_fine)
y_smooth = spline_y(t_fine)
z_smooth = spline_z(t_fine)
ax.plot(x_smooth, y_smooth, z_smooth, color='blue', label='Spline Curve')

ax.set_xlabel("X (meters)")
ax.set_ylabel("Y (meters)")
ax.set_zlabel("Elevation (m)")
ax.legend()
plt.show()
