import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import csv

from scipy.interpolate import interp1d

from util import get_project_root

results_folder = '/RQ3_H2/results'


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


def visualize_whole_project():
    with open(get_latest_csv_path()) as csv_file:
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        statement_coverage = []
        checked_coverage = []
        percent_coverage = []
        project_name = set()
        for row in reader:
            statement_coverage.append(float(row['statement_coverage']))
            checked_coverage.append(float(row['checked_coverage']))
            percent_coverage.append(int(row['percent_coverage']))
            project_name.add(row['project'])

    percent_coverage = np.array(percent_coverage)
    checked_coverage = np.array(checked_coverage)

    percent_coverage_smooth = np.linspace(min(percent_coverage), max(percent_coverage), 500)
    f = interp1d(percent_coverage, checked_coverage, kind='quadratic')
    checked_coverage_smooth = f(percent_coverage_smooth)

    f1 = interp1d(percent_coverage, statement_coverage, kind='quadratic')
    statement_coverage_smooth = f1(percent_coverage_smooth)

    project_name = ','.join([s for s in project_name])
    save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_whole_result'
    fig = plt.gcf()
    fig.set_size_inches(15, 5)

    plt.plot(percent_coverage_smooth, checked_coverage_smooth, label="checked coverage")
    plt.plot(percent_coverage_smooth, statement_coverage_smooth, label="statement coverage")
    plt.xlabel('coverage score in percentage for project: ' + project_name)
    plt.ylabel('correlation (rpb) value')
    plt.title('Point Biserial correlation for statement and checked coverage')
    plt.legend()
    plt.show()
    fig.savefig(save_path, dpi=100)


# visualize_whole_project()

def visualize_as_scatter_plot():
    with open(get_latest_csv_path()) as csv_file:
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        statement_coverage = []
        checked_coverage = []
        percent_coverage = []
        project_name = set()
        for row in reader:
            statement_coverage.append(int(1 if row['statement_coverage'] == "True" else 0))
            checked_coverage.append(int(1 if row['checked_coverage'] == "True" else 0))
            percent_coverage.append(int(row['percent_coverage']))

            project_name.add(row['project'])

    plt.scatter(checked_coverage, percent_coverage)
    plt.show()


# visualize_as_scatter_plot()


def visualize_as_bar_plot():
    with open(get_latest_csv_path()) as csv_file:
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        statement_coverage = []
        checked_coverage = []
        percent_coverage = []
        counts_statement = {}
        counts_checked = {}
        counts_statement_f = {}
        counts_checked_f = {}
        project_name = set()
        for row in reader:
            statement_coverage.append(int(1 if row['statement_coverage'] == "True" else 0))
            checked_coverage.append(int(1 if row['checked_coverage'] == "True" else 0))
            percent_coverage.append(int(row['percent_coverage_s']))
            project_name.add(row['project'])

            try:
                counts_statement[int(row['percent_coverage_s'])] = counts_statement[int(row['percent_coverage_s'])] + \
                    int(1 if row['statement_coverage'] == "True" else 0)
            except KeyError:
                counts_statement[int(row['percent_coverage_s'])] = int(1 if row['statement_coverage'] == "True" else 0)

            try:
                counts_checked[int(row['percent_coverage_c'])] = counts_checked[int(row['percent_coverage_c'])] + \
                    int(1 if row['checked_coverage'] == "True" else 0)
            except KeyError:
                counts_checked[int(row['percent_coverage_c'])] = int(1 if row['checked_coverage'] == "True" else 0)
            except ValueError:
                pass

            try:
                counts_statement_f[int(row['percent_coverage_s'])] = counts_statement_f[int(row['percent_coverage_s'])]\
                                                                     + int(1)
            except KeyError:
                counts_statement_f[int(row['percent_coverage_s'])] = int(1)

            try:
                counts_checked_f[int(row['percent_coverage_c'])] = counts_checked_f[int(row['percent_coverage_c'])] \
                                                                   + int(1)
            except KeyError:
                counts_checked_f[int(row['percent_coverage_c'])] = int(1)
            except ValueError:
                pass

    label = [item for item, _ in sorted(counts_statement.items())]
    statement_bar_heights = [item / counts_statement_f[_] for _, item in sorted(counts_statement.items())]
    checked_bar_heights = [item / counts_checked_f[_] for _, item in sorted(counts_checked.items())]

    statement_bar_heights_label = [str(item) + '/' + str(counts_statement_f[_])
                                   for _, item in sorted(counts_statement.items())]
    checked_bar_heights_label = [str(item) + '/' + str(counts_checked_f[_])
                                 for _, item in sorted(counts_checked.items())]

    project_name = ','.join([s for s in project_name])
    ind = np.arange(len(label))
    width = 0.35
    fig, ax = plt.subplots()

    checked_coverage_bars = ax.bar(ind - width / 2, checked_bar_heights, width)
    statement_coverage_bars = ax.bar(ind + width / 2, statement_bar_heights, width)

    ax.set_ylabel('Ratio')
    ax.set_xlabel('% coverage score')
    ax.set_title('Ratio of Total No. of test suites to test suite includes bug detecting tests: Lang')
    ax.set_xticks(ind - width / 2)
    ax.set_xticklabels(tuple(label))

    ax.legend((checked_coverage_bars[0], statement_coverage_bars[0]), ('Checked Coverage', 'Statement Coverage'))

