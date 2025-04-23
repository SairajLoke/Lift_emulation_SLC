import threading
import time
import signal
import sys

from sai_slc_driver import run_slc_driver
from merged_gui import run_merged_gui
from lift_utils import TABLE_ELEMENTS_NEXT_STATE_MAPPING # had to do this to make unpickkle work
from lift_utils import LIFT_SYSTEM

stop_event = threading.Event() 
request_list = []
LIFT = LIFT_SYSTEM() 


def signal_handler(sig, frame):
    print("\nKeyboardInterrupt (Ctrl+C) received. Cleaning up...")
    stop_event.set()  # signal thread to stop
    time.sleep(0.5)  # give threads time to clean up
    sys.exit(0)




if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    request_thread = threading.Thread(target=run_merged_gui, args=(request_list,LIFT,stop_event), daemon=True) # to kill thread using ctrl c
    time.sleep(1)  #to ensure GUI is ready before SLC starts
    request_thread.start()

    # Wait for threads to complete ..I'll rather pass stop_event to threads, in real life I'll rathre do emergency stop
    # gui_thread.join()
    # slc_thread.join()

    try:
        run_slc_driver(request_list, LIFT)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting gracefully.\n")
        
        
        



# if __name__ == "__main__":
#     signal.signal(signal.SIGINT, signal_handler)

#     # Create threads
#     # gui_thread = threading.Thread(target=run_gui, args=(request_list,), daemon=True)
#     slc_thread = threading.Thread(target=run_slc_driver, args=(request_list,LIFT), daemon=True) # to kill thread using ctrl c
#     # After initializing LIFT
#     # lift_state_thread = threading.Thread(target=run_lift_visualizer, args=(LIFT,), daemon=True)

#     time.sleep(1)  # Optional delay to ensure GUI is ready before SLC starts
#     slc_thread.start()

#     # Start threads
#     # gui_thread.start()
#     # lift_state_thread.start()
#     # time.sleep(1)  # Optional delay to ensure GUI is ready before SLC starts
#     # Start merged GUI in main thread
#     # Wait for threads to complete ..rather pass stop_event to threads, in real life I'll rathre do emergency stop
#     # gui_thread.join()
#     # slc_thread.join()

#     try:

#         run_merged_gui(request_list, LIFT)
#         # Keep the main thread alive so Ctrl+C works
#         # while True:
#         #     slc_thread.is_alive()
#         #     print("Main thread is alive. Press Ctrl+C to exit.")
#         #     time.sleep(0.5)
#         # while gui_thread.is_alive() or slc_thread.is_alive() or lift_state_thread.is_alive():
#         #     time.sleep(0.5)
#     except KeyboardInterrupt:
#         print("\nKeyboardInterrupt received. Exiting gracefully.")
        
        
        

