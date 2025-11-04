# detect_arm File Usage Documentation

## 1. First, you need to use piper_sdk version 0.3.0 or above

Check the pip package version

```bash
pip3 show piper_sdk
```

Output

```bash
Name: piper_sdk
Version: 0.3.0
Summary: A sdk to control Agilex piper arm
Home-page: https://github.com/agilexrobotics/piper_sdk
Author: RosenYin
Author-email: 
License: MIT License
Location: .../.local/lib/python3.8/site-packages
Requires: python-can
Required-by: 
```

## 2. Execute detect_arm.py

Note the path - use the `piper_sdk` package inside the `Location` path shown above. You can obtain it using the following command:

```bash
export PIPER_SDK_PATH=$(pip3 show piper_sdk | grep ^Location: | awk '{print $2}')
```

```bash
echo $PIPER_SDK_PATH
```

The file has three input parameters:

- `--can_port` is used to set the CAN port name to read from
- `--hz` is used to set the terminal print refresh frequency
- `--req_flag` is used to set whether to send request query commands to the robotic arm when executing the script to obtain some static parameters of the arm, such as firmware version, maximum joint velocity, etc.

Under normal circumstances, execute the following command:

Note: `PIPER_SDK_PATH` is obtained from the above command

```bash
python3 $PIPER_SDK_PATH/piper_sdk/demo/detect_arm.py --can_port can0 --hz 10 --req_flag 1
```
