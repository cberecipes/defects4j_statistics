"""
========
Barchart
========

A bar plot with errorbars and height labels on individual bars
"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import csv
from itertools import islice

from matplotlib.patches import Rectangle

from util import get_project_root

results_folder = '/RQ3_H1/results'


def get_latest_csv_path():
    path = str(get_project_root()) + results_folder + '/*.csv'
    list_of_files = glob.glob(path)
    if len(list_of_files) <= 0:
        print("compute the solution first")
        exit(0)
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def autolabel(ax, rects, labels):
    """
    Attach a text label above each bar displaying its height
    """
    idx = 0
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height, labels[idx], ha='center', va='bottom')
        idx = idx + 1


def visualize_by_project_id(start, end):
    with open(get_latest_csv_path()) as csv_file:
        n = [int(start), int(end)]
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        sorted_list = sorted(reader, key=lambda c_row: int(c_row['project_id']), reverse=False)
        ratio_statement_coverage = []
        ratio_checked_coverage = []
        project_ids = []
        checked_coverage_label = []
        statement_coverage_label = []
        project_name = ','.join(set([s['project'] for s in sorted_list]))

        for row in islice(sorted_list, n[0], n[1]):
            ratio_checked_coverage.append(float(row['ratio_checked_coverage']))
            ratio_statement_coverage.append(float(row['ratio_statement_coverage']))
            project_ids.append(int(row['project_id']))
            statement_coverage_label.append(row['len_of_bug_detecting_tests'] + '/' +
                                            row['len_of_statement_covering_tests'])
            checked_coverage_label.append(row['len_of_bug_detecting_tests'] + '/' +
                                          row['len_of_checked_covering_tests'])

        ind = np.arange(len(range(n[0], n[1])))
        width = 0.35
        fig, ax = plt.subplots()

        # rects1 = ax.bar(ind, ratio_checked_coverage, width, color='r')
        # rects2 = ax.bar(ind + width, ratio_statement_coverage, width, color='y')

        checked_coverage_bars = ax.bar(ind - width / 2, ratio_checked_coverage, width)
        statement_coverage_bars = ax.bar(ind + width / 2, ratio_statement_coverage, width)

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Ratio')
        ax.set_xlabel('Project bug Id')
        ax.set_title('Ratio between bug detecting and covering tests for project: ' + project_name)
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(tuple(project_ids))
        formula_legend = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

        ax.legend((formula_legend, checked_coverage_bars[0], statement_coverage_bars[0]),
                  ('Ratio = No. of bug detecting tests / No. of Covering tests',
                   'Checked Coverage',
                   'Statement Coverage'))

        autolabel(ax, checked_coverage_bars, checked_coverage_label)
        autolabel(ax, statement_coverage_bars, statement_coverage_label)

        fig.set_size_inches(15, 5)
        # save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_' +
        # str(max(project_ids))
        save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save)
        fig.savefig(save_path, dpi=100)
        plt.show()


def visualize_whole_project():
    with open(get_latest_csv_path()) as csv_file:
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        sum_len_of_bug_detecting_tests = 0
        sum_len_of_statement_covering_tests = 0
        sum_len_of_checked_covering_tests = 0
        project_name = set()
        for row in reader:
            sum_len_of_bug_detecting_tests = sum_len_of_bug_detecting_tests + \
                int(row['len_of_bug_detecting_tests'])
            sum_len_of_statement_covering_tests = sum_len_of_statement_covering_tests + \
                int(row['len_of_statement_covering_tests'])
            sum_len_of_checked_covering_tests = sum_len_of_checked_covering_tests + \
                int(row['len_of_checked_covering_tests'])

            project_name.add(row['project'])

        sum_checked_coverage = sum_len_of_bug_detecting_tests / sum_len_of_checked_covering_tests
        checked_coverage_label = [str(sum_len_of_bug_detecting_tests) + '/' + str(sum_len_of_checked_covering_tests)]
        sum_statement_coverage = sum_len_of_bug_detecting_tests / sum_len_of_statement_covering_tests
        statement_coverage_label = [str(sum_len_of_bug_detecting_tests) + '/' + str(sum_len_of_statement_covering_tests)]

        project_name = ','.join([s for s in project_name])
        ind = np.arange(1)
        width = 0.35
        fig, ax = plt.subplots()

        checked_coverage_bars = ax.bar(ind - width / 2, sum_checked_coverage, width)
        statement_coverage_bars = ax.bar(ind + width / 2, sum_statement_coverage, width)

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Ratio')
        ax.set_xlabel('Project: ' + project_name)
        ax.set_title('Overall result: \n Ratio between bug detecting and covering tests for project: ' + project_name)
        ax.set_xticks(tuple())
        ax.set_xticklabels(tuple(''))

        formula_legend = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

        ax.legend((formula_legend, checked_coverage_bars[0], statement_coverage_bars[0]),
                  ('Ratio = No. of bug detecting tests / \nNo. of Covering tests',
                   'Checked Coverage',
                   'Statement Coverage'))

        autolabel(ax, checked_coverage_bars, checked_coverage_label)
        autolabel(ax, statement_coverage_bars, statement_coverage_label)


        # save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_' +
        # str(max(project_ids))
        save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_whole_result'
        fig.savefig(save_path, dpi=100)
        plt.show()


visualize_by_project_id(0, 20)
visualize_whole_project()


