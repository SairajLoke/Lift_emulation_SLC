import RPi.GPIO as GPIO
from time import sleep

# Set up GPIO pin numbering to physical layout
GPIO.setmode(GPIO.BOARD)

# Set up pin 11 for PWM
GPIO.setup(11, GPIO.OUT)

# Initialize PWM with 50Hz frequency
p = GPIO.PWM(11, 50)

try:
    # Start PWM with 0% duty cycle (servo off initially)
    p.start(0)
    
    while True:
        # Move the servo back and forth
        p.ChangeDutyCycle(3)  # Move servo to one position
        sleep(2)
        p.ChangeDutyCycle(6)
        sleep(2)
        p.ChangeDutyCycle(9)
        sleep(2)
        p.ChangeDutyCycle(12)  # Move servo to the other position
        sleep(2)

except KeyboardInterrupt:
    # Handle interrupt gracefully (e.g., Ctrl+C)
    print("Program interrupted, cleaning up...")

finally:
    # Ensure PWM is stopped and GPIO is cleaned up
    print(f"PWM object: {p}")
    if p is not None:
        p.stop()        # Stop PWM signal
    
    GPIO.cleanup()  # Clean up GPIO settings to reset pins
