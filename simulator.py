from argparse import ArgumentParser
import heapq
import numpy as np


def parseArguments():
    parser = ArgumentParser()
    parser.add_argument('T', type=float, help='Simulation time')
    parser.add_argument('N', type=int, help='Number of input ports')
    parser.add_argument('M', type=int, help='Number of output ports')
    
    # Parse the initial arguments
    args, _ = parser.parse_known_args()

    # Get the values of N and M
    N = args.N
    M = args.M
    total_probs = N * M

    parser.add_argument('probs', type=float, nargs=total_probs, help='Probabilities for each input-output pair')
    parser.add_argument('arrival_rates', type=float, nargs=N, help='Arrival rates for each input port')
    parser.add_argument('ouput_queue_sizes', type=float, nargs=M, help='Output queue sizes for each output port')
    parser.add_argument('handling_rates', type=float, nargs=M, help='Handling rates for each output port')

    # Parse all arguments
    args = parser.parse_args()
    args.probs = np.array(args.probs).reshape(N, M)
    return args


class Event:
    def __init__(self, arrival_time, transmission_time, transmission_start=None, port=None):
        self.arrival_time = arrival_time
        self.transmission_time = transmission_time
        self.transmission_start = transmission_start
        self.inputPort = port

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

    def __eq__(self, other):
        if other is None:
            return False
        return self.arrival_time == other.arrival_time

class Simulator:
    def __init__(self ,T, N, M, queue_sizes, arrival_rates, handle_rates, probabilities_matrix,):
        self.start = 0
        self.max_time = T
        self.input_ports = N
        self.output_ports = M
        self.probabilities_matrix = probabilities_matrix
        self.arrival_rates = arrival_rates
        self.queues_sizes = queue_sizes
        self.handle_rates = handle_rates

        self.queues = [[] for _ in range(M)]
        self.events = []

        self.Y = 0
        self.y = [0 for _ in range(M)]
        self.X = 0
        self.x = [0 for _ in range(M)]
        self.end_time = 0
        self.TotalWaitTime = 0
        self.TotalServiceTime = 0
    
    def runSimulation(self):

      for inputPort, arrival_rate in enumerate(self.arrival_rates):
        interarrival_time = np.random.exponential( 1 / arrival_rate) # time between arrivals is distributed exp(1/lambda) in a poisson(lambda) distribution
        arrival_time = interarrival_time + self.start
        if arrival_time <= self.max_time:
          new_event = Event(arrival_time, None, None, inputPort)
          heapq.heappush(self.events, new_event)
      
      while self.events:
        event = heapq.heappop(self.events) # get the event with minimum arrival time to process it
        prev_arrival_time = event.arrival_time
        
        output_port = np.random.choice(range(self.output_ports), p=self.probabilities_matrix[event.inputPort])
        self.processOutputPort(output_port, prev_arrival_time) # event.arrival_time is the time at which the event is transmitted from inputPort to outputPort i.e current_time
        
        interarrival_time = np.random.exponential(1 / self.arrival_rates[event.inputPort])
        new_arrival_time = interarrival_time + prev_arrival_time
        
        if new_arrival_time <= self.max_time:
          new_arrival_time = interarrival_time + event.arrival_time
          new_event = Event(new_arrival_time, None, None, event.inputPort) # get new events for inputPorts
          heapq.heappush(self.events, new_event)

      return self.finalize()
    

    def processOutputPort(self, index, current_time):   
        self.queues[index] = [e for e in self.queues[index] if current_time < (e.transmission_start + e.transmission_time)] # remove already processed events
        
        if len(self.queues[index]) >= self.queues_sizes[index] + 1:
            self.x[index] += 1 # throw event
        else:
            transmission_time = np.random.exponential(1 / self.handle_rates[index])
            if not self.queues[index]: # not delay because queue is empty
              transmission_start = current_time 
            else:
              # event has to wait till all events before have been transmitted, use the last event in the queue and start transmitting after its done transmitting (definition depends on previous events)
              transmission_start = self.queues[index][len(self.queues[index])-1].transmission_start + self.queues[index][len(self.queues[index])-1].transmission_time
            
            event = Event(current_time, transmission_time, transmission_start, None)
            self.queues[index].append(event)

            self.TotalWaitTime += (transmission_time + (transmission_start - current_time))
            self.TotalServiceTime += transmission_time
            self.y[index] += 1 # correctly handled event
    
    def finalize(self):
      self.Y = sum(self.y)
      self.X = sum(self.x)

      process_end_times = [self.queues[i][-1].transmission_start + self.queues[i][-1].transmission_time for i in range(self.output_ports) if self.queues[i]]
      if process_end_times:
          self.end_time = max(process_end_times)
          
      #collect statistics
      t_w = self.TotalWaitTime / self.Y
      t_s = self.TotalServiceTime / self.Y

      handled_events_per_queue_str = ' '.join(map(str, self.y))
      thrown_events_per_queue_str = ' '.join(map(str, self.x))
      formatted_string = (
              f"{self.Y} "
              f"{handled_events_per_queue_str} "
              f"{self.X} "
              f"{thrown_events_per_queue_str} "
              f"{self.end_time} "
              f"{t_w} "
              f"{t_s}"
      )
      print(formatted_string)
      return t_w, t_s

if __name__ == "__main__":
    args = parseArguments()
    simulator = Simulator(args.T, args.N, args.M, args.ouput_queue_sizes, args.arrival_rates, args.handling_rates, args.probs)
    simulator.runSimulation()
