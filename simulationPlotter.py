import simulator
import numpy as np
import matplotlib.pyplot as plt

class Myargs:
    def __init__(self, T, N=1, M=1, probabilities=[[1]], arrival_rates=[9], queue_sizes=[1000], handling_rates=[12]):
        self.T = T
        self.N = N
        self.M = M
        self.probs = probabilities
        self.arrival_rates = arrival_rates
        self.ouput_queue_sizes = queue_sizes
        self.handling_rates = handling_rates
        
def plot():
    # Parameters
    num_runs = 10
    T_values = [10, 100, 500, 1000, 1500, 2000, 2500]  # Example: Different values of T

    # Perform multiple runs for each T value
    avg_wait_times = []
    for T in T_values:
        args = Myargs(T)
        # args = Myargs(T, queue_sizes=[5]) # change to queue_sizes=[5] for second plot!
        sim = simulator.Simulator(args.T, args.N, args.M, args.ouput_queue_sizes, args.arrival_rates, args.handling_rates, args.probs)
        avg_wait_times_per_run = [sim.run_simulation() for _ in range(num_runs)]
        avg_wait_time = np.mean(avg_wait_times_per_run)
        avg_wait_times.append(avg_wait_time)

    # Plotting
    plt.plot(T_values, avg_wait_times, marker='o')
    plt.xlabel('Simulation Time (T) [seconds]')
    plt.ylabel('Average Wait Time [seconds]')
    plt.title('Average Wait Time vs Simulation Time')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot()