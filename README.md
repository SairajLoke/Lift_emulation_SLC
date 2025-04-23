# Lift_emulation_SLC

## installations
pip -r requirements.txt 
sudo apt-get install python3-tk graphviz
<!-- pip install RPi.GPIO -->
sudo apt remove python3-rpi.gpio
sudo apt install python3-rpi-lgpio


## RUN
python3 sai_graph_generator.py 
python3 sai_transitions_2_table.py 
python3 sai_main_lift_system.py

sudo apt update
sudo apt install python3-pynput
sudo apt install python3-rpi.gpio


Debugging each terms in the individual steps (transition graphs, eqns, table) was hard...so i automated the creation given just a flow_chart 

To check for Lift calls in another process?

LiftCall queue
FloorRequest queue

Limitations
Lift can only take new Lift Calls once it is done serving the current

It stays at the last called floor After every 30 mins 
After getting in lift one must press a floor in correct direction ...else we wait till then...


# Features
-   Queue management for floor requests
-   IDLE time checking
-   Door operations
-   Movement control between floors
-   Weight limit checks
-   Floor request handling

- I also provide an option to create space optimized state-transition table..that removes repeated entries of same stae but in different BDDs 


# Future Directions

1. Doing more stress testing on the latency aspect
2. Thread safe queues/list to be used.
3. Provide parallel process support (using multiprocessing.Dequeue()/ Queue()) ...wont give signi benefit i believe as the viz cide is light? and has 3 fns running...also no visible performance loss in current threadeding env