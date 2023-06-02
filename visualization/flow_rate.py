import toml
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def main() -> None:
    # Get cumulative exits per time, for different pedestrians' initial positions
    simulations = run_simulations()

    with open("config.toml", "r") as f:
        config = toml.load(f)

    exit_widths = config["benchmarks"]["exitWidths"]
    flow_rates = []
    errors = []

    for d in exit_widths:
        flow_rates.append(simulations[d]["flow_rate"][0])
        errors.append(simulations[d]["flow_rate"][1])

    # Plot flow rate vs exit width, with vertical error bars
    plt.errorbar(exit_widths, flow_rates, yerr=errors, fmt='o', capsize=3, markersize=4, color="black")
    plt.plot(exit_widths, flow_rates)  # Connect markers with straight lines

    plt.xlabel("Ancho de salida (m)", fontsize=18)
    plt.ylabel("Caudal (personas/s)", fontsize=18)

    plt.tight_layout()
    plt.grid()
    plt.savefig("out/flow_rate_vs_d.png")
    plt.show()

    # Make a linear regression over the previous plot
    coefficients = np.polyfit(exit_widths, flow_rates, 1)
    slope = coefficients[0]
    intercept = coefficients[1]
    curve = slope * np.array(exit_widths) + intercept

    plt.errorbar(exit_widths, flow_rates, yerr=errors, fmt='o', capsize=3, markersize=4, color="black")
    plt.plot(exit_widths, curve, color='red', label=f"y = {slope:.2f}d + {intercept:.2f}")

    # Customize the plot
    plt.xlabel("Ancho de salida (m)", fontsize=18)
    plt.ylabel("Caudal (personas/s)", fontsize=18)

    # Save and show the plot
    plt.tight_layout()
    plt.grid()
    plt.legend()
    plt.savefig("out/flow_rate_d_regression.png")
    plt.show()


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

        simulations[d] = {}

        for j in range(rounds):
            # Create particles
            subprocess.run(["python", "generate_pedestrians.py"])

            # Run simulation
            subprocess.run(["java", "-jar", "./target/dinamica-peatonal-1.0-SNAPSHOT-jar-with-dependencies.jar"])

            # Save exits per dt
            with open(config["files"]["benchmark"], 'r') as file:
                lines = file.readlines()
            
            simulations[d][j] = {}
            simulations[d][j]["times"] = []
            simulations[d][j]["exits"] = []

            for line in lines:
                data = line.split()
                time = float(data[0])
                cumulative_exits = int(data[1])
                # Take only the times in the stationary period
                if time >= 10 and time <= 45:
                    simulations[d][j]["times"].append(time)
                    simulations[d][j]["exits"].append(cumulative_exits)

            # Linear regression
            coefficients = np.polyfit(simulations[d][j]["times"], simulations[d][j]["exits"], 1)
            slope = coefficients[0]
            intercept = coefficients[1]
            # Calculate the curve of best fit
            curve = slope * np.array(simulations[d][j]["times"]) + intercept

            # PLot 1 linear regression as an example
            if j == 0 and d == 2.4:
                plt.scatter(simulations[d][j]["times"][::50], simulations[d][j]["exits"][::50], color='blue')
                plt.plot(simulations[d][j]["times"][::50], curve[::50], color='red', label=f"y = {slope:.2f}t + {intercept:.2f}")

                # Customize the plot
                plt.xlabel("Tiempo (s)", fontsize=18)
                plt.ylabel("Egresos", fontsize=18)

                # Save and show the plot
                plt.tight_layout()
                plt.grid()
                plt.legend()
                plt.savefig("out/exits_dt_regression.png")
                plt.show()

            simulations[d][j]["flow_rate"] = slope
        
        # Get the average flow rate for current exit width, and the standard deviation
        flow_rates = [simulations[d][j]["flow_rate"] for j in range(rounds)]
        simulations[d]["flow_rate"] = (np.mean(flow_rates), np.std(flow_rates))

    return simulations


if __name__ == '__main__':
    main()