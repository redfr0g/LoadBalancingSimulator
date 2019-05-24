"""
Use of SimComponents to simulate the network of queues from Homework #6 problem 1, Fall 2014.
See corresponding solution set for mean delay calculation based on Burkes theorem.

Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
import random
import functools

import simpy

from SimComponents import PacketGenerator, PacketSink, PortMonitor, SwitchPort, RandomBrancher, RoundRobin, \
    WeightedRoundRobin, LeastConnection, RandomBalancer


def PrintResults(endpoints):
    for endpoint in endpoints:
        print("average system occupancy on endpoint {} : {}".format(endpoints.index(endpoint), float(
            sum(endpoint.sizes) / sum(endpoint.arrivals))))
        print("packets recieved by endpoint {} = {}".format(endpoints.index(endpoint), endpoint.packets_rec))
        # print(endpoint.sizes)
        # print("packets lost {}".format(pg1.packets_sent - ps1.packets_rec - ps2.packets_rec - ps3.packets_rec - ps4.packets_rec))


if __name__ == '__main__':
    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters.
    # each call to these will produce a new random value.

    mean_pkt_size = 1000.0  # in bytes
    adist1 = functools.partial(random.expovariate, 2.0)
    sdist = functools.partial(random.uniform, 1000, 1000)  # Uniform partial for constant packet size
    samp_dist = functools.partial(random.expovariate, 0.50)

    # Create the SimPy environment. This is the thing that runs the simulation.
    env = simpy.Environment()

    # Create the packet generators and sinks (simulating endpoint servers and network input)

    pg1 = PacketGenerator(env, "Stream", adist1, sdist)
    endpoints_max = 10
    endpoints_list = []
    endpoints_weigths = []  # weights added randomly from 1-10

    for i in range(0, endpoints_max):
        endpoints_list.append(PacketSink(env, random.randint(1, 10), debug=False, rec_arrivals=True, rec_sizes=True))
                                                                                            # TODO Add to packetsink service rate and service list and packets loss  (Aga)
                                                                                            # TODO Calculate business from servicing time and total time
        endpoints_weigths.append(endpoints_list[i].weight)

    # load balancing algirithms
    lb1 = WeightedRoundRobin(env, endpoints_max, endpoints_weigths, mean_pkt_size)
    lb2 = RoundRobin(env, endpoints_max)
    lb3 = LeastConnection(env, endpoints_max, endpoints_list)
    lb4 = RandomBalancer(env, endpoints_max)
                                                                                            # TODO Add least load algorithm which checks and updates service lists in all servers when gets its packets

    balancer = lb3

    # Wire packet generators and sinks together
    pg1.out = balancer

    for i in range(0, endpoints_max):
        balancer.outs[i] = endpoints_list[i]

    # Run it
    env.run(until=10000)
    PrintResults(endpoints_list)
