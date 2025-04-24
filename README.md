# Lift_emulation_SLC

## TODO 


## Keypoints

1. Automated Moore Machine Digram, Transition Fns Extraction, BDD Table from Transition functions
2. I also provide an option to have state-transition table..that doesnt allow repeated entries of same stae but in different BDDs 
3. RPI + Servo Motor based H/W implementation 
4. GUI for testing , emulation ( code can be demonstrated and tested wihout H/W)


## Features of the LIFT System
-   Queue management for floor requests
-   Threading Support for Lift Call/Floor Request
-   Up/Down logic with lifts floors ( 2U-3 1D-0 ) (Function Call-Destination FLoor, ..., )

-   Door operations
-   Movement control between floors
-   Floor request handling

-   IDLE time checking
-   Weight limit checks
-   Homing Support 


## Handbook Lift Limitations
- Lift can only take new Lift Calls once it is done serving the current
- (so all Lift calls done while lift in motion are ignored)
- no weight checks, 
- no up/down direction logic
- no Homing
- no IDLE-state detection
- no multple floor request serve


## Installations
pip -r requirements.txt 

OR 

sudo apt update

sudo apt install python3-rpi-lgpio python3-pynput python3-tk graphviz

<!-- sudo apt-get install python3-tk graphviz -->
<!-- pip install RPi.GPIO -->
<!-- sudo apt remove python3-rpi.gpio
sudo apt install python3-rpi-lgpio -->




## RUN
python3 sai_graph_generator.py 

python3 sai_transitions_2_table.py 

python3 sai_main_lift_system.py

Debugging each terms in the individual steps (transition graphs, eqns, table) was hard...so i automated the creation given just a flow_chart 



## SOME NOTES: 
- After getting in lift one must press a floor in correct direction ...else we wait till then...


=================== Current Not so ideal behaviour ===============

if lift calls at floor 1,2,3,4 in that order...(say all want to go at floor 0)
    , even if person on 1st floor presses 0 inside lift, the lift will serve 2-4 first
    this is coz the serves are completely FCFS basis 

also observed if i press 1-down , 2-up, 3-down, lift will take all calls



================== Expected Behaviours ===========================


-----------------DOOR OPERATIONS------------------

Door closes after timeout when no further requests exist.
Door opens at requested floor.
Door stays open when weight exceeds threshold.??

------------------Lift Movement-------------------

wrong direction key?....ignored till the first destination reached
anytine floors are served from inside 



---------------------Homing------------------------

System enters WAITING state on startup.
Lift transitions to IDLE when idle time exceeds threshold.
Homing behavior when no requests exist (idle returns to HOME_FLOOR).
Lift remains WAITING when no requests and doors are open., idle_bool = true...


------------ Request Handling-----------------

- Valid request (correct direction floor during floor request await) is added to queue.
- Queue is updated and next request is popped.
- Queue emptied after serving all requests
- Redundant call is removed if current floor already in queue.


------------ Concurrent Lift Calls ----------------

supports multiple concurrent lift calls. 
    - if they are on the way to the first call..the lift stops if the direction matches
    - if in different direction call the lift will put in queue but not stop while serving the first call,...will come back after serve is done


------- Moving lift floor calls (from inside the lift)----------

Lift can be called from inside the lift while the lift is in any state(except before the very first lift summoning)
    - if the call is in the same direction as the lift, it will stop at the requested floor
    - if the call is in the opposite direction, it will be ignored ...as not valid direction, if no valid call for the entire dureation...close door and go waiting


NOTE:

actually the floor req shouldn't ideally work unless the firsttime the door opens
weight can actually be added just after wait time and just before door close...but not practically large time 






so after 1st idle phase it goes into a waiting phase...with no more homing calls
Call at 4, and 
    call at 2 
        before it passes 2
        after it passes 2 



# Future Directions

1. Doing more stress testing on the latency aspect
2. Thread safe queues/list to be used.
3. Provide parallel process support (using multiprocessing.Dequeue()/ Queue()) ...wont give signi benefit i believe as the viz cide is light? and has 3 fns running...also no visible performance loss in current threadeding env