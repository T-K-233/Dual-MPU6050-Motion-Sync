import threading

import numpy as np
import serial

import bpy

# change this to your MCU COM port, can be viewed in Windows Device Manager
MCU_COM_PORT = "COM5"


# get scene armature object
armature = bpy.data.objects["Armature"]

# get the bones we need
bone_root = armature.pose.bones.get("Root")
bone_upper_arm_R = armature.pose.bones.get("J_Bip_R_UpperArm")
bone_lower_arm_R = armature.pose.bones.get("J_Bip_R_LowerArm")


# this is for syncing motion data between threads
gdata = []

is_stopped = False


def receiveSerial():
    global gdata
    ser = serial.Serial(MCU_COM_PORT)
    
    while not is_stopped:
        c = b""
        buf = b""
        while c != b"\n":
            buf += c
            c = ser.read()
        
        data = buf.decode()
        
        # remove the "println" artifact
        data = data.replace("\r", "")
        
        items = data.split("\t")
        
        # we should be getting 9 entries, two quats, and the last one being empty
        if len(items) != 9:
            print("<SerialHandler>: Incorrect packet received.")
            continue
        
        gdata = items
        
#        print(gdata)
    
    print("<SerialHandler>: Stopped.")
            

# a piece of math code copied from StackOverflow
def multiplyQuaternion(quaternion1, quaternion0):
    w0, x0, y0, z0 = quaternion0
    w1, x1, y1, z1 = quaternion1
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
        global gdata
        
        if event.type == "ESC":
            return self.cancel(context)
    
        if event.type == "TIMER":
            # this will eval true every Timer delay seconds
            items = gdata
            
            print(items)
            
            if not items:
                return  {"PASS_THROUGH"}
            
            w0 = float(items[0])
            x0 = float(items[1])
            y0 = float(items[2])
            z0 = float(items[3])
            w1 = float(items[4])
            x1 = float(items[5])
            y1 = float(items[6])
            z1 = float(items[7])
            
            # convert data to numpy arrays
            q0 = np.array([w0, x0, y0, z0])
            q1 = np.array([w1, x1, y1, z1])
            
            # get inverse transformation of q0, the parent bone
            q0_inv = np.array([w0, -x0, -y0, -z0])
            n
            
            # rotate child about parent, to get relative position of the child
            q1_rel = multiplyQuaternion(q0_inv, q1)
            
            # apply transformation
            bone_upper_arm_R.rotation_quaternion[0] = w0
            bone_upper_arm_R.rotation_quaternion[1] = x0
            bone_upper_arm_R.rotation_quaternion[2] = y0
            bone_upper_arm_R.rotation_quaternion[3] = z0
            
            bone_lower_arm_R.rotation_quaternion[0] = q1_rel[0]
            bone_lower_arm_R.rotation_quaternion[1] = q1_rel[1]
            bone_lower_arm_R.rotation_quaternion[2] = q1_rel[2]
            bone_lower_arm_R.rotation_quaternion[3] = q1_rel[3]

            # if refresh rate is too low, uncomment this line to force Blender to render viewport
#            bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
    
        return {"PASS_THROUGH"}

    def execute(self, context):
        # update rate is 0.01 second
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        
    def cancel(self, context):
        global is_stopped
        is_stopped = True
        context.window_manager.event_timer_remove(self._timer)
        print("<BlenderTimer>: Stopped.")
        return {"CANCELLED"}


if __name__ == "__main__":
    bpy.utils.register_class(ModalTimerOperator)

    # start serial handler    
    t = threading.Thread(target=receiveSerial)    
    t.start()

    # start Blender timer
    bpy.ops.wm.modal_timer_operator()
    
    print("All started.")
