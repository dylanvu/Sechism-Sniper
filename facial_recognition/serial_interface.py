import time
import serial

def sendCommand(command, ser):
    print(f"Sending {command}")

    # convert the string to bytes
    # commandBytes = command.encode('utf-8')
    ser.write(bytes(command, "utf-8"))
    # while True:
    #     pass
    # print(commandBytes)
    # ser.close()

if __name__ == "__main__":
    # port = "/dev/ttyUSB0" # rpi
    port = "COM9" # windows, FIXME
    ser = serial.Serial(port=port, baudrate=115200, timeout=0.1)
    time.sleep(2)
    sendCommand("0", ser)