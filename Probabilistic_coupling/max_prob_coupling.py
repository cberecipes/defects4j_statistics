import csv
import random
from os import path
from datetime import datetime

# from pyaml import print
from Probabilistic_coupling.tests.class_details import print_class_details
from util import read_config
from utils import utils
from statistics import mean
import statistics
import pandas as pd
import numpy as np
from utils.utils import read_file

results_folder_path = 'Probabilistic_coupling/results/'
project_config = read_config(['project_details.properties'])
aggregated_csv = [['project_id', 'adequacy_based_tests_statement', 'adequacy_based_tests_checked']]
max_pc = results_folder_path + "max_pc.csv"


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    # utils.write_list_as_csv([["target",
    #                           "Proj-id",
    #                           "checked_pc",
    #                           "statement_pc",
    #                           "len(bug_detecting_tests)/len(covering_tests)",
    #                           "len(bug_detecting_tests)/len(covering_tests)"]],
    #                         max_pc)

    utils.write_list_as_csv([["checked_pc_max", "statement_pc_max", "project-id"]],
                            max_pc)
    for project in project_list:
        for_each_project(project)

    # file_name = "{}{}".format(file_path, 'full')
    # utils.write_list_as_csv(aggregated_csv, file_name + '.csv')


statement_pc = []
checked_pc = []


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        result_file_path = "{}prob_coupling_{}_{}.csv".format(results_folder_path, project_name, project_id)

        # try:
        #     df = pd.read_csv(result_file_path)
        #     df[df.checked_pc == df.checked_pc.max()][df.statement_pc != 0][df.checked_pc != 0].to_csv(max_pc, index=False, mode='a', header=False)
        #     df[df.statement_pc == df.statement_pc.max()][df.checked_pc != 0][df.statement_pc != 0].to_csv(max_pc, index=False, mode='a', header=False)
        # except FileNotFoundError:
        #     pass
        try:
            df = pd.read_csv(result_file_path)
            if df['checked_pc'].max() != 0 and df['statement_pc'].max() != 0:
                utils.write_string_to_file(str(df['checked_pc'].max()) + ', ' +
                                           str(df['statement_pc'].max()) + ", {}-{} \n".
                                           format(project_name, project_id), max_pc)

        except FileNotFoundError:
            pass
