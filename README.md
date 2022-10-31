# tkinter-swarm-robot-simulator

This was a GUI python project using the tkinter module to represent a swarm robot simulator to compare the efficiency of two swarm behaviors.
The first one is centralized (called military behavior) and the second one is a decentralized behavior (called bird flock). 
The efficency here is defined as the time taken for the swarm to reach the goal (represented by a red dot with semi-random coordinates), the less time taken the higher the efficiency.  
Data (coordinates of the goal, the number of robots, the size of the arena, the time taken) is collected and put into an SQL database and that data is displayed through matplotlib.pyplot.
The ultimate goal of this project was to see which behavior was better at finding a missing person (the goal) inside a 2D arena.
Warning though, my simulator is terribly inefficient, lags and is prone to bugs but some of its ideas might help someone.

[MCOT_55839_17599 en-US (1).pdf](https://github.com/Asamoth/tkinter-swarm-robot-simulator/files/9904202/MCOT_55839_17599.en-US.1.pdf)


