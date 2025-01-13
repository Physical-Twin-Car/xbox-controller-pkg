import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32, Bool
from my_robot_interfaces.msg import BesturingsData
from geometry_msgs.msg import Twist  # For simulation
import pygame
from datetime import datetime

class XboxControllerNode(Node):
    def __init__(self):
        super().__init__('xbox_controller_node')

        self.controller_publisher = self.create_publisher(BesturingsData, 'besturings_data', 10)
        self.parkour_publisher = self.create_publisher(Bool, 'lidar_parkour_mode', 10)

        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.started = False
        self.prev_a = 0
        self.mode = 0
        self.timer = self.create_timer(0.04, self.read_controller)  # 100Hz

    def read_controller(self):
        pygame.event.pump()
        
        # A button for activation
        a_button = self.joystick.get_button(0)  # A button

        # Check if A button is pressed for 1.5 seconds to activate
        if a_button == 1 and self.prev_a == 0:
            self.start_time = datetime.now()
        elif a_button == 1 and self.start_time and (datetime.now() - self.start_time).total_seconds() > 1.5:
            self.started = True
            
        self.prev_a = a_button
        
        DPad_up = self.joystick.get_hat(0) == (0, 1)
        DPad_down = self.joystick.get_hat(0) == (0, -1)
        # DPad_left = self.joystick.get_hat(0) == (-1, 0) # niet in gebruik
        # DPad_right = self.joystick.get_hat(0) == (1, 0) # niet in gebruik

        #testen van dpad controller
        #print(f'up dpad: {up_DPad}')
        #print(f'down dpad: {down_DPad}')

        if DPad_up == True: # controller mode
            self.mode = 1
            self.send_parkour_message(False)
        elif DPad_down == True: # lidar parkour mode
            self.started = False
            self.mode = 2
            print("Lidar Parkour mode activated.")
            self.send_parkour_message(True)
            

        if self.mode == 1:
            if not self.started:
                print("Controller mode activated. Hold 'A' for 1.5 seconds to activate the system.")
                return

        if self.mode == 0:
            print(f'Mode: {self.mode}. Pick a mode: D-pad up for controller. D-pad down for lidar parkour.')
            return
               
        
        if self.mode == 1 and self.started:
            throttle = (self.joystick.get_axis(4) + 1) / 2  # Right trigger for throttle
            brake = (self.joystick.get_axis(5) + 1) / 2  # Left trigger for brake
            steering = self.joystick.get_axis(0)  # Left joystick for steering
        
            steering = self.ignore_drift_zone(steering)
            
            # Define direction based on button presses
            direction = 0  # Neutral by default
            if self.joystick.get_button(1):  # 'B' button forward
                direction = 1
            elif self.joystick.get_button(3):  # 'X' button reverse
                direction = 2
            elif self.joystick.get_button(4):  # 'Y' button neutral
                direction = 0

            # Create a BesturingsData message for real car
            besturings_data = BesturingsData()
            besturings_data.throttle = float(throttle)
            besturings_data.steering = float(steering)
            besturings_data.direction = int(direction)
            besturings_data.brake = float(brake)

            print(f"Throttle: {throttle}, Brake: {brake}, Steering: {steering}, Direction: {direction}")

            # Publish the message
            self.controller_publisher.publish(besturings_data)


    def ignore_drift_zone(self, value):
        drift_zone = 0.05
        if abs(value) < drift_zone:
            return 0
        return value
    
    def send_parkour_message(self, status):
        msg = Bool()
        msg.data = status
        self.parkour_publisher.publish(msg)
        print('Bericht verzonden naar lidar_parkour_node topic: "%s"' % msg.data)


        


def main(args=None):
    rclpy.init(args=args)
    node = XboxControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
