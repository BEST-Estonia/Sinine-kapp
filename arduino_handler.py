import serial
import time

# --- Configuration ---
ARDUINO_PORT = 'COM3'  # Change this to your port
BAUDRATE = 9600
TIMEOUT = 5

ser = None

def connect():
    """
    Establish the serial connection to the Arduino.
    """
    global ser
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUDRATE, timeout=TIMEOUT)
        time.sleep(3)  # Allow Arduino to reboot on serial connect

        # Clear Arduino boot messages
        ser.reset_input_buffer()

        print(f"Serial connection established on {ARDUINO_PORT}")
        return True
    except serial.SerialException as e:
        print(f"Error connecting to {ARDUINO_PORT}: {e}")
        ser = None
        return False


def disconnect():
    """
    Close the serial connection.
    """
    global ser
    if ser and ser.is_open:
        ser.close()
        print("Serial connection closed.")
        ser = None


def _send_command(command):
    """
    Internal helper to send a command (with newline).
    """
    global ser
    if not ser or not ser.is_open:
        print("Error: Serial connection is not open.")
        return False

    ser.write((command + '\n').encode('utf-8'))
    return True


def _read_response():
    """
    Internal helper to read a string response.
    """
    global ser
    if not ser or not ser.is_open:
        print("Error: Serial connection is not open.")
        return None

    try:
        response = ser.readline().decode('utf-8').strip()
        print("Received:", response)
        return response
    except Exception as e:
        print("Read error:", e)
        return None


def get_nfc():
    """
    Requests the Arduino to read an NFC card.
    Returns UID string or None on failure.
    """
    print("Requesting NFC scan...")

    if not _send_command("N"):
        return None

    response = _read_response()

    if not response:
        print("Error: No response (timeout).")
        return None

    if response.startswith("ERROR"):
        print("Arduino error:", response)
        return None

    return response  # Valid NFC ID


def wheight():
    """
    Request the Arduino to start the weighting program.
    """
    print("Requesting weighting...")

    if not _send_command("Y"):
        return False

    response = _read_response()

    if response == "ACK:Weighting":
        print("Weighting acknowledged.")
        return True

    print("Unexpected weighting response:", response)
    return False
