import time
from argparse import ArgumentParser
import numpy as np
import heapq # smallest element always at the top of the queue



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
    def __init__(self, arrival_time=None, output_port_index = None, input_port_index = None):
        self.arrival_time = arrival_time
        self.inserted_to_output_queue_time = None
        self.done_handling = None
        self.throwAway = False
        self.output_port_index = output_port_index
        self.input_port_index = input_port_index
        
    def __lt__(self, other):
        # Define the less than comparison method
        return self.arrival_time < other.arrival_time

    def __eq__(self, other):
       # Define the equality comparison method
        if other is None:
            return False
        return self.arrival_time == other.arrival_time

        
class InputPort:
    def __init__(self, port_index, arrival_rate, max_time, start_time, probs, num_ouput_queues):
        self.index = port_index
        self.arrival_rate = arrival_rate
        self.max_time = max_time
        self.start_time = start_time
        self.queue = []
        self.arrival_times = []
        self.probabilities = probs
        self.output_ports_num = num_ouput_queues
        self.generateArrivalTimes()
        self.enqueue_events()
        # self.generateNextArrivalTime()
        
    def generateArrivalTimes(self):
        current_time = self.start_time
        while current_time < self.max_time:
            # if events are distributed poiison(\lambda) then the difference in arrival rate is distributed exp(1/lambda)
            inter_arrival_time = np.random.exponential(1 / self.arrival_rate) 
            current_time += inter_arrival_time
            if current_time < self.max_time:
                self.arrival_times.append(current_time)
                
    def enqueue_events(self):
        for arr_time in self.arrival_times:
            heapq.heappush(self.queue, Event(arr_time, self.route_event(), self.index))
    
    # def generateNextArrivalTime(self):
    #     # if events are distributed poiison(\lambda) then the difference in arrival rate is distributed exp(1/lambda)
    #     inter_arrival_time = np.random.exponential(1 / self.arrival_rate) 
    #     if len(self.arrival_times) > 0:
    #         current_time = max(self.arrival_times) + inter_arrival_time
    #     else:
    #         current_time = self.start_time + inter_arrival_time
    #     if current_time < self.max_time:
    #         self.arrival_times.append(current_time)
    
    # def enqueue_event(self):
    #     heapq.heappush(self.queue, Event(self.generateNextArrivalTime(), self.route_event(), self.index))
                
    def route_event(self):
        chosen_port_index = np.random.choice(self.output_ports_num, p=self.probabilities)
        return chosen_port_index

    def dequeue_event(self):
        if len(self.queue) == 0:
            return None
        return heapq.heappop(self.queue)


class OutputPort:
    def __init__(self, handling_rate, queue_max_size, start_time):
        self.start = start_time
        self.handling_rate = handling_rate
        self.max_size = queue_max_size + 1 # +1 for a packet that is being sent
        self.queue = []
        self.thrown_events = 0
        self.handled_events = 0
        self.total_wait_time = 0
        self.total_service_time = 0
        self.last_handled_time = time.time()
        self.handling_times = []
        
    def generateNextArrivalTimes(self):
        current_time = time.time()
        # if events are distributed poiison(lambda) then the difference in arrival rate is distributed exp(1/lambda)
        inter_arrival_time = np.random.exponential(1 / self.handling_rate) 
        if len(self.handling_times) > 0:
            current_time = max(self.handling_times) + inter_arrival_time
        else:
            current_time += inter_arrival_time
        self.handling_times.append(current_time)

    def enqueue_event(self, event: Event):
        if len(self.queue) >= self.max_size:
            self.thrown_events += 1
            event.throwAway = True
            return
        event.inserted_to_output_queue_time = time.time()
        heapq.heappush(self.queue, event)
        if len(self.queue) > 0:
            self.generateNextArrivalTimes()

    def dequeue_event(self):
        if len(self.queue) == 0:
            return
        service_start = time.time()
        self.handled_events += 1
        popped_event = heapq.heappop(self.queue)
        popped_event.done_handling = time.time()
        self.last_handled_time = popped_event.done_handling - self.start
        self.total_wait_time += popped_event.done_handling - popped_event.inserted_to_output_queue_time # not sure about this calculation
        if len(self.handling_times) >= 2:
            self.total_service_time += (self.handling_times[1] - service_start) # not sure about this calculation
        else:
            self.total_service_time += (popped_event.done_handling - service_start) # not sure about this calculation
        self.handling_times = self.handling_times[1:] # remove first element!


