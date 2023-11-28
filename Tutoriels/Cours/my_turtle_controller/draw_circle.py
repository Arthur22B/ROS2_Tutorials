import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class DrawCircleNode(Node):

    def __init__(self):
        super().__init__('draw_circle')
        self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.send_velocity_command)
        self.get_logger().info("Draw circle node has been started")

    def send_velocity_command(self):
        msg = Twist()
        msg.linear.x = 2.0
        #msg.linear.y = 1.0
        msg.angular.z = 1.0
        self.cmd_vel_pub_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node =DrawCircleNode()
    rclpy.spin(node)
    rclpy.shutdown()
