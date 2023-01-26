# Motion Sync

## Prerequisite

Requires [I2CDev Library](https://github.com/jrowberg/i2cdevlib) for reading MPU6050 on Arduino.


## Usage

1. Connect hardware. The wiring diagram is documented inside Arduino script. Should be straghtforward, just an Arduino controller + two MPU6050s connected with I2C wires. The wires cannot be too long (I'm using a total length of ~600mm).

2. Upload Arduino code to MCU.

3. Open Blender and change the `MCU_COM_PORT` value to what Arduino is currently using (can be checked in Device Manager, or just Arduino IDE).

4. Run the script. The MPU6050 needs ~8 seconds to initialize before start transmitting data, so initially the armature won't move, and the script will prompt something like `2023-01-25 18:01:28 WARNING [BPY]: Invalid joint data `

5. Press ESC at the main Blender window to stop the script.

## Packet Format

Data is streamed from the sensor to the host computer in JSON key-value pair encoding format.

### Joint Data Message

```json
{"key": "/joint/joint_name", "value": [0, 0, 0, 0]}\n
```

where `pos` is in format `[x, y, z]`, and `rot` is in format `[w, x, y, z]`.


### System Log Message

```json
{"key": "/log", "value": "INFO: log message"}\n
```

#### Note: all the newline character in the data should be escaped with NLSM encoding.

## Video

[Bilibili](https://www.bilibili.com/video/BV1jZ4y1z7R7/)

[Youtube](https://www.youtube.com/watch?v=F1IdRtIDdIs)

## License

Code in this repository is under MIT License and GPLv3 License.

Model in Blender file is under Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0) License.
