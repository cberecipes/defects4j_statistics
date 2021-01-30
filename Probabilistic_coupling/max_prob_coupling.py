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
aggregated_csv = [['project_id', 'class_name', 'adequacy_based_tests_statement', 'adequacy_based_tests_checked']]
max_pc = results_folder_path + "max_pc.csv"
max_pc_per_project = results_folder_path + "max_pc_per_proj/"
max_pc_per_project_file = ""


def compute():
    global max_pc_per_project_file
    project_list = project_config.get('projects', 'project_list').split(",")
    # utils.write_list_as_csv([["target",
    #                           "Proj-id",
    #                           "checked_pc",
    #                           "statement_pc",
    #                           "len(bug_detecting_tests)/len(covering_tests)",
    #                           "len(bug_detecting_tests)/len(covering_tests)"]],
    #                         max_pc)

    utils.write_list_as_csv([["checked_pc_max", "statement_pc_max", "mutation_pc_max", "class_name", "project-id"]],
                            max_pc)
    for project in project_list:
        max_pc_per_project_file = max_pc_per_project + project + ".csv"
        utils.write_list_as_csv([["checked_pc_max", "statement_pc_max", "mutation_pc_max", "class_name", "project-id"]],
                                max_pc_per_project_file)
        for_each_project(project)

    # file_name = "{}{}".format(file_path, 'full')
    # utils.write_list_as_csv(aggregated_csv, file_name + '.csv')


statement_pc = []
checked_pc = []


def for_each_project(project_name):
    global max_pc_per_project_file
    project_range = project_config.get('projects', project_name).split(",")

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        result_file_path = "{}prob_coupling_{}_{}.csv".format(results_folder_path, project_name, project_id)
        mutation_result_file_path = "{}mutant_pc_{}_{}.csv".format(results_folder_path, project_name, project_id)

        try:
            df = pd.read_csv(result_file_path)
            mutation_max_pc_score = get_mutation_pc_max(mutation_result_file_path)
            for class_name in df.class_name.unique():
                if df['checked_pc'].max() != 0 and df['statement_pc'].max() != 0 and mutation_max_pc_score != 0:
                    utils.write_string_to_file(str(df[df['class_name'] == class_name]['checked_pc'].max()) + ', ' +
                                               str(df[df['class_name'] == class_name]['statement_pc'].max()) + ', ' +
                                               mutation_max_pc_score + ', ' +
                                               class_name +
                                               ", {}-{} \n".format(project_name, project_id), max_pc)

                    utils.write_string_to_file(str(df[df['class_name'] == class_name]['checked_pc'].max()) + ', ' +
                                               str(df[df['class_name'] == class_name]['statement_pc'].max()) + ', ' +
                                               mutation_max_pc_score + ', ' +
                                               class_name +
                                               ", {}-{} \n".format(project_name, project_id), max_pc_per_project_file)

        except FileNotFoundError:
            pass


def get_mutation_pc_max(mutation_result_file_path):
    df = pd.read_csv(mutation_result_file_path)
    return str(df['pc_score'].max())
