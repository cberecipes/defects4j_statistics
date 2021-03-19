import statistics
from os import path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import csv
import seaborn as sns
from matplotlib import font_manager
from matplotlib.collections import PathCollection

from util import get_project_root, read_config

results_folder = '/Probabilistic_coupling/results'
results_folder_max_pc_per_proj = '/Probabilistic_coupling/results/max_pc_per_proj'
project_config = read_config(['../project_details.properties'])


def visualize_as_box_plot():
    font = {'size': 20}

    plt.rc('font', **font)
    project_list = project_config.get('projects', 'project_list').split(",")

    # if len(project_list) > 1:
    #     print("reduce number of projects to 1")
    #     exit(0)
    project_list = project_list[0]

    statement_coverage_r = []
    checked_coverage_r = []

    file_name = "/point_biserial_correlation__full" + ".csv"
    path = str(get_project_root()) + results_folder + file_name

    try:
        with open(path) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            for row in reader:
                statement_coverage_r.append(float(row['adequacy_based_tests_statement']))
                checked_coverage_r.append(float(row['adequacy_based_tests_checked']))
    except FileNotFoundError:
        pass

    data_to_plot = [statement_coverage_r, checked_coverage_r]
    fig = plt.figure(1, figsize=(9, 6))

    ax = fig.add_subplot()

    ax.set_ylabel('Probabilistic coupling')
    # ax.set_xlabel('Indicates whether or not, a bug detecting test is included in generated test suite')
    # ax.set_title(project_list)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(tuple(['Statement coverage', 'Checked coverage']))

    bp = ax.violinplot(data_to_plot, showmeans=True, showmedians=True)

    # loop over the paths of the mean lines
    xy = [[l.vertices[:, 0].mean(), l.vertices[0, 1]] for l in bp['cmeans'].get_paths()]
    xy = np.array(xy)

    ax.scatter(xy[:, 0], xy[:, 1], s=121, c="crimson", marker="x", zorder=3)

    # make lines invisible
    bp['cmeans'].set_visible(False)

    bp['bodies'][0].set(color='#e69138', linewidth=2)
    bp['bodies'][1].set(color='#3d85c6', linewidth=2)

    ax.legend().remove()
    plt.show()
    save_path = str(get_project_root()) + results_folder + '/' + str(project_list) + '_violin-plot'
    fig.savefig(save_path, dpi=100)


def visualize_as_violin_plot():
    font = {'size': 20}
    plt.rc('font', **font)

    statement_increase = []
    checked_increase = []
    mutation_increase = []

    file_name = "/max_pc" + ".csv"
    path = str(get_project_root()) + results_folder + file_name

    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')

        for row in reader:
            statement_increase.append(float(row['statement_pc_max']))
            checked_increase.append(float(row['checked_pc_max']))
            # mutation_increase.append(float(row['mutation_coverage_increase'])
            #                          if float(row['mutation_coverage_increase']) > 0 else 0)
    # statement_increase = list(filter(lambda num: num != 0, statement_increase))
    # checked_increase = list(filter(lambda num: num != 0, checked_increase))
    data_to_plot = [statement_increase, checked_increase]
    fig = plt.figure(1, figsize=(9, 6))

    ax = fig.add_subplot()

    ax.set_ylabel('Max PC')
    # ax.set_xlabel('Indicates whether or not, a bug detecting test is included in generated test suite')
    ax.set_title("Probabilistic Coupling")
    ax.set_xticks([1, 2, 3])
    if len(mutation_increase) > 0:
        ax.set_xticklabels(tuple(['Statement cov.', 'Checked cov.', 'Mutation score']))
    else:
        ax.set_xticklabels(tuple(['Statement coverage', 'Checked coverage']))

    bp = ax.violinplot(data_to_plot, showmeans=True, showmedians=True)

    # loop over the paths of the mean lines
    xy = [[l.vertices[:, 0].mean(), l.vertices[0, 1]] for l in bp['cmeans'].get_paths()]

    xy = np.array(xy)
    ax.scatter(xy[:, 0], xy[:, 1], s=121, c="crimson", marker="x", zorder=3)

    # make lines invisible
    bp['cmeans'].set_visible(False)

    bp['bodies'][0].set(color='#e69138', linewidth=2)
    bp['bodies'][1].set(color='#3d85c6', linewidth=2)

    ax.legend().remove()
    plt.show()
    save_path = str(get_project_root()) + results_folder + '/max_pc_violin-plot'
    fig.savefig(save_path, dpi=100)


