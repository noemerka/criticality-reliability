"""
Test the ICC function on one cortical vertex.
"""

from src.io import load_dataset
from src.icc import compute_icc21


def main():

    # Load dataset
    test_data, retest_data, _ = load_dataset()

    # Test only one vertex
    vertex = 0

    icc = compute_icc21(
        test_data[:, vertex],
        retest_data[:, vertex],
    )

    print()
    print(f"ICC = {icc:.6f}")


if __name__ == "__main__":
    main()
    