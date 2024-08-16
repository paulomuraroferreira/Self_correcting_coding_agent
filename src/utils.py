from dataclasses import dataclass
from pathlib import Path

current_file_dir = Path(__file__).parent

@dataclass
class PathInfo:
    CSV_PATH:str = str(current_file_dir.parent / "data" )
    DATA_FOLDER_PATH:str = str(current_file_dir.parent / "data" )
    ENV_FILE_PATH:str = str(current_file_dir.parent / '.env')


import uuid 

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print(f"Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)