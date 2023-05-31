import toml
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def main() -> None:
    # Get cumulative exits per time, for different pedestrians' initial positions
    simulations = run_simulations()

    print("\n\n--- AVERAGE FLOW RATES ---")
    print(simulations)


def run_simulations(rounds: int = 3):
    with open("config.toml", "r") as f:
        config = toml.load(f)

    exit_width = config["benchmarks"]["exitWidths"]
    pedestrians = config["benchmarks"]["pedestrians"]
    
    # Average flow rate for each exit width
    simulations = {}

    for i, d in enumerate(exit_width):
        config["simulation"]["exitWidth"] = d
        config["simulation"]["pedestrians"] = pedestrians[i]

        print(f"Running simulation with {d=} and pedestrians={pedestrians[i]}")

        with open("config.toml", "w") as f:
            toml.dump(config, f)

        # Save the times of each round for the current `y`
        flow_rates = []

        for _ in range(rounds):
            previous_exits = 0
            
            # Create particles
            subprocess.run(["python", "generate_pedestrians.py"])

            # Run simulation
            subprocess.run(["java", "-jar", "./target/dinamica-peatonal-1.0-SNAPSHOT-jar-with-dependencies.jar"])

            # Save event times
            with open(config["files"]["benchmark"], 'r') as file:
                lines = file.readlines()

            for line in lines:
                data = line.split()
                cumulative_exits = int(data[1])
                flow_rates.append(cumulative_exits - previous_exits)
                previous_exits = cumulative_exits

        simulations[d] = (np.mean(flow_rates), np.std(flow_rates))

    return simulations


if __name__ == '__main__':
    main()