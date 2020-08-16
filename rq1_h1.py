#!usr/bin/python
import sys

from RQ1_H1 import full_coverage_score


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    full_coverage_score.compute()


if __name__ == "__main__":
    main()
