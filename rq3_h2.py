#!usr/bin/python
import sys

from RQ3_H2 import correlation_checked_fault


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    correlation_checked_fault.compute()


if __name__ == "__main__":
    main()
