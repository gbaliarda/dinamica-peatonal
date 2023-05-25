import tomllib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import EllipseCollection

def main() -> None:
    config = load_config()

    with open(config["files"]["output"], 'r') as file:
        lines = file.readlines()

    events = {}
    time = None

    for line in lines:
        data = line.split()

        if len(data) == 1:
            time = float(data[0])
            events[time] = []
        else:
            particle = {
                'x': float(data[0]),
                'y': float(data[1]),
                'v': float(data[2]),
                'radius': float(data[3]),
            }
            events[time].append(particle)

    # Update animation frame
    def update(frame):
        t = list(events.keys())[frame]
        particles = events[t]

        x = [p['x'] for p in particles]
        y = [p['y'] for p in particles]
        diameters = [p['radius'] * 2 for p in particles]

        ax.clear()

        # Create the EllipseCollection as a scatter plot, to be able to use the `diameters` array
        # Ref: https://stackoverflow.com/questions/33094509/correct-sizing-of-markers-in-scatter-plot-to-a-radius-r-in-matplotlib
        ax.add_collection(EllipseCollection(widths=diameters, heights=diameters, angles=0, units='xy', edgecolors='k', offsets=list(zip(x, y)), transOffset=ax.transData))

        ax.set_aspect('auto')
        ax.set_xlim([0, 20])
        ax.set_ylim([0, 20])
        ax.set_title(f'Time: {t:.2f}')

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 5))

    # Create animation
    anim = animation.FuncAnimation(fig, update, frames=len(events))

    # Save animation as mp4
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=20, bitrate=1800)

    anim.save('out/animation.mp4', writer=writer)


def load_config() -> dict[str, any]:
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    return config

if __name__ == '__main__':
    main()