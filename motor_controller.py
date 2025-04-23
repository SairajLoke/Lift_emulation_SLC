

# -------------------------------hardware control functions interfacing with servo motor-------------------------------------------
class MotorController:
    def __init__(self):
        # Initialize any hardware communication (e.g., GPIO, I2C, etc.)
        self.servo_position = 0  # Example to keep track of the servo position

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
        
