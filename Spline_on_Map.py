import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import make_interp_spline

# Read data
file_path = r"C:\Users\schae\Documents\Purdue_Solar_Racing\Calculation_Tool\Coords2.txt"
data = np.loadtxt(file_path)

lat, lon, elev = data[:, 0], data[:, 1], data[:, 2]

# Parameterization
t = np.linspace(0, 1, len(lat))
t_fine = np.linspace(0, 1, 300)

# Fit splines
spline_lat = make_interp_spline(t, lat, k=3)
spline_lon = make_interp_spline(t, lon, k=3)
spline_elev = make_interp_spline(t, elev, k=3)

# Evaluate smooth curve
lat_smooth = spline_lat(t_fine)
lon_smooth = spline_lon(t_fine)
elev_smooth = spline_elev(t_fine)

# Create 3D plot
fig = go.Figure()

# Add original points
fig.add_trace(go.Scatter3d(
    x=lon, y=lat, z=elev,
    mode='markers',
    marker=dict(size=5, color='red'),
    name="Original Points"
))

# Add spline curve
fig.add_trace(go.Scatter3d(
    lon=lon_smooth, lat=lat_smooth, z=elev_smooth,
    mode='lines',
    line=dict(color='blue', width=3),
    name="Spline Curve"
))

# Configure Mapbox
fig.update_layout(
    title="3D Spline on Earth",
    margin=dict(l=0, r=0, t=40, b=0),
    scene=dict(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        zaxis_title="Elevation (m)"
    ),
    mapbox=dict(
        style="satellite",
        center={"lat": lat[0], "lon": lon[0]},
        zoom=10
    )
)

fig.show()
