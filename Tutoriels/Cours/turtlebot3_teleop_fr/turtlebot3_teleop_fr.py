# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 21:54:30 2023

@author: bouille arthur
INSA Strasbourg GE5
"""

import sys
import threading

import geometry_msgs.msg
import rclpy

if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

msg1 = """
Ce noeud prend les touches du clavier et les publie sous forme 
de messages Twist/TwistStamped.
"""

msg = """
---------------------------
Se déplacer :        Réglages vitesses :
   a    z    e       t/y : +/- 0.01 linéaire et +/- 0.05 angulaire
   q    s    d       g/h : +/- 0.01 linéaire
   w    x    c       b/n : +/- 0.05 angulaire
                       r : reset vitesses (0.1 et 1.0)

Autres touches : stop !

---------------------------

Ctrl-C pour fermer
"""

moveBindings = {
    'z': (1, 0, 0, 0),
    'e': (1, 0, 0, -1),
    'q': (0, 0, 0, 1),
    'd': (0, 0, 0, -1),
    'a': (1, 0, 0, 1),
    'x': (-1, 0, 0, 0),
    'w': (-1, 0, 0, -1),
    'c': (-1, 0, 0, 1),
}

speedBindings = {
    'r': (0.1, 1.0), # Reset vitesses
    't': (0.01, 0.05),
    'y': (-0.01, -0.05),
    'g': (0.01, 0),
    'h': (-0.01, 0),
    'b': (0, 0.05),
    'n': (0, -0.05),

}

def getKey(settings):
    if sys.platform == 'win32':
        # getwch() returns a string on Windows
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        # sys.stdin.read() returns a string on Linux
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def vels(speed, turn):
    return 'Actuellement :\tLinear_vel = %s\tAngular_vel = %s ' % (speed, turn)


def main():
    settings = saveTerminalSettings()

    rclpy.init()

    node = rclpy.create_node('teleop_keyboard_fr')

    # parameters
    stamped = node.declare_parameter('stamped', False).value
    frame_id = node.declare_parameter('frame_id', '').value
    if not stamped and frame_id:
        raise Exception("'frame_id' can only be set when 'stamped' is True")

    if stamped:
        TwistMsg = geometry_msgs.msg.TwistStamped
    else:
        TwistMsg = geometry_msgs.msg.Twist

    pub = node.create_publisher(TwistMsg, 'cmd_vel', 10)

    spinner = threading.Thread(target=rclpy.spin, args=(node,))
    spinner.start()

    speed = 0.1
    turn = 1.0
    x = 0.0
    y = 0.0
    z = 0.0
    th = 0.0
    status = 0.0

    twist_msg = TwistMsg()

    if stamped:
        twist = twist_msg.twist
        twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist_msg.header.frame_id = frame_id
    else:
        twist = twist_msg

    try:
        print(msg1)
        print(msg)
        print(vels(speed, turn))
        while True:
            key = getKey(settings)
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                y = moveBindings[key][1]
                z = moveBindings[key][2]
                th = moveBindings[key][3]
                
            elif key in speedBindings.keys():
                if key != 'r': # Si pas reset on modifie les valeurs de vitesses 
                    speed = round(speed + speedBindings[key][0],2)
                    turn = round(turn + speedBindings[key][1],2)
                    # Vérification par rapport au valeur de vitesse max pour le turtlebot burger
                    # 0.22 en linéaire et 2.84 en angulaire
                    if speed > 0.22:
                        speed = 0.22
                        print("Vitesse linéaire 0.22 maximum !")
                    elif speed < -0.22:
                        speed = -0.22
                        print("Vitesse linéaire -0.22 minimum !")
                    if turn > 2.84:
                        turn = 2.84
                        print("Vitesse angulaire 2.84 maximum !")
                    elif turn < -2.84:
                        turn = -2.84
                        print("Vitesse angulaire -2.84 minimum !")

                else:          # On reset les valeurs des vitesses si 'r'
                    speed = 0.1
                    turn = 1.0

                print(vels(speed, turn))

                if (status == 14):
                    print(msg)
                status = (status + 1) % 15    
                    

            else:
                x = 0.0
                y = 0.0
                z = 0.0
                th = 0.0
                if (key == '\x03'):
                    break

            if stamped:
                twist_msg.header.stamp = node.get_clock().now().to_msg()

            twist.linear.x = x * speed
            twist.linear.y = y * speed
            twist.linear.z = z * speed
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = th * turn
            pub.publish(twist_msg)

    except Exception as e:
        print(e)

    finally:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()

        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        pub.publish(twist_msg)
        rclpy.shutdown()
        spinner.join()

        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()