# visualize_as_violin_plot()


def visualize_as_violin_plot_jitter(checked_increase, statement_increase, mutation_increase, save_path, title, y_label):
    font = {'size': 20}
    plt.rc('font', **font)

    means = []
    modes = []

    means.append(statistics.mean(statement_increase))
    means.append(statistics.mean(checked_increase))
    if len(mutation_increase) > 0:
        means.append(statistics.mean(mutation_increase))

    modes.append(statistics.median(statement_increase))
    modes.append(statistics.median(checked_increase))
    if len(mutation_increase) > 0:
        modes.append(statistics.median(mutation_increase))

    data_to_plot = [statement_increase, checked_increase]
    if len(mutation_increase) > 0:
        data_to_plot = [statement_increase, checked_increase, mutation_increase]

    fig = plt.figure(1, figsize=(9, 6))
    ax = sns.violinplot(data=data_to_plot, color=".8")
    sns.stripplot(data=data_to_plot, jitter=True, ax=ax)
    plt.setp(ax.collections, alpha=.3)
    scatter1 = ax.scatter(x=range(len(means)), y=means, s=121, c="crimson", marker="x", zorder=3)
    scatter2 = ax.scatter(x=range(len(modes)), y=modes,  s=121, c="crimson", zorder=3, marker=">")

    plt.legend((scatter1, scatter2),
               ('Mean', 'Median'),
               scatterpoints=1,
               loc='lower right',
               ncol=3,
               fontsize=15)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xticks([0, 1, 2])
    if len(mutation_increase) > 0:
        ax.set_xticklabels(tuple(['Statement cov.', 'Checked cov.', 'Mutation score']))
    else:
        ax.set_xticklabels(tuple(['Statement coverage', 'Checked coverage']))

    # ax.legend()
    plt.show()
    fig.savefig(save_path, dpi=100)


def visualize_as_boxplot_plot_jitter(checked_score, statement_score, mutation_score, save_path, title, y_label):
    font = {'size': 20}
    plt.rc('font', **font)

    means = []
    modes = []

    means.append(statistics.mean(statement_score))
    means.append(statistics.mean(checked_score))
    if len(mutation_score) > 0:
        means.append(statistics.mean(mutation_score))

    modes.append(statistics.median(statement_score))
    modes.append(statistics.median(checked_score))
    if len(mutation_score) > 0:
        modes.append(statistics.median(mutation_score))

    data_to_plot = [statement_score, checked_score]
    if len(mutation_score) > 0:
        data_to_plot = [statement_score, checked_score, mutation_score]
    fig = plt.figure(1, figsize=(9, 6))

    ax = fig.add_subplot(111)

    ax.set_ylabel(y_label)
    # ax.set_xlabel('Indicates whether or not, a bug detecting test is included in generated test suite')
    ax.set_title(title)
    # ax.set_xticks(ind + width / 2)
    if len(mutation_score) > 0:
        ax.set_xticklabels(tuple(['Statement cov.', 'Checked cov.', 'Mutation score']))
    else:
        ax.set_xticklabels(tuple(['Statement coverage', 'Checked coverage']))

    bp = ax.boxplot(data_to_plot)
    bp['medians'][0].set(color='#3d85c6', linewidth=2)
    bp['medians'][1].set(color='#e69138', linewidth=2)
    if len(mutation_score) > 0:
        bp['medians'][2].set(color='#6aa84f', linewidth=2)

    ax.legend().remove()
    plt.show()
    fig.savefig(save_path+"-boxplot", dpi=100)


def visualize_as_histogram(checked_score, statement_score, mutation_score, save_path, title, y_label):
    font = {'size': 20}
    plt.rc('font', **font)

    means = []
    modes = []

    means.append(statistics.mean(statement_score))
    means.append(statistics.mean(checked_score))
    if len(mutation_score) > 0:
        means.append(statistics.mean(mutation_score))

    modes.append(statistics.median(statement_score))
    modes.append(statistics.median(checked_score))
    if len(mutation_score) > 0:
        modes.append(statistics.median(mutation_score))

    data_to_plot = [statement_score, checked_score]
    if len(mutation_score) > 0:
        data_to_plot = [statement_score, checked_score, mutation_score]
    fig = plt.figure(1, figsize=(9, 6))

    ax = fig.add_subplot()

    ax.set_ylabel(y_label)
    ax.set_xlabel('PC score')
    # ax.set_xlabel('Indicates whether or not, a bug detecting test is included in generated test suite')
    ax.set_title(title)
    # ax.set_xticks(ind + width / 2)
    # if len(mutation_score) > 0:
    #     ax.set_xticklabels(tuple(['Statement cov.', 'Checked cov.', 'Mutation score']))
    # else:
    #     ax.set_xticklabels(tuple(['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']))

    bp = ax.hist(data_to_plot, bins=10, range=(0, 1.0), label=['statement coverage', 'checked coverage'])
    # bp['medians'][0].set(color='#3d85c6', linewidth=2)
    # bp['medians'][1].set(color='#e69138', linewidth=2)
    # if len(mutation_score) > 0:
    #     bp['medians'][2].set(color='#6aa84f', linewidth=2)

    ax.legend()
    plt.show()
    fig.savefig(save_path+"-histogram", dpi=100)