#    ax.legend((checked_coverage_bars[0]), ('Checked Coverage'))

    autolabel(ax, checked_coverage_bars, checked_bar_heights_label)
    autolabel(ax, statement_coverage_bars, statement_bar_heights_label)

    fig.set_size_inches(15, 5)
    # save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_' +
    # str(max(project_ids))
    save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save)
    fig.savefig(save_path, dpi=100)
    plt.show()


visualize_as_bar_plot()


def visualize_as_box_plot():
    with open(get_latest_csv_path()) as csv_file:
        file_name_to_save = os.path.basename(csv_file.name).split(".")[0]
        reader = csv.DictReader(csv_file, delimiter=',')
        statement_coverage_t = []
        statement_coverage_f = []
        checked_coverage_t = []
        checked_coverage_f = []
        project_name = set()
        for row in reader:
            if row['statement_coverage'] == "True":
                statement_coverage_t.append(int(row['percent_coverage_s']))
            if row['checked_coverage'] == "True":
                checked_coverage_t.append(int(row['percent_coverage_c']))

            if row['statement_coverage'] == "False":
                statement_coverage_f.append(int(row['percent_coverage_s']))
            if row['checked_coverage'] == "False":
                checked_coverage_f.append(int(row['percent_coverage_c']))

            project_name.add(row['project'])

        project_name = ','.join([s for s in project_name])

        data_to_plot = [checked_coverage_f, checked_coverage_t, statement_coverage_f, statement_coverage_t]
        print(len(checked_coverage_f), len(checked_coverage_t), len(statement_coverage_f), len(statement_coverage_t))
        fig = plt.figure(1, figsize=(9, 6))

        # Create an axes instance
        ax = fig.add_subplot(111)

        ax.set_ylabel('No. of tests with % coverage score')
        ax.set_xlabel('Indicates whether or not, a bug detecting test is included in generated test suite')
        ax.set_title('Box-plot showing higher coverage improves fault detecting rate for project: Lang')
        # ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(tuple(['False', 'True', 'False', 'True']))

        # Create the boxplot
        bp = ax.boxplot(data_to_plot)
        bp['medians'][0].set(color='#4070A0', linewidth=2)
        bp['medians'][1].set(color='#4070A0', linewidth=2)

        bp['medians'][2].set(color='orange', linewidth=2)
        bp['medians'][3].set(color='orange', linewidth=2)

        ax.legend((bp['medians'][0], bp['medians'][2]), ('Checked Coverage', 'Statement Coverage'))

        plt.show()
        save_path = str(get_project_root()) + results_folder + '/' + str(file_name_to_save) + '_box-plot'
        fig.savefig(save_path, dpi=100)


visualize_as_box_plot()

