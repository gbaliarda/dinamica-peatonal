import toml
import json
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def main() -> None:
    # Get cumulative exits per time, for different pedestrians' initial positions
    rounds = 5
    simulations = run_simulations(rounds)

    for j in range(rounds):
        times = simulations[j]["times"]
        exits = simulations[j]["exits"]

        plt.plot(times, exits, label=f"Simulación {j+1}")

    plt.xlabel("Tiempo (s)", fontsize=18)
    plt.ylabel("Egresos", fontsize=18)

    plt.tight_layout()
    plt.legend()
    plt.grid()
    plt.savefig("out/exits_per_dt.png")
    plt.show()


def run_simulations(rounds: int = 5):
    with open("config.toml", "r") as f:
        config = toml.load(f)
    
    simulations = {}

    for j in range(rounds):
        simulations[j] = {}
        
        # Create particles
        subprocess.run(["python", "generate_pedestrians.py"])

        # Run simulation
        subprocess.run(["java", "-jar", "./target/dinamica-peatonal-1.0-SNAPSHOT-jar-with-dependencies.jar"])

        # Save event times
        with open(config["files"]["benchmark"], 'r') as file:
            lines = file.readlines()

        simulations[j]["times"] = []
        simulations[j]["exits"] = []

        for line in lines:
            data = line.split()
            time = float(data[0])
            cumulative_exits = int(data[1])
            simulations[j]["times"].append(time)
            simulations[j]["exits"].append(cumulative_exits)
    
    return simulations


if __name__ == '__main__':
    main()