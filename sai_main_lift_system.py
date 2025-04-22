import threading
import time

from sai_slc_driver import run_slc_driver
from sai_gui import run_gui

from lift_utils import TABLE_ELEMENTS_NEXT_STATE_MAPPING # had to do this to make unpickkle work

# from collections import deque
# Shared queue used in the elevator logic
request_list = []


if __name__ == "__main__":
    # Create threads
    gui_thread = threading.Thread(target=run_gui, args=(request_list,), daemon=True)
    slc_thread = threading.Thread(target=run_slc_driver, args=(request_list,), daemon=True) # to kill thread using ctrl c

    # Start threads
    gui_thread.start()
    time.sleep(2)  # Optional delay to ensure GUI is ready before SLC starts
    slc_thread.start()

    # Wait for threads to complete (optional)
    # gui_thread.join()
    # slc_thread.join()

    try:
        # Keep the main thread alive so Ctrl+C works
        while gui_thread.is_alive() or slc_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting gracefully.")