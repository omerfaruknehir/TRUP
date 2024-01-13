import sys
if sys.platform.startswith("linux"):
    from infrastructure.linux.status_detector import shutdown_event
elif sys.platform == "win32":
    from infrastructure.windows.status_detector import shutdown_event