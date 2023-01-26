#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps612.h"

/**
 * # Wiring
 * | MPU6050 | Arduino   |
 * | ------- | --------- |
 * | GND     | GND       |
 * | VCC     | 3V3       |
 * | SCL     | SCL       |
 * | SDA     | SDA       |
 * | ADD     | see below |
 * 
 * ## ADDR pin configuration:
 * 
 * ADDR low = 0x68 (default)
 * ADDR high = 0x69
 */

// initialize the two MPUs with their I2C ID
MPU6050 mpu68(0x68);
MPU6050 mpu69(0x69);

uint8_t error_code = 0U;      // return status after each device operation (0 = success, !0 = error)

void setup() {
  Wire.begin();

  // it seems that we cannot use too high clock rate, due to the long I2C wire.
  // cannot flash firmware if signal integrity is too bad.
  // Wire.setClock(400000);
  Wire.setClock(100000);

  Serial.begin(115200);
  
  // initialize device
  Serial.print("{\"key\": \"/log\", \"value\": \"Initializing device 0x68...\", \"level\": \"DEBUG\"}\n");
  mpu68.initialize();
  error_code = mpu68.dmpInitialize();
  
  // 1 = initial memory load failed
  // 2 = DMP configuration updates failed
  // (if it's going to break, usually the code will be 1)
  if (error_code == 1U) {
    Serial.print("{\"key\": \"/log\", \"value\": \"device 0x68 initialization failed: initial memory load failed.\", \"level\": \"ERROR\"}\n");
    while (1) {}
  }
  if (error_code == 2U) {
    Serial.print("{\"key\": \"/log\", \"value\": \"device 0x68 initialization failed: DMP configuration updates failed.\", \"level\": \"ERROR\"}\n");
    while (1) {}
  }
  
  Serial.print("{\"key\": \"/log\", \"value\": \"Initializing device 0x69...\", \"level\": \"DEBUG\"}\n");
  mpu69.initialize();
  error_code = mpu69.dmpInitialize();

  // 1 = initial memory load failed
  // 2 = DMP configuration updates failed
  // (if it's going to break, usually the code will be 1)
  if (error_code == 1U) {
    Serial.print("{\"key\": \"/log\", \"value\": \"device 0x68 initialization failed: initial memory load failed.\", \"level\": \"ERROR\"}\n");
    while (1) {}
  }
  if (error_code == 2U) {
    Serial.print("{\"key\": \"/log\", \"value\": \"device 0x68 initialization failed: DMP configuration updates failed.\", \"level\": \"ERROR\"}\n");
    while (1) {}
  }

  // verify connection
  if (!mpu68.testConnection()) {
    Serial.print("{\"key\": \"/log\", \"value\": \"device 0x68 connection failed.\", \"level\": \"ERROR\"}\n"); 
  }
  if (!mpu69.testConnection()) {
    Serial.print("{\"key\": \"/log\", \"value\": \"device 0x69 connection failed.\", \"level\": \"ERROR\"}\n");
  }

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

  
  // Calibration Time: generate offsets and calibrate our MPU6050
  mpu68.CalibrateAccel(6);
  mpu68.CalibrateGyro(6);
  
  mpu69.CalibrateAccel(6);
  mpu69.CalibrateGyro(6);

  // calibration procedure will dump garbage on serial, we use a newline to fence it
  Serial.print("\n");
  
  // turn on the DMP, now that it's ready
  Serial.print("{\"key\": \"/log\", \"value\": \"Enabling DMP...\", \"level\": \"DEBUG\"}\n");
  mpu68.setDMPEnabled(true);
  mpu69.setDMPEnabled(true);
  Serial.print("{\"key\": \"/log\", \"value\": \"Device ready.\", \"level\": \"INFO\"}\n");
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
  
  Serial.print("{\"key\": \"/joint/0\", \"value\": [");
  Serial.print(q68.w);Serial.print(", ");
  Serial.print(q68.x);Serial.print(", ");
  Serial.print(q68.y);Serial.print(", ");
  Serial.print(q68.z);
  Serial.print("]}\n");
  
  Serial.print("{\"key\": \"/joint/1\", \"value\": [");
  Serial.print(q69.w);Serial.print(", ");
  Serial.print(q69.x);Serial.print(", ");
  Serial.print(q69.y);Serial.print(", ");
  Serial.print(q69.z);
  Serial.print("]}\n");
}
