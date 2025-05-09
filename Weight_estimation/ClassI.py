import numpy as np


def ClassI(crates, vehicles, persons, R, ld_cr, eff_p, cp):
    w_crates = crates * 4500 * 9.80655
    w_vehicles = vehicles * 2962 * 9.80655
    w_persons = persons * 100 * 9.80655
    w_payload = w_crates + w_vehicles + w_persons
    w_crew = 2 * 100 * 9.80655
    Mtfo = 0.005
    a = 0.5482
    b = 486.68

    ff1 = .990
    ff2 = .990
    ff3 = .995
    ff4 = .980
    ff7 = .990
    ff8 = .992
    ff5 = 1 / np.exp(R / eff_p * cp * 9.80655 / ld_cr)
    Mff = ff1 * ff2 * ff3 * ff4 * ff5 * ff7 * ff8

    W_TO = (b + w_crew + w_payload) / (Mff - a - Mtfo)
    W_OE = a * W_TO + b + W_TO * Mtfo + w_crew

    return W_OE/9.80655, W_TO/9.80655, (1-Mff)*W_TO/9.80655


if __name__ == '__main__':
    oew = ClassI(1, 2, 9, 4000000, 15, 0.82, 90e-9)
    print(oew, 70307*9.81)

