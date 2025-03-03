PC1
terminal1 ros2 run joy joy_node
terminal2 cd robocon_ws
          source install/setup.bash
	  ros2 run joy_communication joy_publisher

PC2
terminal1 cd robocon_ws_2025/robocon_ws
	  source install/setup.bash
	  ros2 run joy_communication joy_subscriber
