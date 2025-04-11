import rclpy
# import can 
from rclpy.node import Node
from sensor_msgs.msg import Joy

class JoySubscriber(Node):
    def __init__(self):
        super().__init__('joy_subscriber')
        self.joy_subscription = self.create_subscription(
            Joy,
            '/remote_joy',
            self.joy_callback,
            10
        )
        # self.can_bus = can.interface.Bus(channel='can0', bustype='socketcan')  # ← コメントアウト

    def joy_callback(self, msg):
        try:
            vx = msg.axes[0]
            vy = msg.axes[1]
            omega = msg.axes[2]
            
            lx = 0.25
            ly = 0.25

            v1 = vx + vy + (lx + ly) * omega
            v2 = -vx + vy + (lx + ly) * omega
            v3 = -vx - vy + (lx + ly) * omega
            v4 = vx - vy + (lx + ly) * omega

            motor_speeds = [
                self.scale_speed(v1),
                self.scale_speed(v2),
                self.scale_speed(v3),
                self.scale_speed(v4)
            ]

            button_values = []
            for i in range(0, 8, 2):
                value = self.button_pair_value(msg.buttons[i], msg.buttons[i + 1])
                button_values.append(self.scale_from_button(value))

            can_data = motor_speeds + button_values  # 8バイト想定

            # CAN送信はコメントアウト
            # can_message = can.Message(arbitration_id=0x123, data=can_data, is_extended_id=False)
            # self.can_bus.send(can_message)

            self.get_logger().info(f'[DEBUG] Would send CAN data: {can_data}')

        except Exception as e:
            self.get_logger().error(f'Failed to process Joy message: {e}')

    def scale_speed(self, value):
        """-1.0～1.0 → 0～254"""
        return max(0, min(254, int((value + 1.0) * 127)))

    def button_pair_value(self, left_button, right_button):
        """左→+127, 右→-127, 両方/なし→0"""
        if left_button == 1 and right_button == 0:
            return 127
        elif right_button == 1 and left_button == 0:
            return -127
        else:
            return 0

    def scale_from_button(self, value):
        """-127～127 → 0～254"""
        return max(0, min(254, value + 127))

def main(args=None):
    rclpy.init(args=args)
    node = JoySubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped cleanly')
    except Exception as e:
        node.get_logger().error(f'Exception: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

