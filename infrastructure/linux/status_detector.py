import signal
import sys
from inspect import signature
from types import FrameType
import traceback

_event_funcs = []

def shutdown_event(func):
    if len(signature(func).parameters) != 1:
        raise ValueError("shutdown_event must be take an argument `signal`")
    _event_funcs.append(func)
    return func

def _shutdown_handler(signum, frame: FrameType):
    global _event_funcs
    event_funcs = _event_funcs
    if len(_event_funcs) == 0:
        return
    _event_funcs = []
    print(f"\nReceived signal {signum}, shutting server down. Current thread:")
    print(''.join(traceback.format_list(traceback.extract_stack(frame))).removesuffix('\n'))
    for i in event_funcs:
        i(signum)
    sys.exit(0)

# Register the shutdown handler
handler_term = signal.signal(signal.SIGTERM, _shutdown_handler)
handler_int  = signal.signal(signal.SIGINT, _shutdown_handler)