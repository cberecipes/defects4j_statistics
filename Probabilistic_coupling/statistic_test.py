from scipy.stats import pearsonr
import scipy.stats as ss
from bisect import bisect_left
from pandas import Categorical
import pandas as pd
import numpy as np
import itertools as it
import csv

from numpy import mean
from numpy import var
from math import sqrt

from util import get_project_root, read_config

results_folder = '/Probabilistic_coupling/results'
results_folder_max_pc_per_proj = results_folder + '/max_pc_per_proj'
project_config = read_config(['../project_details.properties'])


# calculate Pearson's correlation
def correlation(d1, d2):
    corr, _ = pearsonr(d1, d2)
    # print('Pearsons correlation: %.3f' % corr, _)
    print("correlation:\t{:.3f} \np-val: \t\t{:.5f}". format(corr, _))
    return corr


# https://gist.github.com/jacksonpradolima/f9b19d65b7f16603c837024d5f8c8a65
# https://machinelearningmastery.com/effect-size-measures-in-python/
# function to calculate Cohen's d for independent samples
def cohend(d1, d2):
    # calculate the size of samples
    n1, n2 = len(d1), len(d2)
    # calculate the variance of the samples
    s1, s2 = var(d1, ddof=1), var(d2, ddof=1)
    # calculate the pooled standard deviation
    s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    # calculate the means of the samples
    u1, u2 = mean(d1), mean(d2)
    # calculate the effect size
    return (u1 - u2) / s


# https://gist.github.com/jacksonpradolima/f9b19d65b7f16603c837024d5f8c8a65
def VD_A(treatment, control):
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000
    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/
    :param treatment: a numeric list
    :param control: another numeric list
    :returns the value estimate and the magnitude
    """
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data must have the same length")

    r = ss.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m) # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474] # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return "A12: \t\t" + str(estimate) + " \nmagnitude:\t" + magnitude


def VD_A_DF(data, val_col: str = None, group_col: str = None, sort=True):
    """
    :param data: pandas DataFrame object
    An array, any object exposing the array interface or a pandas DataFrame.
    Array must be two-dimensional. Second dimension may vary,
    i.e. groups may have different lengths.
    :param val_col: str, optional
    Must be specified if `a` is a pandas DataFrame object.
    Name of the column that contains values.
    :param group_col: str, optional
    Must be specified if `a` is a pandas DataFrame object.
    Name of the column that contains group names.
    :param sort : bool, optional
    Specifies whether to sort DataFrame by group_col or not. Recommended
    unless you sort your data manually.
    :return: stats : pandas DataFrame of effect sizes
    Stats summary ::
    'A' : Name of first measurement
    'B' : Name of second measurement
    'estimate' : effect sizes
    'magnitude' : magnitude
    """

    x = data.copy()
    if sort:
        x[group_col] = Categorical(x[group_col], categories=x[group_col].unique(), ordered=True)
        print(x)
        exit(0)
        x.sort_values(by=[group_col, val_col], ascending=True, inplace=True)

    groups = x[group_col].unique()

    # Pairwise combinations
    g1, g2 = np.array(list(it.combinations(np.arange(groups.size), 2))).T

    # Compute effect size for each combination
    ef = np.array([VD_A(list(x[val_col][x[group_col] == groups[i]].values),
    list(x[val_col][x[group_col] == groups[j]].values)) for i, j in zip(g1, g2)])

    return pd.DataFrame({
        'A': np.unique(data[group_col])[g1],
        'B': np.unique(data[group_col])[g2],
        'estimate': ef[:, 0],
        'magnitude': ef[:, 1]
    })


def read_big_file_and_compute_stats():
    file_name = "/max_pc" + ".csv"
    path = str(get_project_root()) + results_folder + file_name
    statement_increase = []
    checked_increase = []
    mutation_coverage = []

    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            statement_increase.append(float(row['statement_pc_max']))
            checked_increase.append(float(row['checked_pc_max']))

    correlation(checked_increase, statement_increase)
    print("cohend's d: {}".format(cohend(checked_increase, statement_increase)))
    print(VD_A(checked_increase, statement_increase))
    # df = pd.DataFrame({'a': checked_increase, 'b': statement_increase})
    # print(VD_A_DF(df))


read_big_file_and_compute_stats()


def read_file_and_visualise():
    project_list = project_config.get('projects', 'project_list').split(",")
    results_folder = str(get_project_root()) + results_folder_max_pc_per_proj
    for project in project_list:
        file_name = "/" + project + ".csv"
        path = results_folder + file_name
        statement_increase = []
        checked_increase = []
        mutation_coverage = []

        with open(path) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')

            for row in reader:
                statement_increase.append(float(row['statement_pc_max']))
                checked_increase.append(float(row['checked_pc_max']))

                # mutation_increase.append(float(row['mutation_coverage_increase'])
                #                          if float(row['mutation_coverage_increase']) > 0 else 0)

        if len(checked_increase) < 2:
            continue
        print(project + ":")
        correlation(checked_increase, statement_increase)
        print("cohend's d:\t{}".format(cohend(checked_increase, statement_increase)))
        print(VD_A(checked_increase, statement_increase))
        print("-"*80)


# read_file_and_visualise()
