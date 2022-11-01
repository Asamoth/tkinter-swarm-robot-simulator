# **Simulator of a swarm of robot and their behaviors through tkinter**

This was a GUI python project using the tkinter module to represent a swarm robot simulator to compare the efficiency of two swarm behaviors.
The first one is centralized (called military behavior) and the second one is a decentralized behavior (called bird flock). 
The efficency here is defined as the time taken for the swarm to reach the goal (represented by a red dot with semi-random coordinates), the less time taken the higher the efficiency.  
Data (coordinates of the goal, the number of robots, the size of the arena, the time taken) is collected and put into an SQL database and that data is displayed through matplotlib.pyplot.
The ultimate goal of this project was to see which behavior was better at finding a missing person (the goal) inside a 2D arena.
Warning though, my simulator is terribly inefficient, lags and is prone to bugs but some of its ideas might help someone.

To launch the simulation, you only need: 
1. main2.py the main in which all classes are called
2. robot.py the robot class which contains all of the swarm behavior and the kinematics model for a differential-drive robot.
3. simu.py the simulation class which contains all of the GUI for drawing the robots inside of a window.
4. angle.py an angle class that I did not make, used for rotating items in the aforementioned classes.
5. TailleX.txt and TailleY.txt, two text files that contain lists of X and Y sizes that will take the windows, chosen at random.
6. robot_model.png a simple png image that represents the robot, used in simu.py.

The other files:
To make use of the other .py files named "donnee", you need to download a mysql connector module.
These only serve to display matplotlib graphs of the data gathered in the mySQL database.

 # **Swarm robotics: efficiency of swarm behaviors applied to a concrete situation**

Practical applications in swarm robotics are numerous. In accordance with Moore's law, the potential of this field will not stop growing. Having got a taste for programming freedom while working on a project in Python, it seemed interesting to me to discover this field.

Some research in swarm robotics is pushing to develop a swarm intelligence capable of operating in search and rescue missions, as well as in disaster response where health and prevention of over-accident or aggravation of situations are at the heart of the field.

# **Thematic positioning** 

*COMPUTER SCIENCE (Practical Computer Science), INDUSTRIAL SCIENCE (Mechanical Engineering).* 

# **Keywords** 

*Simulation*

*Autonomous robot*

*Detection and obstacle avoidance* 

*Sensors* 

*Biomimetism* 

# **Annotated bibliography**

The  concept  of  swarm  intelligence  was  proposed  by  Gerardo  Beni  and  Jim  Wang  in  a  very influential thesis that  later gave rise to a field of robotics. The latter describes a group of robots, usually in large numbers, forming a swarm. These must communicate via local interactions, i.e. there is a limitation to the proximity of the information that can be transmitted. These interactions can take the form of either direct or indirect transmission as stigmergy, such as termites marking a path to follow via pheromones. Finally, the members of the swarm  show  a  certain  material homogeneity  and  are  as  much  structurally  as  behaviorally identical (or almost), and these react in response to the evolution of the environment. [2]

The characteristic related to the necessary large number of robots in a swarm is however questionable because the attribute sought in terms of number is more related to  the  scalability  of  the  swarm's behavior than to the quantity of individuals in itself. This character seems a priori innate to the swarm principle because the robots only interact locally, however it is a question of making a compromise between centralized and distributed architecture.  A centralized behavior applied to a precise configuration  will be effective because it is specifically  designed for the  type of  environment  in  which  the  swarm  will  work,  but  it  will  be  problematic  once  the  swarm  is decentralized; distributed behavior, on the other hand, will leave more freedom to the members of the swarm with less directed instructions, but has the advantage  of  being versatile in different types of terrain because their behavior will not be disturbed by the change in environment. [4]

Swarm robotics is intrinsically linked to the behavior of social insects, schools of fish, flocks of birds and flocks of sheep. Biomimicry is thus at the heart of the field. Different approaches to the behavior  or  type  of  swarm  sought  will  benefit  from  biomimicry  targeted  at  different  animal behaviors.  In  aeronautics,  understanding  and  modeling  the  behavior  of  flocks  of  birds  is necessary  for the  automation  of certain  tasks for drones.  In search  and  rescue, where time is limited, the efficiency of an ant algorithm, for example, can be interesting. [1] [4]

In the context of disaster response and relief that we are interested in, the "s-bot" or "swarm-robot" concept is particularly relevant. These being self-reconfigurable modular robots will be able to interconnect each other autonomously in different configurations, notably in order to form chains of robots. They are capable of pulling loads such as incapacitated human beings. The problem arises when it comes to autonomy, an s-bot is constrained to about two hours of operation [2].

![sbots](https://user-images.githubusercontent.com/117095706/199107970-c81370c4-d3f9-4c9d-aaad-ad3b8602136f.png)

It is then  all  the more important to minimize the maximum time  needed to find a target in a given environment.

# **Selected issues**

The  aim  is  to  study  the  effectiveness  of  different  biomimetic  swarm  behaviors  conforming  to  a distributed model compared to a centralized architecture as well as their scalability, in the  context of terrestrial search and rescue.

# **Objectives** 

Building a robot simulator in a 2-dimensional environment via python. -Writing centralized swarm behavior(s) using biomimicry.

-Writing  of  distributed  swarm  behavior(s)  in  accordance  with  the  previously  defined  simulation environment.

-Assembly of multifunctional robots controlled by Arduino. -Translation of swarm behaviors  into Arduino for experimentation.

-Study of the efficiency of swarming behaviors as a function of the number of robots in an arena of defined size in accordance with the experiment.

-Comparison of simulation and experimental results and interpretation.

# **Proof of kinematics model used in the modelisation**
![model](https://user-images.githubusercontent.com/117095706/199108893-60822a26-c214-47eb-8b75-73409417e79e.png)
![implementation](https://user-images.githubusercontent.com/117095706/199109061-b9b2854d-7211-449c-9cb1-1ec5288ae01f.png)

By integrating the matricial system with respect to time, we get a function that will update the (x,y) position in the tkinter canvas as well as the angular position of the robot. Its parameter is a time interval named dt which will represent the time measured between two iterations of the code.
Note that the origin of the axis in tkinter is in the top left whereas in my mathematical model, the origin is in the bottom left and the positive values of y are in opposite directions.

# **Results**
![fig1](https://user-images.githubusercontent.com/117095706/199322021-a4755a9f-ac99-4be5-a26d-47934d768a12.png)

# **Bibliographic references**

[1] Sangita Roy; Samir Biswas; Sheli Sinha Chaudhuri: Nature-Inspired Swarm Intelligence and Its Applications: [*For Biomimicry and Applications*](http://www.researchgate.net/publication/)


[2] Hui Keng Lau: Error Detection in Swarm Robotics: [*A Focus on Adaptivity to Dynamic Environments*](https://www.cs.york.ac.uk/rts/documents/thesis/lau12.pdf)


[3] Francesco Mondada : SWARM-BOT: [*from concept to implementation*](http://www.researchgate.net/publication/4045834_SWARM-BOT\_from\_concept\_to\_implementation)


[4] Ying Tan : Swarm Robotics: Collective Behavior Inspired by Nature : [*For biomimicry, applications, notions of decentralization and scalability of a swarm*](http://www.cil.pku.edu.cn/docs/20190509161711220102.pdf)


