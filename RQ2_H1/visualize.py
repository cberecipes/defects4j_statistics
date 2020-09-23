import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import csv
from itertools import islice

from RQ2_H1.format_as_csv import compute_percent_increase
from util import get_project_root, read_config

results_folder = '/RQ2_H1/results'
project_config = read_config(['../project_details.properties'])


def get_configured_csv_path():
    project_list = project_config.get('projects', 'project_list').split(",")

    if len(project_list) > 1:
        print("reduce number of projects to 1")
        exit(0)
    project_list = project_list[0]
    return str(get_project_root()) + results_folder + '/' + project_list + '.csv'


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
        statement_coverage_increase = []
        checked_coverage_increase = []
        mutation_coverage_increase = []
        project_ids = []

        project_name = ','.join(set([s['project'] for s in sorted_list]))

        for row in islice(sorted_list, n[0], n[1]):
            checked_coverage_increase.append(float(row['checked_coverage_increase']))
            statement_coverage_increase.append(float(row['statement_coverage_increase']))
            mutation_coverage_increase.append(float(row['mutation_coverage_increase']))

            project_ids.append(int(row['project_id']))

        ind = np.arange(len(range(n[0], n[1])))
        width = 0.35
        fig, ax = plt.subplots()

        # rects1 = ax.bar(ind, ratio_checked_coverage, width, color='r')
        # rects2 = ax.bar(ind + width, ratio_statement_coverage, width, color='y')

        checked_coverage_bars = ax.bar(ind - width / 2, checked_coverage_increase, width)
        statement_coverage_bars = ax.bar(ind + width / 2, statement_coverage_increase, width)
        mutation_coverage_bars = ax.bar(ind + width * 3 / 2, mutation_coverage_increase, width)

        # add some text for labels, title and axes ticks
        ax.set_ylabel('% increase in coverage score')
        ax.set_xlabel('Project bug Id')
        ax.set_title('% of coverage increase for statement and checked coverage for project : ' + project_name)
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(tuple(project_ids))
        # formula_legend = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

        ax.legend((checked_coverage_bars[0], statement_coverage_bars[0], mutation_coverage_bars[0]),
                  ('Checked Coverage', 'Statement Coverage', 'Mutation Coverage'))

        # autolabel(ax, checked_coverage_bars)
        # autolabel(ax, statement_coverage_bars)

        fig.set_size_inches(15, 5)
        # save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_' +
        # str(max(project_ids))
        save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save)
        fig.savefig(save_path, dpi=100)
        plt.show()


def visualize_whole_project():
    with open(get_configured_csv_path()) as csv_file:
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        sum_checked_buggy = 0
        sum_checked_fixed = 0
        sum_coverage_buggy = 0
        sum_coverage_fixed = 0
        sum_mutation_buggy = 0
        sum_mutation_fixed = 0
        project_name = set()
        for row in reader:
            sum_checked_buggy = sum_checked_buggy + float(row['checked_buggy'])
            sum_checked_fixed = sum_checked_fixed + float(row['checked_fixed'])

            sum_coverage_buggy = sum_coverage_buggy + float(row['statement_buggy'])
            sum_coverage_fixed = sum_coverage_fixed + float(row['statement_fixed'])

            sum_mutation_buggy = sum_mutation_buggy + float(row['mutation_buggy'])
            sum_mutation_fixed = sum_mutation_fixed + float(row['mutation_fixed'])

            project_name.add(row['project'])

        checked_coverage_increase_per = compute_percent_increase(sum_checked_buggy, sum_checked_fixed)
        statement_coverage_increase_per = compute_percent_increase(sum_coverage_buggy, sum_coverage_fixed)
        mutation_coverage_increase_per = compute_percent_increase(sum_mutation_buggy, sum_mutation_fixed)

        checked_coverage_increase = [sum_checked_buggy, sum_checked_fixed]
        statement_coverage_increase = [sum_coverage_buggy, sum_coverage_fixed]
        mutation_coverage_increase = [sum_mutation_buggy, sum_mutation_fixed]

        checked_coverage_label = ['', 'inc:' + str(round(checked_coverage_increase_per, 3))]
        statement_coverage_label = ['', 'inc: ' + str(round(statement_coverage_increase_per, 3))]
        mutation_coverage_label = ['', 'inc: ' + str(round(mutation_coverage_increase_per, 3))]

        project_name = ','.join([s for s in project_name])
        ind = np.arange(2)
        width = 0.3
        fig, ax = plt.subplots()

        checked_coverage_bars = ax.bar(ind - width / 2, checked_coverage_increase, width)
        statement_coverage_bars = ax.bar(ind + width / 2, statement_coverage_increase, width)
        mutation_coverage_bars = ax.bar(ind + width * 3 / 2, mutation_coverage_increase, width)

        # ax.set_ylabel('sum of coverage score of all projects')
        ax.set_xlabel(project_name)
        # ax.set_title('Overall result: coverage increase of bug detecting tests')
        ax.set_xticks(tuple(ind + width / 120))
        ax.set_xticklabels(tuple(['buggy version', 'fixed version']))

        # formula_legend = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

        # ax.legend((checked_coverage_bars[0], statement_coverage_bars[0], mutation_coverage_bars[0]),
        #           ('Checked Coverage', 'Statement Coverage', 'Mutation Coverage'), loc='lower left')

        ax.legend().remove()
        autolabel(ax, checked_coverage_bars, checked_coverage_label)
        autolabel(ax, statement_coverage_bars, statement_coverage_label)
        autolabel(ax, mutation_coverage_bars, mutation_coverage_label)


        # save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_' +
        # str(max(project_ids))
        save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_whole_result'
        fig.savefig(save_path, dpi=100)
        plt.show()


# visualize_by_project_id(0, 1)
# visualize_whole_project()

def visualize_as_box_plot():
    font = {'size': 18}

    plt.rc('font', **font)
    project_list = project_config.get('projects', 'project_list').split(",")

    if len(project_list) > 1:
        print("reduce number of projects to 1")
        exit(0)
    project_list = project_list[0]

    statement_increase = []
    checked_increase = []
    mutation_increase = []

    file_name = "/" + project_list + ".csv"
    path = str(get_project_root()) + results_folder + file_name

    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')

        for row in reader:
            statement_increase.append(float(row['statement_coverage_increase']))
            checked_increase.append(float(row['checked_coverage_increase'])
                                    if float(row['checked_coverage_increase']) > 0 else 0)
            mutation_increase.append(float(row['mutation_coverage_increase'])
                                     if float(row['mutation_coverage_increase']) > 0 else 0)

    data_to_plot = [statement_increase, checked_increase, mutation_increase]
    fig = plt.figure(1, figsize=(9, 6))

    ax = fig.add_subplot(111)

    ax.set_ylabel('% coverage score increase')
    # ax.set_xlabel('Indicates whether or not, a bug detecting test is included in generated test suite')
    ax.set_title(project_list)
    # ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(tuple(['Statement coverage', 'Checked coverage', 'Mutation score']))

    bp = ax.boxplot(data_to_plot)
    bp['medians'][0].set(color='#3d85c6', linewidth=2)
    bp['medians'][1].set(color='#e69138', linewidth=2)
    bp['medians'][2].set(color='#6aa84f', linewidth=2)

    ax.legend().remove()
    plt.show()
    save_path = str(get_project_root()) + results_folder + '/' + str(project_list) + '_box-plot'
    fig.savefig(save_path, dpi=100)


visualize_as_box_plot()


