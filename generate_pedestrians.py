import numpy as np
import math
import tomllib

# Configuration
with open("config.toml", "rb") as f:
  config = tomllib.load(f)
  STATIC_FILE = config["files"]["staticInput"]
  PEDESTRIAN_MIN_RADIUS = config["simulation"]["minRadius"]
  PEDESTRIAN_MAX_RADIUS = config["simulation"]["maxRadius"]
  PEDESTRIAN_AMOUNT = config["simulation"]["pedestrians"]
  BOX_LENGTH = config["simulation"]["boxLength"]

def generate_static_file():
    # Grid Length/maxDiameter x Length/maxDiameter
    amount_cells = math.floor(BOX_LENGTH / (PEDESTRIAN_MAX_RADIUS * 2))
    grid = np.zeros((amount_cells, amount_cells))

    with open(STATIC_FILE, "w") as f:
        for _ in range(PEDESTRIAN_AMOUNT):
            free_indexes = np.where(grid == 0)
            amount_indexes = len(free_indexes[0])
            if amount_indexes == 0:
                break
            x_index = np.random.randint(amount_indexes)
            y_index = np.random.randint(amount_indexes)
            index = (free_indexes[0][x_index], free_indexes[1][y_index])
            grid[index[0]][index[1]] = 1
            position_x = PEDESTRIAN_MAX_RADIUS * 2 * (index[0] + 1/2)
            position_y = PEDESTRIAN_MAX_RADIUS * 2 * (index[1] + 1/2)
            f.write(f"{position_x:.2f} {position_y:.2f}\n")


if __name__ == "__main__":
    generate_static_file()
