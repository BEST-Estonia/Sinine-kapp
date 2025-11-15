import serial
import time

# --- Configuration ---
# !! IMPORTANT: Change 'COM3' to your Arduino's serial port
# On Linux/Mac, it might be '/dev/ttyUSB0' or '/dev/tty.usbmodem14201'
ARDUINO_PORT = 'COM3'
BAUDRATE = 9600
TIMEOUT = 5 # Time in seconds to wait for a response

# --- Global Serial Object ---
# This single object will hold our connection
ser = None

def connect():
    """
    Establishes the serial connection to the Arduino.
    You MUST call this before any other function.
    Returns True on success, False on failure.
    """
    global ser
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUDRATE, timeout=TIMEOUT)
        # Wait for the Arduino to reset (common on connection)
        time.sleep(2)
        # Read any "ready" message from Arduino
        init_message = ser.readline().decode('utf-8').strip()
        print(f"Arduino says: {init_message}")
        print(f"Serial connection established on {ARDUINO_PORT}.")
        return True
    except serial.SerialException as e:
        print(f"Error connecting to {ARDUINO_PORT}: {e}")
        ser = None
        return False

def disconnect():
    """
    Closes the serial connection. Call this when your program exits.
    """
    global ser
    if ser and ser.is_open:
        ser.close()
        print("Serial connection closed.")
        ser = None

def _send_command(command):
    """
    Internal helper to send a command.
    """
    global ser
    if not ser or not ser.is_open:
        print("Error: Serial connection is not open. Call connect() first.")
        return False
        
    full_command = (command + '\n').encode('utf-8')
    ser.write(full_command)
    print(f"Sent command: {command}")
    return True

def _read_response():
    """
    Internal helper to read a response.
    """
    global ser
    if not ser or not ser.is_open:
        print("Error: Serial connection is not open.")
        return None
        
    response = ser.readline().decode('utf-8').strip()
    print(f"Received: {response}")
    return response

def get_nfc():
    """
    Sends 'N' to Arduino, waits for, and returns the NFC tag ID.
    Returns None on timeout or error.
    """
    print("Requesting NFC scan from Arduino...")
    if not _send_command('N'):
        return None
        
    # Wait for the response from the Arduino
    response = _read_response()
    
    if response and response.startswith("ERROR:"):
        print(f"Arduino error: {response}")
        return None
    elif not response:
        print("Error: No response from Arduino (timeout).")
        return None
        
    # If we got a valid response, it should be the ID
    return response

def wheight():
    """
    Sends the 'Y' command to start the weighting program.
    Returns True if the Arduino acknowledges, False otherwise.
    """
    print("Requesting Arduino to start weighting...")
    if not _send_command('Y'):
        return False
    
    # Wait for the acknowledgment
    response = _read_response()
    
    if response == "ACK:Weighting":
        print("Weighting program acknowledged.")
        return True
    else:
        print(f"Error: Unexpected response to weighting command: {response}")
        return False