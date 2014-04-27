#!/usr/bin/python

"CS 244 Assingment 3: Increasing initial congestion window"

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.util import pmonitor
from signal import SIGINT

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser
import random

import sys
import os
from util.monitor import monitor_qlen
from util.helper import stdev

# Parse arguments
parser = ArgumentParser(description="Cwnd adjusting")

# Expt parameters
args = parser.parse_args()
parser.add_argument('-n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in star.  Must be >= 3",
                    required=True)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=1000)

parser.add_argument('--cong',
                    dest="cong",
                    help="Congestion control algorithm to use",
                    default="bic")


# Topology to be instantiated in Mininet
class StarTopo(Topo):
    "Star topology for Buffer Sizing experiment"

    def __init__(self, n=3, cpu=None, maxq=None):
        # Add default members to class.
        super(StarTopo, self ).__init__()
        self.n = n
        self.cpu = cpu
        self.create_topology()

    def create_topology(self):

        # add switch
        switch = self.addSwitch('s0')

        # add hosts and links
        for h in range(self.n):
            host = self.addHost('h%s' % (h + 1))
            bw_inst = getBW()
            delay_inst = '%fms'%getRTT()/4
                        
            linkopts = dict(bw=bw_inst, delay=delay_inst,
                    max_queue_size=self.maxq, htb=True)

            self.addLink(host, switch, **linkopts)

def getBW():
    sample = random.uniform(0, 1)
    if sample < 0.25:
        return 200/2.0  # kbps
    elif sample < 0.5:
        return (200+500)/2.0
    elif sample < 0.75:
        return (500+1259)/2.0
    else:
        return (1259+3162)/2.0

def getRTT():
    sample = random.uniform(0, 1)
    if sample < 0.25:
        return 31/2.0
    elif sample < 0.5:
        return (31+70)/2.0
    elif sample < 0.75:
        return (70+120)/2.0
    else:
        return (120+1000)/2.0


def main():
    "Create network and run Buffer Sizing experiment"

    start = time()
    # Reset to known state
    topo = StarTopo(n=args.n, maxq=args.maxq)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    net.CLI()
    # Set initial congestion window to three
    # Experiment

    # Set initial congestion window to ten
    # Experiment

if __name__ == '__main__':
    try:
        main()
    except:
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")
