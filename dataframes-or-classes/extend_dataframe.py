import dataclasses
from typing import Dict

import pandas as pd
import numpy as np


@dataclasses.dataclass
class LpVariable:
    """Stand-in for pulp class."""
    x: float
    y: int


class BatteryOptDataFrame(pd.DataFrame):
    """Extends pd.DataFrame for problem related to battery placement optimization."""

    def __init__(self, *args, **kwargs):
        super(BatteryOptDataFrame, self).__init__(*args, **kwargs)

        if (self.dtypes != self.expected_dtypes).all():
            raise ValueError(
                f"expected:\n{self.expected_dtypes}\nactual:\n{self.dtypes}"
            )
        self["identifier"] = (
            self["bus"]
            .str.cat(self["voltage"].astype(str), sep=";")
            .str.cat(self["connectors"].astype(str), sep=";")
        )

    @property
    def _constructor(self):
        return BatteryOptDataFrame

    @property
    def expected_dtypes(self) -> Dict[str, np.dtype]:
        return pd.Series({
            "bus": np.dtype("O"),
            "voltage": np.dtype("float64"),
            "connectors": np.dtype("int64"),
        })

    def generate_pulp_variables(self) -> Dict[str, LpVariable]:
        return {
            r.identifier: LpVariable(r.voltage, r.connectors)
            for r in self.itertuples()
        }

