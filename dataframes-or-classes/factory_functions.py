import dataclasses
import functools
from pprint import pprint
from typing import Dict, List

import pandas as pd
import numpy as np


@dataclasses.dataclass
class LpVariable:
    """Stand-in for pulp class."""
    x: float
    y: int


@functools.singledispatch
def create_battery_dataframe(
    bus: List[str],
    voltage: List[float],
    connectors: List[int],
) -> pd.DataFrame:

    battery = pd.DataFrame(
        {
            "bus": pd.Series(bus, dtype=np.dtype("O")),
            "voltage": pd.Series(voltage, dtype=np.dtype("float64")),
            "connectors": pd.Series(connectors, dtype=np.dtype("int64")),
        }
    )
    battery["identifier"] = (
        battery["bus"]
        .str.cat(battery["voltage"].astype(str), sep=";")
        .str.cat(battery["connectors"].astype(str), sep=";")
    )
    return battery


@create_battery_dataframe.register
def _(bus: str, voltage: float, connectors: int) -> pd.DataFrame:
    return create_battery_dataframe([bus], [voltage], [connectors])


def generate_lp_variables(batteries: pd.DataFrame) -> Dict[str, LpVariable]:
    # relying on some amount of "duck-typing" for the schema of the 'batteries' DataFrame
    return {
        r.identifier: LpVariable(r.voltage, r.connectors)
        for r in batteries.itertuples()
    }


if __name__ == "__main__":
    bus = ["a", "b", "c"]
    voltage = [0.8, 1.5, 3.1]
    connectors = [1, 2, 5]

    batteries = create_battery_dataframe(bus, voltage, connectors)
    print(batteries)

    battery = create_battery_dataframe(bus[0], voltage[0], connectors[0])
    print(battery)

    lp_vars = generate_lp_variables(batteries)
    pprint(lp_vars)

