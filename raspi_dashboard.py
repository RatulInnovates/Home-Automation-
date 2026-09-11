import os

os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")

from flask import Flask, jsonify, render_template, request
from gpiozero import LED, MotionSensor

import board
import adafruit_dht

from door_state import read_state, record_activity, set_gas_alarm, set_output, write_state

app = Flask(__name__, template_folder="templates", static_folder="static")

pir = None
pir_error = None

try:
    pir = MotionSensor(27)
except Exception as exc:
    pir_error = str(exc)

try:
    dht_device = adafruit_dht.DHT11(board.D4)
except Exception as exc:
    dht_device = None
    dht_init_error = str(exc)
else:
    dht_init_error = None

try:
    light = LED(17)
except Exception:
    light = None

try:
    fan = LED(18)
except Exception:
    fan = None

last_motion_state = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    global last_motion_state

    current_motion = False
    if pir is not None:
        current_motion = bool(pir.motion_detected)
        if current_motion and not last_motion_state:
            record_activity("motion", "Motion detected in the entrance area.")
    last_motion_state = current_motion

    state = read_state()

    temp = None
    humidity = None
    sensor_error = None

    if dht_device is not None:
        try:
            temp = dht_device.temperature
            humidity = dht_device.humidity
        except Exception as exc:
            sensor_error = str(exc)
    else:
        sensor_error = dht_init_error

    if temp is not None:
        temp = round(temp, 1)
    if humidity is not None:
        humidity = round(humidity, 1)

    return jsonify(
        {
            "motion_detected": current_motion,
            "last_motion_at": state.get("last_motion_at"),
            "last_person": state.get("last_person"),
            "temperature_c": temp,
            "humidity": humidity,
            "gas_alarm": bool(state.get("gas_alarm", False)),
            "fan_on": bool(state.get("fan_on", False)),
            "light_on": bool(state.get("light_on", False)),
            "recent_activity": state.get("recent_activity", [])[:10],
            "sensor_error": sensor_error,
            "gpio_error": pir_error,
            "features": [
                "Face-recognition door unlock",
                "PIR motion detection",
                "Live home temperature and humidity",
                "Gas leak alert status",
                "Fan and light controls",
            ],
        }
    )


@app.route("/api/control/<name>", methods=["POST"])
def control_device(name):
    data = request.get_json(silent=True) or {}
    desired = bool(data.get("state", False))

    if name == "fan":
        if fan is not None:
            fan.value = desired
        set_output("fan", desired)
    elif name == "light":
        if light is not None:
            light.value = desired
        set_output("light", desired)
    elif name == "gas_alarm":
        set_gas_alarm(desired)
        record_activity("alert", "Gas leak alarm toggled manually.")

    return jsonify({"ok": True, "name": name, "state": desired})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
