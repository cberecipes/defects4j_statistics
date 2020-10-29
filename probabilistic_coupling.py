#!usr/bin/python
import sys

from Probabilistic_coupling import adequacy_based_testsuite_creation


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    adequacy_based_testsuite_creation.compute()


if __name__ == "__main__":
    main()
