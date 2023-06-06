import toml
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def main() -> None:
    # Get cumulative exits per time, for different pedestrians' initial positions
    rounds = 1
    simulations = run_simulations(rounds)

    # Plot cumulative exits per time
    for j in range(rounds):
        times = simulations[j][0]["times"]
        exits = simulations[j][0]["exits"]

        plt.plot(times, exits)

    plt.xlabel("Tiempo (s)", fontsize=18)
    plt.ylabel("Egresos", fontsize=18)

    plt.tight_layout()
    plt.grid()
    plt.savefig("out/exits_per_dt.png")
    plt.show()

    # Compute the average time for each amount of exits, given a step of 10 exits.
    # E.g. average time for 10 exits, average time for 20 exits, etc.
    exits_step = 10
    max_exits = 400
    average_times = {}
    average_times2 = {}
    average_times3 = {}

    for j in range(rounds):
        times = np.array(simulations[j][0]["times"])
        exits = np.array(simulations[j][0]["exits"])

        for exit_count in range(0, max_exits + 1, exits_step):
            # Find the first occurrance of the given step in the exits array
            index = np.where(exits >= exit_count)[0][0] # the equality might not exist, so we take the first greater value
            try:
                average_times[exit_count].append(times[index])
            except KeyError:
                average_times[exit_count] = [times[index]]

    for j in range(rounds):
        times2 = np.array(simulations[j][1]["times"])
        exits2 = np.array(simulations[j][1]["exits"])

        for exit_count in range(0, max_exits + 1, exits_step):
            # Find the first occurrance of the given step in the exits array
            index = np.where(exits2 >= exit_count)[0][0] # the equality might not exist, so we take the first greater value
            try:
                average_times2[exit_count].append(times2[index])
            except KeyError:
                average_times2[exit_count] = [times2[index]]

    for j in range(rounds):
        times3 = np.array(simulations[j][2]["times"])
        exits3 = np.array(simulations[j][2]["exits"])

        for exit_count in range(0, max_exits + 1, exits_step):
            # Find the first occurrance of the given step in the exits array
            index = np.where(exits3 >= exit_count)[0][0] # the equality might not exist, so we take the first greater value
            try:
                average_times3[exit_count].append(times3[index])
            except KeyError:
                average_times3[exit_count] = [times3[index]]

    # Iterate over the `average_times` keys and values, and compute the average time for each exit count
    exits = []
    times = []
    errors = []
    exits2 = []
    times2 = []
    errors2 = []
    exits3 = []
    times3 = []
    errors3 = []

    for exit_count, _times in average_times.items():
        average_time = np.mean(_times)
        std = np.std(_times)
        exits.append(exit_count)
        times.append(average_time)
        errors.append(std)

    for exit_count, _times in average_times2.items():
        average_time = np.mean(_times)
        std = np.std(_times)
        exits2.append(exit_count)
        times2.append(average_time)
        errors2.append(std)


    for exit_count, _times in average_times3.items():
        average_time = np.mean(_times)
        std = np.std(_times)
        exits3.append(exit_count)
        times3.append(average_time)
        errors3.append(std)

    # Plot exit count vs average time, with horizontal error bars
    plt.errorbar(times, exits, xerr=errors, fmt='o', capsize=3, markersize=3, color="black")
    plt.errorbar(times2, exits2, xerr=errors2, fmt='o', capsize=3, markersize=3, color="black")
    plt.errorbar(times3, exits3, xerr=errors3, fmt='o', capsize=3, markersize=3, color="black")
    plt.plot(times, exits, label="1 puerta d=2.4", color="red")  # Connect markers with straight lines
    plt.plot(times2, exits2, label="1 puerta d=1.2", color="green")  # Connect markers with straight lines
    plt.plot(times3, exits3, label="2 puertas d=1.2", color="blue")  # Connect markers with straight lines

    plt.xlabel("Tiempo (s)", fontsize=18)
    plt.ylabel("Egresos", fontsize=18)

    plt.tight_layout()
    plt.grid()
    plt.legend()
    plt.savefig("out/avg_exits_per_dt.png")
    plt.show()


    collisions1 = [116454, 120064, 123694, 123017, 119262, 116371, 116084, 121610, 116457, 121077]
    collisions2 = [313203, 317533, 316586, 320860, 325217, 311116, 317800, 317890, 322461, 321654]
    collisions3 = [108520, 114534, 112216, 111144, 112379, 107497, 108773, 113063, 107773, 111848]

    mean1 = np.mean(collisions1)
    std1 = np.std(collisions1)
    mean2 = np.mean(collisions2)
    std2 = np.std(collisions2)
    mean3 = np.mean(collisions3)
    std3 = np.std(collisions3)

    # Configuración de los datos para el gráfico de barras
    means = [mean1, mean2, mean3]
    stds = [std1, std2, std3]
    labels = ['1 puerta d=2.4', '1 puertas d=1.2', '2 puertas d=1.2']
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(x, means, width, yerr=stds, capsize=4)

    # Etiquetas, título y leyenda
    ax.set_ylabel('Colisiones', fontsize=18)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=14)

    plt.tight_layout()
#     plt.savefig("out/collisions_per_door.png")
    plt.show()

def run_simulations(rounds: int = 5):
    with open("config.toml", "r") as f:
        config = toml.load(f)
    
    simulations = {}

    for j in range(rounds):
        simulations[j] = {}

        # Create particles
        subprocess.run(["python", "generate_pedestrians.py"])

        for amount_doors in range(3):
            print(f"Running with {amount_doors}")
            if amount_doors == 0:
                config["simulation"]["exitWidth"] = 2.4
            else:
                config["simulation"]["exitWidth"] = 1.2

            if amount_doors == 2:
                config["simulation"]["amountDoors"] = 2
            else:
                config["simulation"]["amountDoors"] = 1
            simulations[j][amount_doors] = {}

            with open("config.toml", "w") as f:
                toml.dump(config, f)

            # Run simulation
            subprocess.run(["java", "-jar", "./target/dinamica-peatonal-1.0-SNAPSHOT-jar-with-dependencies.jar"])

            # Save event times
            with open(config["files"]["benchmark"], 'r') as file:
                lines = file.readlines()

            simulations[j][amount_doors]["times"] = []
            simulations[j][amount_doors]["exits"] = []

            for line in lines:
                data = line.split()
                time = float(data[0])
                cumulative_exits = int(data[1])
                simulations[j][amount_doors]["times"].append(time)
                simulations[j][amount_doors]["exits"].append(cumulative_exits)

    return simulations


if __name__ == '__main__':
    main()