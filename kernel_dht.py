import time

def read_sensor():
    # The Linux Kernel automatically creates these files and updates them
    temp_file = "/sys/bus/iio/devices/iio:device0/in_temp_input"
    hum_file = "/sys/bus/iio/devices/iio:device0/in_humidityrelative_input"
    
    try:
        with open(temp_file, "r") as f:
            # IIO files report in milli-units (e.g., 25000 = 25.0 C)
            temperature = float(f.read()) / 1000.0
            
        with open(hum_file, "r") as f:
            humidity = float(f.read()) / 1000.0
            
        return temperature, humidity
    except OSError:
        # If the file is temporarily locked by the kernel updating it
        return None, None
    except FileNotFoundError:
        print("Error: Sensor not found. Did you add the dtoverlay and reboot?")
        exit(1)

if __name__ == "__main__":
    print("Reading DHT11 via Linux Kernel... Press Ctrl+C to stop.")
    while True:
        temp, hum = read_sensor()
        if temp is not None:
            print(f"Temperature: {temp:.1f}°C | Humidity: {hum:.1f}%")
        else:
            print("Waiting for sensor stabilization...")
        
        # The DHT11 physical hardware requires 2 seconds between updates
        time.sleep(2)