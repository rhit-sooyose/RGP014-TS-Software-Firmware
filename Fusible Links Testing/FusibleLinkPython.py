import serial
import csv
import datetime
import time
import os  # <-- Added this import

# --- USER: CONFIGURE THESE SETTINGS ---

# Find this in the Arduino IDE under "Tools -> Port"
# Examples: "COM3" (Windows), "/dev/ttyUSB0" or "/dev/ttyACM0" (Linux/Mac)
SERIAL_PORT = "COM6"  # <--- CHANGE THIS to your Arduino's serial port

# This MUST match the SERIAL_BAUD_RATE in the Arduino code
BAUD_RATE = 115200

# --- END OF CONFIGURATION ---

def get_output_filename():
    """Generates a unique CSV filename with a timestamp."""
    now = datetime.datetime.now()
    return f"fusible_link_test_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"

def connect_to_arduino(port, baud):
    """Tries to connect to the Arduino, retrying if necessary."""
    print(f"Attempting to connect to Arduino on {port} at {baud} baud...")
    while True:
        try:
            ser = serial.Serial(port, baud, timeout=2)
            print("Connection successful. Waiting for data...")
            # Wait for Arduino to reset (common on connection)
            time.sleep(2)
            # Flush any initial data (like the "Starting log..." message)
            ser.flushInput()
            # Read and discard the first few lines to get to the data
            for _ in range(3):
                 ser.readline()
            print("Ready to log data.")
            return ser
        except serial.SerialException:
            print(f"Connection failed. Retrying in 3 seconds...")
            time.sleep(3)

def log_data():
    """Main function to read from serial and write to CSV."""
    
    # --- New code to define file path ---
    # Get the directory where this python script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Generate the base filename
    base_filename = get_output_filename()
    # Join the script's directory and the filename to get the full path
    output_filepath = os.path.join(script_dir, base_filename)
    # --- End of new code ---
    
    try:
        # Open the serial port
        ser = connect_to_arduino(SERIAL_PORT, BAUD_RATE)
        
        # Open the CSV file for writing using the new full path
        with open(output_filepath, 'w', newline='') as csvfile:
            # Create a CSV writer object
            csv_writer = csv.writer(csvfile)
            
            # Write the header row
            csv_writer.writerow(['Timestamp (ms)', 'Current (A)'])
            
            print(f"\nLogging data to {output_filepath}")  # <-- Changed to show full path
            print("Press Ctrl+C to stop logging.")
            
            while True:
                try:
                    # Read a line of data from the Arduino
                    # The 'b' prefix means it's a 'bytes' object
                    line_bytes = ser.readline()
                    
                    # Decode from bytes to a standard string (e.g., "1234,15.25")
                    # Use 'utf-8' encoding and strip any whitespace (\r\n)
                    line_str = line_bytes.decode('utf-8').strip()
                    
                    # Ensure the line is not empty and looks like our data
                    if line_str and ',' in line_str:
                        # Split the string "1234,15.25" into a list ["1234", "15.25"]
                        data_list = line_str.split(',')
                        
                        if len(data_list) == 2:
                            # Write this list as a new row in the CSV
                            csv_writer.writerow(data_list)
                            
                            # Optional: Print to console to see data in real-time
                            print(f"Logged: {data_list[0]} ms, {data_list[1]} A")
                        
                except Exception as e:
                    print(f"Error reading line: {e}")

    except KeyboardInterrupt:
        # This block runs when you press Ctrl+C
        print("\nLogging stopped by user.")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        
    finally:
        # This will run whether the script finishes or is interrupted
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")
        print(f"Data logging complete. File saved as: {output_filepath}")  # <-- Changed to show full path

# --- Main execution ---
if __name__ == "__main__":
    # Check if pySerial is installed
    try:
        import serial
    except ImportError:
        print("Error: The 'pySerial' library is required.")
        print("Please install it by running: pip install pyserial")
        exit()
        
    log_data()