import numpy as np


def ClassI(crates, vehicles, persons):
    w_crates = crates * 4500 * 9.80655
    w_vehicles = vehicles * 2962 * 9.80655
    w_persons = persons * 100 * 9.80655
    w_payload = w_crates + w_vehicles + w_persons

