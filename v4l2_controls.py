import subprocess

def set_control(ctrl_name, value, device="/dev/video0"):
    """
    Generic function to set a V4L2 control.
    """
    subprocess.run(
        ["v4l2-ctl", "-d", device, "--set-ctrl", f"{ctrl_name}={value}"],
        check=True
    )
    print(f"{ctrl_name} set to {value}")

def power_line_freq(value, device="/dev/video0"):
    """
    Set power_line_frequency control.
    0 = Disabled, 1 = 50Hz, 2 = 60Hz
    """
    if value not in [0, 1, 2]:
        raise ValueError("power_line_frequency must be 0 (Disabled), 1 (50Hz), or 2 (60Hz)")
    set_control("power_line_frequency", value, device)

def brightness(value, device="/dev/video0"):
    """
    Set brightness (0-255)
    """
    if not 0 <= value <= 255:
        raise ValueError("brightness must be between 0 and 255")
    set_control("brightness", value, device)

def contrast(value, device="/dev/video0"):
    """
    Set contrast (0-255)
    """
    if not 0 <= value <= 255:
        raise ValueError("contrast must be between 0 and 255")
    set_control("contrast", value, device)

def sharpness(value, device="/dev/video0"):
    """
    Set sharpness (0-3)
    """
    if not 0 <= value <= 3:
        raise ValueError("sharpness must be between 0 and 3")
    set_control("sharpness", value, device)
