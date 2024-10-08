import simulator
import numpy as np
import matplotlib.pyplot as plt

class Myargs:
    def __init__(self, T, queue_sizes, N=1, M=1, probabilities=[[1]], arrival_rates=[9], handling_rates=[12]):
        self.T = T
        self.N = N
        self.M = M
        self.probs = probabilities
        self.arrival_rates = arrival_rates
        self.ouput_queue_sizes = queue_sizes
        self.handling_rates = handling_rates
        
def plot(queue_sizes):
    num_runs = 10
    T_values = [10, 100, 500, 1000, 1500, 2000, 2500]

    avg_times = []
    avg_times_per_run = []
    for T in T_values:
        args = Myargs(T, queue_sizes)
        for _ in range(num_runs):
            sim = simulator.Simulator(args.T, args.N, args.M, args.ouput_queue_sizes, args.arrival_rates, args.handling_rates, args.probs)
            avg_times_per_run.append(sim.runSimulation()[0])
        avg_time = np.mean(avg_times_per_run)
        avg_times.append(avg_time)
        
    colors = plt.cm.viridis(np.linspace(0, 1, len(T_values)))  # Generate colors from colormap

    for i, color in enumerate(colors):
        plt.scatter(T_values[i], avg_times[i], marker='o', color=color, label=f'T = {T_values[i]}')

    # Plotting
    plt.xlabel('Simulation Time (T) [seconds]')
    plt.ylabel('Average (t_w) [seconds]')
    plt.title('Average Time vs Simulation Time')
    plt.grid(True)
    # plt.show()
    plt.savefig(f'dry_queue_size={queue_sizes[0]}.png', bbox_inches='tight')
    plt.clf()

if __name__ == "__main__":
    plot(queue_sizes=[1000])
    plot(queue_sizes=[5])