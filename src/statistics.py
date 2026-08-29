"""
Statistical helper functions.
"""

from pathlib import Path

import pandas as pd


def save_result(
    analysis: str,
    value: float,
    output_file: Path,
) -> None:
    """
    Save one analysis result as a CSV file.
    """

    df = pd.DataFrame(
        {
            "Analysis": [analysis],
            "Value": [value],
        }
    )

    df.to_csv(
        output_file,
        index=False,
    )