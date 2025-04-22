import threading
import time

from sai_slc_driver import run_slc_driver
# from sai_gui import run_gui
# from sai_viz_lift_state import run_lift_visualizer
from merged_gui import run_merged_gui

from lift_utils import TABLE_ELEMENTS_NEXT_STATE_MAPPING # had to do this to make unpickkle work
from lift_utils import LIFT_SYSTEM

# from collections import deque
# Shared queue used in the elevator logic
request_list = []
LIFT = LIFT_SYSTEM() 

if __name__ == "__main__":
    # Create threads
    # gui_thread = threading.Thread(target=run_gui, args=(request_list,), daemon=True)
    slc_thread = threading.Thread(target=run_slc_driver, args=(request_list,LIFT), daemon=True) # to kill thread using ctrl c
# After initializing LIFT
    # lift_state_thread = threading.Thread(target=run_lift_visualizer, args=(LIFT,), daemon=True)

    # Start threads
    # gui_thread.start()
    time.sleep(1)  # Optional delay to ensure GUI is ready before SLC starts
    # lift_state_thread.start()
    time.sleep(1)  # Optional delay to ensure GUI is ready before SLC starts
    slc_thread.start()
    
    
    # Start merged GUI in main thread
    run_merged_gui(request_list, LIFT)

    # Wait for threads to complete (optional)
    # gui_thread.join()
    # slc_thread.join()

    try:
        # Keep the main thread alive so Ctrl+C works
        while True:
            slc_thread.is_alive()
            print("Main thread is alive. Press Ctrl+C to exit.")
            time.sleep(0.5)
        # while gui_thread.is_alive() or slc_thread.is_alive() or lift_state_thread.is_alive():
        #     time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting gracefully.")
        
        
        

