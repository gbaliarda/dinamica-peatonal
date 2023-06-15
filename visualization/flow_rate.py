import toml
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def main() -> None:
    # Get cumulative exits per time, for different pedestrians' initial positions
    with open("config.toml", "r") as f:
        config = toml.load(f)

    simulations = run_simulations(config)

    exit_widths = config["benchmarks"]["exitWidths"]
    pedestrians = config["benchmarks"]["pedestrians"]

    # Plot cumulative exits per time, for each exit width
    exit_rate_comp(simulations, exit_widths, pedestrians)

    # Plot flow rate vs exit width
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

    min_slope = 2.4
    max_slope = 3.0
    step = 0.01
    slope_values = np.arange(min_slope, max_slope, step)
    slope_errors = []
    best_slope = 2.4
    error_best_slope = None

    for slope in slope_values:
        regression_error = 0
        for i in np.arange(len(exit_widths)):
            x = exit_widths[i]
            y = flow_rates[i]
            regression_error += pow(y - slope * x, 2)

        
        if error_best_slope == None or error_best_slope > regression_error:
            best_slope = slope
            error_best_slope = regression_error
        
        slope_errors.append(regression_error)
    
    plt.plot(slope_values, slope_errors)
    plt.xlabel('Pendiente', fontsize=18)
    plt.ylabel('E(Pendiente)', fontsize=18)
    plt.savefig("out/error_regression.png")
    plt.show()

    plt.errorbar(exit_widths, flow_rates, yerr=errors, fmt='o', capsize=3, markersize=4, color="black")
    plt.plot(exit_widths, [best_slope * x for x in exit_widths], color='red', label=f"y = {best_slope:.2f}d")
    plt.xlabel('Ancho de salida (m)', fontsize=18)
    plt.ylabel('Caudal (personas/s)', fontsize=18)
    plt.legend()

    plt.tight_layout()
    plt.show()


def run_simulations(config, rounds: int = 3):
    exit_width = config["benchmarks"]["exitWidths"]
    pedestrians = config["benchmarks"]["pedestrians"]
    
    # Average flow rate for each exit width
    simulations = {}
    simulations["rounds"] = rounds

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
                simulations[d][j]["times"].append(time)
                simulations[d][j]["exits"].append(cumulative_exits)
            
            # Get the stationary period, between 10 and 45 seconds
            lower_bound = np.where(np.array(simulations[d][j]["times"]) >= 10)[0][0]
            upper_bound = np.where(np.array(simulations[d][j]["times"]) <= 45)[0][-1]
            stationary_times = np.array(simulations[d][j]["times"])[lower_bound:upper_bound]
            stationary_exits = np.array(simulations[d][j]["exits"])[lower_bound:upper_bound]

            # Linear regression
            coefficients = np.polyfit(stationary_times, stationary_exits, 1)
            slope = coefficients[0]
            intercept = coefficients[1]
            # Calculate the curve of best fit
            curve = slope * stationary_times + intercept

            # PLot 1 linear regression as an example
            if j == 0 and d == 2.4:
                plt.scatter(stationary_times[::50], stationary_exits[::50], color='blue')
                plt.plot(stationary_times[::50], curve[::50], color='red', label=f"y = {slope:.2f}t + {intercept:.2f}")

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


def exit_rate_comp(simulations, exit_widths, pedestrians):
    # Plot cumulative exits per time
    for i, d in enumerate(exit_widths):
        max_exits = pedestrians[i]
        exits_step = max_exits // 20
        average_times = {}

        for j in range(simulations["rounds"]):
            times = np.array(simulations[d][j]["times"])
            exits = np.array(simulations[d][j]["exits"])

            for exit_count in range(0, max_exits + 1, exits_step):
                # Find the first occurrance of the given step in the exits array
                index = np.where(exits >= exit_count)[0][0] # the equality might not exist, so we take the first greater value
                try:
                    average_times[exit_count].append(times[index])
                except KeyError:
                    average_times[exit_count] = [times[index]]
        
        # Iterate over the `average_times` keys and values, and compute the average time for each exit count
        exits = []
        times = []
        errors = []

        for exit_count, _times in average_times.items():
            average_time = np.mean(_times)
            std = np.std(_times)
            exits.append(exit_count)
            times.append(average_time)
            errors.append(std)
        
        # Plot exit count vs average time, with horizontal error bars
        plt.errorbar(times, exits, xerr=errors, fmt='o', capsize=3, markersize=4, color="black")
        plt.plot(times, exits, label=f"d={d} ; N={max_exits}")

    plt.xlabel("Tiempo (s)", fontsize=18)
    plt.ylabel("Egresos", fontsize=18)

    plt.tight_layout()
    plt.grid()
    plt.legend()
    plt.savefig("out/flow_rate_comp.png")
    plt.show()


if __name__ == '__main__':
    main()