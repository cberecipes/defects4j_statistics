from os import path
from datetime import datetime
import csv
from util import read_config

import random
from Probabilistic_coupling.tests.class_details import print_class_details
from utils import utils
from statistics import mean
import statistics
import pandas as pd

from utils.utils import a_intersection_b, len_a_intersection_b

results_folder_path = 'Probabilistic_coupling/results/'
project_config = read_config(['project_details.properties'])
random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
file_path = results_folder_path + '/mutant_pc_'
aggregated_csv = [['project_id', 'adequacy_based_tests_statement', 'adequacy_based_tests_checked']]
mutants_details = "kill.csv"
mutants_killed_details = "killMap.csv"
test_map_details = "testMap.csv"


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    for project in project_list:
        for_each_project(project)


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    projects_exported_path = project_config.get('paths', 'projects_exported_path')

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        probabilistic_coupling = [['mutant_id', 'pc_score', 'lengths']]
        mutant_kill_details_as_dict = {}
        test_map_as_dict = {}
        print("running for {}, with bug-id {}".format(project_name, project_id))
        exported_project_path = projects_exported_path + "/" + project_name + "_" + str(project_id) + "_" + "fixed"
        project_path = defects4j_project_path + "/" + project_name
        test_map_file = exported_project_path + "/" + test_map_details

        if path.isfile(exported_project_path + "/" + mutants_killed_details):
            prepare_test_map(test_map_file)
            with open(exported_project_path + "/" + mutants_killed_details) as csv_file:
                reader = csv.DictReader(csv_file, delimiter=',')
                for mutant in reader:
                    try:
                        mutant_kill_details_as_dict[mutant['MutantNo']].append(mutant['TestNo'])
                    except KeyError:
                        mutant_kill_details_as_dict[mutant['MutantNo']] = []
                        mutant_kill_details_as_dict[mutant['MutantNo']].append(mutant['TestNo'])

            with open(test_map_file) as csv_file:
                reader = csv.DictReader(csv_file, delimiter=',')
                for test in reader:
                    test_map_as_dict[test['TestName']] = test['TestNo']

            list_of_bug_detecting_test = covert_tests_to_numbers(utils.get_bug_detecting_tests(project_id,
                                                                                               project_path),
                                                                 test_map_as_dict)

            for mutant in mutant_kill_details_as_dict:
                len_of_bug_detecting_test_kill_a_mutant = len_a_intersection_b(mutant_kill_details_as_dict[mutant],
                                                                               list_of_bug_detecting_test)
                len_of_tests = len(mutant_kill_details_as_dict[mutant])
                probabilistic_coupling.append([mutant, len_of_bug_detecting_test_kill_a_mutant / len_of_tests,
                                               str(len_of_bug_detecting_test_kill_a_mutant) + "/" + str(len_of_tests)])

            print(test_map_as_dict)
            print(mutant_kill_details_as_dict)
            print(list_of_bug_detecting_test)
            print(probabilistic_coupling)

            with open(file_path + project_name + "_" + str(project_id) + ".csv", mode='w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(probabilistic_coupling)


def covert_tests_to_numbers(list_of_bug_detecting_test, test_map_as_dict):
    result = []
    for bug_detecting_test in list_of_bug_detecting_test:
        result.append(test_map_as_dict[bug_detecting_test])
    return result


def prepare_test_map(test_map_file):
    modified_tests = ['TestNo,TestName\n']
    with open(test_map_file) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for tests in reader:
            modified_tests.append(tests['TestNo'] + "," + tests['TestName'].replace("[", "::").replace("]", "") + "\n")

    file1 = open(test_map_file, 'w')
    file1.writelines(modified_tests)
    file1.close()
