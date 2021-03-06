"""
Use of SimComponents to simulate the network of queues from Homework #6 problem 1, Fall 2014.
See corresponding solution set for mean delay calculation based on Burkes theorem.

Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
import random
import functools
import simpy
import sys
import time
import matplotlib.pyplot as plt
import numpy as np

from SimComponents import PacketGenerator, PacketSink, PortMonitor, SwitchPort, RandomBrancher, RoundRobin, \
    WeightedRoundRobin, LeastConnection, RandomBalancer


def PrintResults(switchports,endpoints):

    iplr_list = []
    avg_occupancy = []
    pkt_sum = 0
    mean_load = 0

    for switchport in switchports:
        iplr_list.append((switchport.packets_drop/switchport.packets_rec)*100)

    for endpoint in endpoints:

        avg_occupancy.append(float(sum(endpoint.sizes) / sum(endpoint.arrivals)))

        pkt_sum+=endpoint.packets_rec
        mean_IPLR = sum(iplr_list)/output_count

        print()
        print("average system occupancy on endpoint {} : {}".format(endpoints.index(endpoint), avg_occupancy[endpoints.index(endpoint)]))
        print("packets recieved by endpoint {} = {}".format(endpoints.index(endpoint), endpoint.packets_rec))
        print("IPLR on endpoint {} = {} %".format(endpoints.index(endpoint), iplr_list[endpoints.index(endpoint)]))
        print()

    if algorithm is 1:
        mean_load = sum(avg_occupancy)/len(avg_occupancy)
        print ("Mean load for all servers: {}".format(mean_load))

    print("Estimated load per server: {}".format(pkt_sum*pkt_size/queue_rate/8/output_count))

    x = [i for i, _ in enumerate(endpoints)]

    plt.bar(x,avg_occupancy,align='center', alpha=0.5,color = 'green',label = 'Total Load')
    plt.bar(x,iplr_list,align='center',alpha=0.5, color = 'red',label='IPLR')
    plt.xticks(x,x)
    plt.legend(loc=4)
    plt.ylabel('Load / %')
    plt.title('Total load distribution and pachet loss rate')
    plt.show()



if __name__ == '__main__':
    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters.
    # each call to these will produce a new random value.

    #parse config file

    config_file = open("config")
    config_args = []

    for line in config_file:
        li = line.strip()
        if not li.startswith("#"):
            config_args.append(li.rstrip())

    #assign arguments to variables

    pkt_size = int(config_args[0])  # in bytes
    pkt_limit = int(config_args[1])
    lmbda = float(config_args[2])
    output_count = int(config_args[3])
    queue_rate = int(config_args[4])
    qlimit = int(config_args[5])
    algorithm = int(config_args[6])



    endpoints_list = []
    switchports_list = []
    endpoints_weigths = []  # weights added randomly from 1-10
    monitor_list = []


    # Create the SimPy environment. This is the thing that runs the simulation.
    env = simpy.Environment()

    adist1 = functools.partial(random.expovariate, lmbda)
    sdist = functools.partial(random.uniform, pkt_size, pkt_size)  # Uniform partial for constant packet size

    # Create the packet generators and sinks (simulating endpoint servers and network input)

    pg1 = PacketGenerator(env, "Stream", adist1, sdist)


    for i in range(0, output_count):

        endpoints_list.append(PacketSink(env, weight=random.randint(1, 10), pkt_size=pkt_size, debug=False, rec_arrivals=True, rec_sizes=True))             #creating endpoints (servers) with processing speed and weight
        switchports_list.append(SwitchPort(env,queue_rate,qlimit=qlimit))
        monitor_list.append(PortMonitor(env,switchports_list[i],adist1))

        endpoints_weigths.append(endpoints_list[i].weight)


    # load balancing algirithms

    lb1 = WeightedRoundRobin(env, output_count, endpoints_weigths, pkt_size)
    lb2 = RoundRobin(env, output_count)
    lb3 = LeastConnection(env, output_count, monitor_list)
    lb4 = RandomBalancer(env, output_count)

    #choose algorithm

    if algorithm == 1:
        balancer = lb1
    elif algorithm == 2:
        balancer = lb2
    elif algorithm == 3:
        balancer = lb3
    elif algorithm == 4:
        balancer = lb4
    else:
        sys.exit("Wrong algorithm!")


    # Wire packet generators and sinks together
    pg1.out = balancer

    for i in range(0, output_count):
        balancer.outs[i] = switchports_list[i]
        switchports_list[i].out = endpoints_list[i]

    # Run it
    print("Starting simulation...")

    start = time.time()
    env.run(until=pkt_limit)
    end = time.time()
    sim_time = end - start

    print("Simulation finished! Simulation time {} seconds.".format(sim_time))
    print ()

    #print results
    PrintResults(switchports_list,endpoints_list)


