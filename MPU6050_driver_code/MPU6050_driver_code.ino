#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps612.h"


// AD0 low = 0x68 (default)
// AD0 high = 0x69

// we will call these two by their I2C ID
MPU6050 mpu68(0x68);
MPU6050 mpu69(0x69);

uint8_t device_error;      // return status after each device operation (0 = success, !0 = error)


void setup() {
  Wire.begin();

  // it seems that we cannot use too high clock rate, due to the long I2C wire.
  // cannot flash firmware if signal integrity is too bad.
//  Wire.setClock(400000);
  Wire.setClock(100000);

  Serial.begin(115200);
  
  // initialize device
  Serial.println(F("Initializing MPU68..."));
  mpu68.initialize();  
  device_error = mpu68.dmpInitialize();
  Serial.println(device_error);

  Serial.println(F("Initializing MPU69..."));
  mpu69.initialize();
  device_error |= mpu69.dmpInitialize();
  Serial.println(device_error);

  // verify connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu68.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));
  Serial.println(mpu69.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // supply your own gyro offsets here, scaled for min sensitivity
  mpu68.setXGyroOffset(0);
  mpu68.setYGyroOffset(0);
  mpu68.setZGyroOffset(0);
  mpu68.setXAccelOffset(0);
  mpu68.setYAccelOffset(0);
  mpu68.setZAccelOffset(0);
  
  mpu69.setXGyroOffset(0);
  mpu69.setYGyroOffset(0);
  mpu69.setZGyroOffset(0);
  mpu69.setXAccelOffset(0);
  mpu69.setYAccelOffset(0);
  mpu69.setZAccelOffset(0);

  // make sure it worked (returns 0 if so)
  if (device_error) { 
    // ERROR!
    // 1 = initial memory load failed
    // 2 = DMP configuration updates failed
    // (if it's going to break, usually the code will be 1)
    while (1) {
      Serial.print(F("DMP Initialization failed (code "));
      Serial.print(device_error);
      Serial.println(F(")"));
    }
  }
  
  // Calibration Time: generate offsets and calibrate our MPU6050
  mpu68.CalibrateAccel(6);
  mpu68.CalibrateGyro(6);
  
  mpu69.CalibrateAccel(6);
  mpu69.CalibrateGyro(6);
  
  mpu68.PrintActiveOffsets();
  mpu69.PrintActiveOffsets();
  
  // turn on the DMP, now that it's ready
  Serial.println(F("Enabling DMP..."));
  mpu68.setDMPEnabled(true);
  mpu69.setDMPEnabled(true);
}

void loop() {
  // Get the Latest packet 
  uint8_t fifo_buffer68[64]; // FIFO storage buffer
  if (!mpu68.dmpGetCurrentFIFOPacket(fifo_buffer68)) {
    return;
  }

  uint8_t fifo_buffer69[64]; // FIFO storage buffer
  if (!mpu69.dmpGetCurrentFIFOPacket(fifo_buffer69)) {
    return;
  }
  
  // orientation/motion vars
  Quaternion q68;           // [w, x, y, z]         quaternion container
  Quaternion q69;           // [w, x, y, z]         quaternion container

  mpu68.dmpGetQuaternion(&q68, fifo_buffer68);
  mpu69.dmpGetQuaternion(&q69, fifo_buffer69);
  
  Serial.print(q68.w);Serial.print("\t");
  Serial.print(q68.x);Serial.print("\t");
  Serial.print(q68.y);Serial.print("\t");
  Serial.print(q68.z);Serial.print("\t");
  
  Serial.print(q69.w);Serial.print("\t");
  Serial.print(q69.x);Serial.print("\t");
  Serial.print(q69.y);Serial.print("\t");
  Serial.print(q69.z);Serial.print("\t");

  Serial.println();
}
