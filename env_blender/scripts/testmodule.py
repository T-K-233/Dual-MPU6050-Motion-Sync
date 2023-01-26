import sys
import os
import json
import logging

import bpy
import numpy as np
import serial

sys.path.append(os.path.join(bpy.path.abspath("//"), "scripts"))

from uartcomm import UARTTable

MCU_COM_PORT = "COM5"
#FPS = 30        # use 30 if system performance is poor
FPS = 60


# set up logging
logger = logging.getLogger("BPY")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setStream(sys.stdout)
    ch.setLevel(logging.DEBUG)
    # ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s::%(threadName)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)


# get scene armature object
armature = bpy.data.objects["Armature"]

# get the bones we need
bone_root = armature.pose.bones.get("Root")
bone_upper_arm_R = armature.pose.bones.get("J_Bip_R_UpperArm")
bone_lower_arm_R = armature.pose.bones.get("J_Bip_R_LowerArm")

uart_table = UARTTable(MCU_COM_PORT, logging_level=logging.DEBUG)

"""
@param bone: the bone object, obtained from armature.pose.bone["<bone_name>"]
@param rotation: rotation in quaternion (w, x, y, z)
"""
def setBoneRotation(bone, rotation):
    w, x, y, z = rotation
    bone.rotation_quaternion[0] = w
    bone.rotation_quaternion[1] = x
    bone.rotation_quaternion[2] = y
    bone.rotation_quaternion[3] = z

"""
a piece of math code copied from StackOverflow
https://stackoverflow.com/questions/39000758/how-to-multiply-two-quaternions-by-python-or-numpy

@param q1: in form (w, x, y, z)
@param q0: @see q1
"""
def multiplyQuaternion(q1, q0):
    w0, x0, y0, z0 = q0
    w1, x1, y1, z1 = q1
    return np.array([-x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,
                     x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
                     -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
                     x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0], dtype=np.float64)
                     

class ModalTimerOperator(bpy.types.Operator):
    # we need these two fields for Blender
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"
    
    _timer = None
    
    def modal(self, context, event):
        if event.type == "ESC":
            logger.info("BlenderTimer received ESC.")
            return self.cancel(context)
    
        if event.type == "TIMER":
            # this will eval true every Timer delay seconds
            q0 = uart_table.get("/joint/0")
            q1 = uart_table.get("/joint/1")
            
            if not q0 or not q1:
                logger.warning("Invalid joint data")
                return {"PASS_THROUGH"}
            
            # convert data to numpy arrays
            q0 = np.array(q0)
            q1 = np.array(q1)
            
            logger.debug(str(q0) + str(q1))
            
            # get inverse transformation of q0, the parent bone
            q0_inv = q0 * np.array([1, -1, -1, -1])
            
            # rotate child about parent, to get relative position of the child
            q1_rel = multiplyQuaternion(q0_inv, q1)
            
            # apply transformation
            setBoneRotation(bone_upper_arm_R, q0)
            setBoneRotation(bone_lower_arm_R, q1_rel)

            # if refresh rate is too low, uncomment this line to force Blender to render viewport
#            bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
    
        return {"PASS_THROUGH"}

    def execute(self, context):
        # update rate is 0.01 second
        self._timer = context.window_manager.event_timer_add(1./FPS, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        
    def cancel(self, context):
        uart_table.stop()
        
        # reset joint position
        setBoneRotation(bone_upper_arm_R, [1, 0, 0, 0])
        setBoneRotation(bone_lower_arm_R, [1, 0, 0, 0])
        context.window_manager.event_timer_remove(self._timer)
        logger.info("BlenderTimer Stopped.")
        return {"CANCELLED"}


if __name__ == "__main__":
    try:
        logger.info("Starting services.")
        bpy.utils.register_class(ModalTimerOperator)
        
        # uart_table.start()
        uart_table.startThreaded()
        
        # start Blender timer
        bpy.ops.wm.modal_timer_operator()
        
        logger.info("All started.")
    except KeyboardInterrupt:
        uart_table.stop()
        logger.info("Received KeyboardInterrupt, stopped.")
