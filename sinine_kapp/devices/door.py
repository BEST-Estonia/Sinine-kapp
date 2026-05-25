"""Door sensor and door actuator helpers."""

import logging

import RPi.GPIO as GPIO


# ---------------------------------------------------------------------------
# GPIO configuration
# ---------------------------------------------------------------------------

DOOR_SENSOR_PIN = 21
_gpio_initialized = False


def open_door():
    """Open/unlock the cabinet door.

    This is currently a placeholder. The controller calls it at the start of a
    drink session, so this is the seam for adding relay/lock hardware later.
    """
    return 0


def init_sensor():
    """Initialize the door sensor input with an internal pull-up."""
    global _gpio_initialized
    try:
        if not _gpio_initialized:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            _gpio_initialized = True
        logging.info("Door sensor initialized successfully on GPIO %s", DOOR_SENSOR_PIN)
    except Exception as exc:
        logging.error(
            "CRITICAL: Failed to initialize door sensor on GPIO %s: %s",
            DOOR_SENSOR_PIN,
            exc,
        )
        _gpio_initialized = False


def is_open() -> bool:
    """Return True when the door sensor reports open."""
    if not _gpio_initialized:
        logging.error("CRITICAL: Door sensor not initialized - returning False (door closed)")
        return False

    try:
        door_state = GPIO.input(DOOR_SENSOR_PIN)
        return door_state != GPIO.LOW
    except Exception as exc:
        logging.error("Error reading door sensor: %s", exc)
        return False


def cleanup():
    """Release GPIO resources owned by this process."""
    global _gpio_initialized

    try:
        GPIO.cleanup()
    except Exception as exc:
        logging.warning("GPIO cleanup failed: %s", exc)
    finally:
        _gpio_initialized = False
