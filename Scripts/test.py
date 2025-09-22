import wmi

def get_monitor_manufacturers():
    c = wmi.WMI()
    obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)
    for monitor in obj:
        print(f"Fabricant: {monitor.MonitorManufacturer}")
        print(f"Type: {monitor.MonitorType}")

if __name__ == "__main__":
    get_monitor_manufacturers()