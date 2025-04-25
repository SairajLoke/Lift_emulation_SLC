
## Demo


### Case 1 other demo (as seen in the hardware video)

https://github.com/user-attachments/assets/b7d06627-d9de-4dc3-a6ea-a6909f306c35

Hardware Demo for above gui interface video 

https://github.com/user-attachments/assets/a99d86da-1702-4508-bb41-f6a720a9e7ae

## Try it NOW !
## Installation and Quick Testing using GUI 

### STEP 1 :  Installations

    pip -r requirements.txt 
    sudo apt-get install python3-tk 

    sudo apt install python3-rpi-lgpio  #if you are using rpi..not needed for laptop based gui-only testing

### STEP 2 & 3 : Get the Moore Machine Diagram ( I have created one which can be used for testing the lift system)  \newline AND Get Transition States for the machine ( Required for getting the BDD Next State Mapping which is used in the SLC Code )

     python sai_graph_generator.py 

 
### STEP 4 : Get the BDD Table automatically from the transition states

     python sai_transitions_2_table.py 

### STEP 5 : DONE!, run the main file to access my lift !
     python sai_main_lift_system.py 


## Setup 
Inputs 
GUI 

Actuators 
2 Servo motors 


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


<!-- sudo apt-get install python3-tk graphviz -->
<!-- pip install RPi.GPIO -->
<!-- sudo apt remove python3-rpi.gpio
sudo apt install python3-rpi-lgpio -->

## The System Details
Time + Interrupt Driven system

![image](https://github.com/user-attachments/assets/fc058f6a-3e4f-4a59-934e-0e79bf45731c)

![CPS2025_LIFT_EMULATION-Lift Flow Diagram drawio(5)](https://github.com/user-attachments/assets/deb4099a-b620-48ed-afd7-0745b9fe27b7)


### Moore Machine 

![image](https://github.com/user-attachments/assets/5f17f93a-9b0f-4700-a9d3-62e2eee73d15)


### Lift Controller State Transition Graph / Equations
![image](https://github.com/user-attachments/assets/a2a4376b-4b05-4893-827a-5166f530df10)


### Interface
![image](https://github.com/user-attachments/assets/1b92b9d9-da82-4b7b-951e-916066fbbfd2)


### SLC Code  

input checked and preprocessed ( converting the input data to Boolean values to be used in SLC machine driver)

![image](https://github.com/user-attachments/assets/218f7fa3-3cab-4172-8d5f-561d52ac7c5a)




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

improvement would be to move it outside computing control signals (folowing the 4 steps here ) 
![image](https://github.com/user-attachments/assets/d92e2b9d-85a4-4021-b093-1dc62423587d)




so after 1st idle phase it goes into a waiting phase...with no more homing calls
Call at 4, and 
    call at 2 
        before it passes 2
        after it passes 2 



# Future Directions

1. use better lib than rpi.gpio, coz its not ideal for realtime ops ( as mentioned on their official Website)

2. Thread safe queues/list to be used.
3. Provide parallel process support (using multiprocessing.Dequeue()/ Queue()) ...wont give signi benefit i believe as the viz cide is light? and has 3 fns running...also no visible performance loss in current threadeding env
