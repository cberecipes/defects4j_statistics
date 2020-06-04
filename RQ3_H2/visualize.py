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


visualize_whole_project()
