import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# Set up the figure and axis
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.axis('off')

# Create a scatter object
scatter = ax.scatter([], [], [], c=[], cmap='hsv', s=5)

# Initialization function
def init():
    scatter._offsets3d = ([], [], [])
    scatter.set_array([])
    return scatter,

# Animation function
def animate(i):
    t = np.linspace(0, 4 * np.pi, 1000)
    
    # Layer 1: Chaotic trigonometric attractors
    x1 = np.sin(3 * t + i * 0.1) * np.cos(2 * t + i * 0.1) * np.sin(5 * t + i * 0.1)
    y1 = np.cos(3 * t + i * 0.1) * np.sin(2 * t + i * 0.1) * np.cos(5 * t + i * 0.1)
    z1 = np.sin(4 * t + i * 0.1) * np.cos(3 * t + i * 0.1) * np.sin(6 * t + i * 0.1)

    # Layer 2: Polar transformations
    r2 = np.sin(4 * t + i * 0.2) * np.cos(3 * t + i * 0.2)
    x2 = r2 * np.cos(t)
    y2 = r2 * np.sin(t)
    z2 = r2 * np.sin(t)

    # Layer 3: Dynamic geometry
    x3 = np.sin(5 * t + i * 0.3) * np.cos(4 * t + i * 0.3) * np.sin(7 * t + i * 0.3)
    y3 = np.cos(5 * t + i * 0.3) * np.sin(4 * t + i * 0.3) * np.cos(7 * t + i * 0.3)
    z3 = np.sin(6 * t + i * 0.3) * np.cos(5 * t + i * 0.3) * np.sin(8 * t + i * 0.3)

    # Combine layers
    x_combined = x1 + x2 * 0.5 + x3 * 0.25
    y_combined = y1 + y2 * 0.5 + y3 * 0.25
    z_combined = z1 + z2 * 0.5 + z3 * 0.25

    scatter._offsets3d = (x_combined, y_combined, z_combined)
    scatter.set_array(np.linspace(0, 1, len(x_combined)))
    return scatter,

# Create the animation
ani = animation.FuncAnimation(fig, animate, init_func=init,
                              frames=256, interval=30, blit=True)

plt.show()
