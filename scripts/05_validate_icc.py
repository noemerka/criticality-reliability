"""
Validate our ICC implementation against pingouin.
"""

import pandas as pd
import pingouin as pg

from src.io import load_dataset
from src.icc import compute_icc21


def main():

    test_data, retest_data, _ = load_dataset()

    vertex = 0

    test = test_data[:, vertex]
    retest = retest_data[:, vertex]

    # Our implementation
    my_icc = compute_icc21(test, retest)

    # Build dataframe for pingouin
    df = pd.DataFrame(
        {
            "subject": list(range(len(test))) * 2,
            "session": ["test"] * len(test) + ["retest"] * len(test),
            "value": list(test) + list(retest),
        }
    )

    icc_table = pg.intraclass_corr(
        data=df,
        targets="subject",
        raters="session",
        ratings="value",
    )

    print("\nOur ICC:")
    print(my_icc)

    print("\nPingouin ICC table:")
    print(icc_table)


if __name__ == "__main__":
    main()