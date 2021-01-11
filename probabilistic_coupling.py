#!usr/bin/python
import sys

from Probabilistic_coupling import adequacy_based_testsuite_creation_v4 as adequacy_based_testsuite_creation
from Probabilistic_coupling import max_prob_coupling


def main():
    arguments = len(sys.argv) - 0
    if arguments != 1:
        print("please verify arguments, size mismatch")
        sys.exit(2)
    adequacy_based_testsuite_creation.compute()
    max_prob_coupling.compute()


if __name__ == "__main__":
    main()
