
import RPi.GPIO as GPIO
from time import sleep

# -------------------------------hardware control functions interfacing with servo motor-------------------------------------------
class MotorController:
    def __init__(self):
        # Initialize any hardware communication (e.g., GPIO, I2C, etc.)
        self.lift_position = 0  
        self.door_position = 0
        
        # Set up GPIO pin numbering to physical layout
        GPIO.setmode(GPIO.BOARD)
        LIFT_MOTOR_PIN = 11  
        DOOR_MOTOR_PIN = 12 
        GPIO.setup(LIFT_MOTOR_PIN, GPIO.OUT)
        GPIO.setup(DOOR_MOTOR_PIN, GPIO.OUT)

        # Initialize PWM with 50Hz frequency
        self.lift_pwm = GPIO.PWM(LIFT_MOTOR_PIN, 50) #p
        # Initialize PWM for door motor
        self.door_pwm = GPIO.PWM(DOOR_MOTOR_PIN, 50)
        
        self.lift_pwm.start(0)
        self.door_pwm.start(0)
        
        self.FLOOR_DELTA = 2 #  
        self.DOOR_DELTA = 6 #

    def set_servo_angle(self, angle):
        # Logic to control the servo (this is hardware-dependent)
        print(f"Setting servo to {angle} degrees.")
        self.servo_position = angle
        # Here you could communicate with the actual hardware to move the servo.

    def open_door(self):
        # For example, opening the door could mean setting the servo to 90 degrees
        self.set_servo_angle(90)
        print("Door opened.")

    def close_door(self):
        # Closing the door could mean setting the servo to 0 degrees
        self.set_servo_angle(0)
        print("Door closed.")
        
    def move_up(self):
        # Logic to move the lift up
        print("Lift moving up.")
        # Here you would add the actual code to control the lift motor.
        
    def move_down(self):
        # Logic to move the lift down
        print("Lift moving down.")
        # Here you would add the actual code to control the lift motor.
        
    def stop_motors(self):
        # Logic to stop the lift motors
        print("Lift motors stopped.")
        # Here you would add the actual code to stop the lift motor.
        
    def test_run(self):
        try:
            while True:
                # Move the servo back and forth
                self.lift_pwm.ChangeDutyCycle(self.lift_position + self.FLOOR_DELTA)  # Move servo to one position
                sleep(2)
                self.lift_pwm.ChangeDutyCycle(self.lift_position + 2*self.FLOOR_DELTA) 
                sleep(2)
                self.lift_pwm.ChangeDutyCycle(self.lift_position + 3*self.FLOOR_DELTA) 
                sleep(2)
                self.lift_pwm.ChangeDutyCycle(self.lift_position + 4*self.FLOOR_DELTA)  # Move servo to the other position
                sleep(2)
                
                self.lift_pwm.ChangeDutyCycle(self.lift_position + 4*self.FLOOR_DELTA)  # Move servo to the other position
                sleep(2)
                self.lift_pwm.ChangeDutyCycle(self.lift_position + 3*self.FLOOR_DELTA) 
                sleep(2)
                self.lift_pwm.ChangeDutyCycle(self.lift_position + 2*self.FLOOR_DELTA) 
                sleep(2)
                self.lift_pwm.ChangeDutyCycle(self.lift_position + self.FLOOR_DELTA)  # Move servo to one position
                sleep(2)

        except KeyboardInterrupt:
            # Handle interrupt gracefully (e.g., Ctrl+C)
            print("Program interrupted, cleaning up...")

        finally:
            # Ensure PWM is stopped and GPIO is cleaned up
            print(f"PWM objects: {self.lift_pwm}, {self.door_pwm}")
            
            if self.door_pwm is not None and self.lift_pwm is not None:
                 # Stop PWM signal
                self.door_pwm.stop()
                self.lift_pwm.stop()
            
            GPIO.cleanup()  # Clean up GPIO settings to reset pins


if __name__ == "__main__":
    
    motor_controller = MotorController()
    try:
        # Test the motor controller
        motor_controller.test_run()
    except Exception as e:
        print(f"Error in motor controller: {e}")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings to reset pins