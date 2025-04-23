
from time import sleep

'''
lift_motor: 35kg, pin: 4(5V),6(GRND),8(control)
door_motor: 25kg, pin: 2(5V),5(GRND),7(control)

'''
USE_HARDWARE = False
if USE_HARDWARE:
    import RPi.GPIO as GPIO
    

# -------------------------------hardware control functions interfacing with servo motor-------------------------------------------
class MotorController:
    def __init__(self):
        # Initialize any hardware communication (e.g., GPIO, I2C, etc.)
        self.current_floor = 0  
        self.door_position = 0
        self.LIFT_MOTOR_PIN = 8  #35kg one 
        self.DOOR_MOTOR_PIN = 7
        
        if USE_HARDWARE:
        # Set up GPIO pin numbering to physical layout
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.LIFT_MOTOR_PIN, GPIO.OUT)
            GPIO.setup(self.DOOR_MOTOR_PIN, GPIO.OUT)

            # Initialize PWM with 50Hz frequency
            self.lift_pwm = GPIO.PWM(self.LIFT_MOTOR_PIN, 50) 
            # Initialize PWM for door motor
            self.door_pwm = GPIO.PWM(self.DOOR_MOTOR_PIN, 50)
        
            self.lift_pwm.start(0)
            self.door_pwm.start(0)
        
        self.angle_to_duty_cycle = {
            0: 2.5,
            30: 3.5,
            60: 4.5,
            #75: 5.0,
            90: 5.5,
            120: 6.5,
            #135: 7.5,
            150: 8.5,
            #165: 9.5,
            #180: 10.0  # doesnt give any deflection or both vals
        }
        
        self.floor_duty_map = {#duty = angle / 18 + 3
            0: 3,     #0, 
            1: 4.66,  #30,
            2: 6.66,  #60,
            3: 8 ,    #90,
            4: 9.66 , #120,
            5: 11.33 ,#150
        }
        
        self.door_duty_map = {
            0: 3,  #0 , close
            1: 8,  #90 , open
        }
        
    #def set_servo_angle(self, servo_pwm, duty):
     #   print(f"Setting servo to {angle} degrees.")
        
    def open_door(self):
        if USE_HARDWARE:
            self.door_pwm.ChangeDutyCycle(self.door_duty_map[1])
        self.door_position = 1
        print("Door opened.")

    def close_door(self):
        if USE_HARDWARE:
            self.door_pwm.ChangeDutyCycle(self.door_duty_map[0])
        self.door_position = 0
        print("Door Closed.")
        
    def move_up(self):
        print("Lift moving Up.")
        self.current_floor += 1
        if USE_HARDWARE:
            self.lift_pwm.ChangeDutyCycle(self.floor_duty_map[self.current_floor])
        
    def move_down(self):
        print("Lift moving Down.")
        self.current_floor -= 1
        if USE_HARDWARE:
            self.lift_pwm.ChangeDutyCycle(self.floor_duty_map[self.current_floor])
        
    def stop_motors(self):
        print("Lift motors stopped.")
        if USE_HARDWARE:
            self.lift_pwm.ChangeDutyCycle(self.floor_duty_map[self.current_floor])
        
        
    def test_run(self):
        if USE_HARDWARE:
            try:
                while True:
                    for angle, value in self.angle_to_duty_cycle.items():
                        duty = angle / 18 + 3
                        self.lift_pwm.ChangeDutyCycle(duty)
                        self.door_pwm.ChangeDutyCycle(duty)
                        print(angle, duty)
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
        else:
            # Simulate the motor control logic
            print("Simulating motor control...")
            self.open_door()
            sleep(1)
            self.close_door()
            sleep(1)
            self.move_up()
            sleep(1)
            self.move_down()
            sleep(1)
            self.stop_motors()
            sleep(1)

if __name__ == "__main__":
    
    motor_controller = MotorController()
    try:
        # Test the motor controller
        motor_controller.test_run()
    except Exception as e:
        print(f"Error in motor controller: {e}")
    finally:
        if USE_HARDWARE:
            GPIO.cleanup()  # Clean up GPIO settings to reset pins
