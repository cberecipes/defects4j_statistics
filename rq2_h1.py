#!usr/bin/python
import sys

from RQ2_H1 import compute_score_increase


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    compute_score_increase.compute()


if __name__ == "__main__":
    main()
