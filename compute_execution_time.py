#!usr/bin/python
import sys
from compute_execution_time import execution_time


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    execution_time.compute()


if __name__ == "__main__":
    main()