def plot_stacked_bar(data, series_labels, category_labels=None,
                     show_values=False, value_format="{}", y_label=None,
                     colors=None, grid=True, reverse=False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    category_labels -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_label         -- Label for y-axis (str)
    colors          -- List of color labels
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis=1)
        category_labels = reversed(category_labels)

    for i, row_data in enumerate(data):
        color = colors[i] if colors is not None else None
        axes.append(plt.bar(ind, row_data, bottom=cum_size,
                            label=series_labels[i], color=color))
        cum_size += row_data

    if category_labels:
        plt.xticks(ind, category_labels)

    if y_label:
        plt.ylabel(y_label)

    plt.legend()

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                plt.text(bar.get_x() + w/2, bar.get_y() + h/2, value_format.format(h), ha="center", va="center")


# def visualize_as_stackedbar(checked_score, statement_score, mutation_score, save_path, title, y_label):
def visualize_as_stackedbar(checked_score, statement_score, mutation_score, save_path, title, y_label):
    font = {'size': 20}
    plt.rc('font', **font)
    plt.figure(figsize=(6, 4))

    series_labels = ['Series 1', 'Series 2']

    zipped_lists = zip(checked_score, statement_score)
    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)
    checked_score, statement_score = [list(tuple) for tuple in tuples]

    data = [checked_score, statement_score]

    plot_stacked_bar(
        data,
        series_labels,
        value_format="{:.1f}",
        y_label="Quantity (units)"
    )

    plt.savefig('bar.png')
    plt.show()


def visualize_as_scatterplot(checked_score, statement_score, mutation_score, save_path, title, y_label):
    font = {'size': 20}
    plt.rc('font', **font)

    zipped_lists = zip(checked_score, statement_score)
    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)
    checked_score, statement_score = [list(tuple) for tuple in tuples]
    grades_range = range(0, len(checked_score))
    fig = plt.figure(1, figsize=(9, 6))
    ax = fig.add_subplot()

    ax.scatter(grades_range, checked_score, label='checked coverage')
    ax.scatter(grades_range, statement_score, label='statement coverage')
    ax.set_xlabel('Statements Range')
    ax.set_ylabel("PC score")
    ax.set_title(title)
    ax.legend()
    plt.savefig(save_path+"-scatter_plots")
    plt.show()


def visualize_as_scatterplot_skew(coverage_scores, save_path, title, y_label):
    font = {'size': 20}
    plt.rc('font', **font)
    legend_font = font_manager.FontProperties(style='normal', size=14)
    # for i in range(0, len(checked_score)):
    #     if statement_score[i] > checked_score[i]:
    #         print(str(statement_score[i]) + ", " + str(checked_score[i]))

    # sorted_pairs = sorted(coverage_scores)
    # print(sorted_pairs)
    # tuples = zip(*sorted_pairs)
    fig = plt.figure(1, figsize=(10, 7))
    ax = fig.add_subplot()
    green_x = mlines.Line2D([], [], color='black', marker='x', linestyle='None',
                              markersize=10, label='Modified statement')
    green_dot = mlines.Line2D([], [], color='green', marker='.', linestyle='None',
                                    markersize=10, label='assertion fail')
    red_dot = mlines.Line2D([], [], color='red', marker='.', linestyle='None',
                                    markersize=10, label='crashing test')
    orange_dot = mlines.Line2D([], [], color='orange', marker='.', linestyle='None',
                                    markersize=10, label='assertion and crashing test')

    for score_zip in coverage_scores:
        checked_score, statement_score, m, checked_nature, statement_nature, checked_modified, statement_modified = score_zip
        ax.scatter(checked_score, statement_score, label='statements', marker=checked_modified, c=checked_nature)

    ax.set_xlabel('Checked coverage PC')
    ax.set_ylabel('Statement coverage PC')
    ax.set_title(title + " - (checked PC)")
    ax.legend(handles=[green_x, green_dot, red_dot, orange_dot], prop=legend_font)
    plt.savefig(save_path+"-scatter_plot-single-checked")
    plt.show()

    fig = plt.figure(1, figsize=(10, 7))
    ax = fig.add_subplot()
    for score_zip in coverage_scores:
        checked_score, statement_score, m, checked_nature, statement_nature, checked_modified, statement_modified = score_zip
        ax.scatter(checked_score, statement_score, label='statements', marker=statement_modified, c=statement_nature)

    ax.set_xlabel('Checked coverage PC')
    ax.set_ylabel('Statement coverage PC')
    ax.set_title(title + " - (statement PC)")
    ax.legend(handles=[green_x, green_dot, red_dot, orange_dot], prop=legend_font)
    plt.savefig(save_path+"-scatter_plot-single-statement")
    plt.show()


