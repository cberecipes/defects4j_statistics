#!usr/bin/python
import sys

from RQ3_H1 import checked_coverage_better_indicator


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    checked_coverage_better_indicator.compute()


if __name__ == "__main__":
    main()