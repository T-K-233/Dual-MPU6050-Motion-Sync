# Dual MPU6050 Motion Sync

## Usage

1. Put stuff in `library` to Arduino library folder.

2. Connect hardware. Should be straghtforward, just an Arduino controller + two MPU6050s connected with I2C wires. The wires cannot be too long (I'm using a total length of ~600mm).

3. Upload Arduino code to MCU.

4. Open Blender and change the `MCU_COM_PORT` value to what Arduino is currently using (can be checked in Device Manager, or just Arduino IDE).

5. Run the script. Blender could halt for a while due to Arduino initializing the MPU6050s.

## Video

[Bilibili](https://www.bilibili.com/video/BV1jZ4y1z7R7/)

[Youtube](https://www.youtube.com/watch?v=F1IdRtIDdIs)

## License

Code in this repository is under MIT License and GPLv3 License.

Model in Blender file is under Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0) License.
