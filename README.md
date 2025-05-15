# epidemic-simulation
Epidemic Simulation
This project simulates the spread of an epidemic in a network using probabilistic rules. It models the dynamics of disease transmission across a population represented as a graph.

Features
Simulates an epidemic over a graph structure.

Each node represents an individual in one of the following states:

Susceptible (S)

Infected (I)

Recovered (R)

The simulation runs for a defined number of steps, and at each step:

Infected individuals may recover with a specified probability.

Infected individuals may infect their susceptible neighbors with a transmission probability.

Requirements
Python 3.x

NetworkX

Matplotlib

NumPy

Install dependencies with:
pip install networkx matplotlib numpy

Usage
To run the simulation:
python comsim.py
Optional command-line arguments:
python comsim.py [network_size] [connection_prob] [initial_infected] [transmission_prob] [recovery_prob] [num_steps]
For example:
python comsim.py 100 0.1 5 0.2 0.1 50

This means:

100 nodes

10% chance of edge between each pair of nodes

5 nodes initially infected

20% chance of transmission

10% chance of recovery

50 simulation steps

Output
A line graph showing the number of susceptible, infected, and recovered individuals over time.

File Structure
comsim.py — Main simulation code

License
MIT License
