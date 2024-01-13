import ctypes

_event_funcs = []

def shutdown_event(func):
    _event_funcs.append(func)
    return func

def _shutdown_handler(ctrl_type):
    if ctrl_type == 0:
        print("Received Ctrl+C, shutting down...")
    elif ctrl_type == 2:
        print("Received system shutdown, shutting down...")
    
    for i in _event_funcs:
        i(ctrl_type)
    return True

kernel32 = ctypes.windll.kernel32
handler = kernel32.SetConsoleCtrlHandler(_shutdown_handler, 1)