# Lift_emulation_SLC

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