def read_big_file_and_visualise():
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
            mutation_coverage.append(float(row['mutation_pc_max']))

            # mutation_increase.append(float(row['mutation_coverage_increase'])
            #                          if float(row['mutation_coverage_increase']) > 0 else 0)

    save_path = str(get_project_root()) + results_folder + '/max_pc_violin-plot'
    visualize_as_boxplot_plot_jitter(checked_increase, statement_increase, mutation_coverage, save_path,
                                     "Probabilistic Coupling: All Projects", "Max PC")


# read_big_file_and_visualise()


def read_file_and_visualise():
    project_list = project_config.get('projects', 'project_list').split(",")
    results_folder = str(get_project_root()) + results_folder_max_pc_per_proj
    for project in project_list:
        file_name = "/" + project + ".csv"
        csv_file_path = results_folder + file_name
        statement_increase = []
        checked_increase = []
        mutation_coverage = []

        with open(csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')

            for row in reader:
                statement_increase.append(float(row['statement_pc_max']))
                checked_increase.append(float(row['checked_pc_max']))

                # mutation_increase.append(float(row['mutation_coverage_increase'])
                #                          if float(row['mutation_coverage_increase']) > 0 else 0)

        save_path = results_folder + '/' + project
        visualize_as_stackedbar(checked_increase, statement_increase, mutation_coverage, save_path,
                                "Probabilistic Coupling: " + project, "Max PC")


# read_file_and_visualise()


def read_file_and_visualise_pc():
    project_list = project_config.get('projects', 'project_list').split(",")

    for project in project_list:
        project_range = project_config.get('projects', project).split(",")

        project_count = 0
        statement_increase = []
        checked_increase = []
        mutation_coverage = []
        coverage_scores = []
        for project_id in range(int(project_range[0]), int(project_range[1]) + 1):

            file_name = "/prob_coupling_" + project + "_" + str(project_id) + ".csv"
            file_path = str(get_project_root()) + results_folder + file_name
            mutation_file_name = "/mutant_pc_" + project + "_" + str(project_id) + ".csv"
            mutation_file_path = str(get_project_root()) + results_folder + mutation_file_name
            if path.isfile(file_path):
                project_count = project_count + 1
                with open(file_path) as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=',')
                    for row in reader:
                        statement_increase.append(float(row['statement_pc']))
                        checked_increase.append(float(row['checked_pc']))

                        coverage_scores.append((float(row['checked_pc']),
                                                float(row['statement_pc']),
                                                0,
                                                row['checked_nature'],
                                                row['statement_nature'],
                                                row['checked_modified'],
                                                row['statement_modified']))

            if path.isfile(mutation_file_path):
                with open(mutation_file_path) as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=',')
                    for row in reader:
                        #mutation_coverage.append(float(row['pc_score']))
                        if float(row['pc_score']) > 0:
                            mutation_coverage.append(float(row['pc_score']))

            save_path = str(get_project_root()) + results_folder + '/' + project
            # visualize_as_scatterplot_skew(coverage_scores, save_path,
            #                               "Probabilistic Coupling: " + project + "-" + str(project_id) +
            #                               "\n Bug count: " + str(project_count), "Count of statements")

        visualize_as_violin_plot_jitter(checked_increase, statement_increase, mutation_coverage, save_path,
                                        "Probabilistic Coupling: " + project, "PC score")


read_file_and_visualise_pc()
