# state_manager.py

state = {
    "phase": "idle",
    "start_decharge": None,
    "end_decharge": None,
    "start_charge": None,
    "end_charge": None,
    "cycle_count": 0,
    "minicycle_count": 0,
    "cycle_start_time": None,
    "init_phase": True,
    "init_loaded_groups": 0,
    "mover_number_map": {
        "current": [1, 2, 3, 4],
        "waiting_next": [5, 6, 7, 8],
        "after_next": [9, 10, 11, 12]
    }
}

def reset_cycle_state():
    state["phase"] = "idle"
    state["start_decharge"] = None
    state["end_decharge"] = None
    state["start_charge"] = None
    state["end_charge"] = None
    state["cycle_count"] = 0
    state["minicycle_count"] = 0
    state["cycle_start_time"] = None
    state["init_phase"] = True
    state["init_loaded_groups"] = 0
    state["mover_number_map"] = {
        "current": [1, 2, 3, 4],
        "waiting_next": [5, 6, 7, 8],
        "after_next": [9, 10, 11, 12]
    }