class Simulator:
    def __init__(self, end_time, num_input_queues, num_output_queues, output_queues_sizes, arrival_rates, handling_rates, prob_matrix):
        self.start_time = time.time()
        self.end_time = self.start_time + end_time
        self.num_input_queues = num_input_queues
        self.num_output_queues = num_output_queues
        self.output_queues_sizes = output_queues_sizes
        self.arrival_rates = arrival_rates
        self.handling_rates = handling_rates
        self.probabilities = prob_matrix
        self.input_ports = [InputPort( i, self.arrival_rates[i], self.end_time, self.start_time, self.probabilities[i], self.num_output_queues ) for i in range(num_input_queues)]
        self.output_ports = [OutputPort( self.handling_rates[i], self.output_queues_sizes[i], self.start_time ) for i in range(num_output_queues)]

    def run_simulation(self):
        while not self.is_simulation_finished():
            next_input_event = self.get_next_input_event()
            if next_input_event != None:
                self.process_input_event(next_input_event)
            next_output_events = self.get_next_output_events()
            if next_output_events != None:
                self.process_output_events(next_output_events)
        avg_wait_time = self.finalize_simulation()
        return avg_wait_time

    def is_simulation_finished(self):
        return all(not input_port.queue for input_port in self.input_ports) and all(not output_port.queue for output_port in self.output_ports)

    def get_next_input_event(self):
        next_events = [input_port.queue[0] for input_port in self.input_ports if input_port.queue]
        # Filter events to only those with arrival times greater than or equal to current simulation time
        next_events = [event for event in next_events if event.arrival_time <= time.time()]
        if next_events:
            return min(next_events, key=lambda event: event.arrival_time)
        return None
    
    def get_next_output_events(self):
        current_time = time.time()
        next_events = []
        for output_port in self.output_ports:
            if output_port.queue:
                next_event = output_port.queue[0]
                if current_time >= output_port.handling_times[0]:
                    next_events.append(next_event)
                else:
                    next_events.append(None)
            else:
                next_events.append(None)
        return next_events

    def process_input_event(self, event):
        input_port = self.input_ports[event.input_port_index]
        output_port = self.output_ports[event.output_port_index]
        output_port.enqueue_event(event)
        input_port.dequeue_event()
        
    def process_output_events(self, events):
        for i in range(self.num_output_queues):
            if events[i] == None:
                pass
            else:
                output_port = self.output_ports[events[i].output_port_index]
                output_port.dequeue_event()

    def finalize_simulation(self):
        num_handled_events_per_queue = [0] * (self.num_output_queues)
        num_thrown_events_per_queue = [0] * (self.num_output_queues)
        total_handled_events = 0
        total_thrown_events = 0
        simulation_end_time = max([self.output_ports[i].last_handled_time for i in range(self.num_output_queues)])
        total_service_time = sum([self.output_ports[i].total_service_time for i in range(self.num_output_queues)])
        total_wait_time = sum([self.output_ports[i].total_wait_time for i in range(self.num_output_queues)])
        for i in range(self.num_output_queues):
            num_handled_events_per_queue[i] = self.output_ports[i].handled_events
            total_handled_events += self.output_ports[i].handled_events
        for i in range(self.num_output_queues):
            num_thrown_events_per_queue[i] = self.output_ports[i].thrown_events
            total_thrown_events += self.output_ports[i].thrown_events
        avg_service_time = total_service_time / total_handled_events
        avg_wait_time = total_wait_time / total_handled_events
        
        # formatted_string = (
        #         f"Total Handled Events: {total_handled_events}, "
        #         f"Number of Handled Events per Queue: {num_handled_events_per_queue}, "
        #         f"Total Thrown Events: {total_thrown_events}, "
        #         f"Number of Thrown Events per Queue: {num_thrown_events_per_queue}, "
        #         f"Simulation End Time: {simulation_end_time}, "
        #         f"Average Wait Time: {avg_wait_time}, "
        #         f"Average Service Time: {avg_service_time}"
        #     )
        # print(formatted_string)
        handled_events_per_queue_str = ' '.join(map(str, num_handled_events_per_queue))
        thrown_events_per_queue_str = ' '.join(map(str, num_thrown_events_per_queue))
        formatted_string = (
                f"{total_handled_events} "
                f"{handled_events_per_queue_str} "
                f"{total_thrown_events} "
                f"{thrown_events_per_queue_str} "
                f"{simulation_end_time} "
                f"{avg_wait_time} "
                f"{avg_service_time}"
            )
        print(formatted_string)
        return avg_wait_time

if __name__ == "__main__":
    args = parseArguments()
    simulator = Simulator(args.T, args.N, args.M, args.ouput_queue_sizes, args.arrival_rates, args.handling_rates, args.probs)
    simulator.run_simulation()