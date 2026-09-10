import time
import board
import adafruit_dht

# Initialize the DHT22 device on GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

def read_sensor():
    while True:
        try:
            # Retrieve temperature and humidity data
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity

            print(f"Temperature: {temperature_c:.1f}°C | Humidity: {humidity:.1f}%")

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(f"Read error: {error.args[0]}. Retrying...")
            time.sleep(2.0)
            continue
        except Exception as error:
            # Safely exit the sensor connection if a fatal error occurs
            dht_device.exit()
            raise error

        # DHT22 requires at least 2 seconds between readings
        time.sleep(2.0)

if __name__ == "__main__":
    try:
        print("Starting DHT22 reading... Press Ctrl+C to quit.")
        read_sensor()
    except KeyboardInterrupt:
        print("\nExiting and cleaning up...")
        dht_device.exit() 