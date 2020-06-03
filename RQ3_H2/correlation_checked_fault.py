import random
import sys
from os import path

from RQ3_H2 import point_biserial_correlation
from util import read_config
from utils import utils

project_config = read_config(['project_details.properties'])
random_number = str(random.randint(1, sys.maxsize-1))
file_path = 'RQ3_H2/results/point_biserial_correlation__' + random_number


def compute():
    result = for_list_of_projects()
    # result = utils.read_json_file('RQ3_H2/results/point_biserial_correlation__7203284079767766139.json')
    point_bc = point_biserial_correlation.compute(result)
    utils.write_list_as_csv(point_bc, file_path + '.csv')
    utils.write_json_file(result, file_path + '_all.json')


def for_list_of_projects():
    project_list = project_config.get('projects', 'project_list').split(",")
    result = []
    for project in project_list:
        tests = for_each_project(project)
        utils.write_json_file(tests[0], file_path + '_' + project + '.json')
        result.append({'tests': tests, 'project': project})
    return result


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    test_suite_size = project_config.get('projects', 'test_suite_size')
    final_result = []
    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        result = {}
        is_project_path_exist = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        if path.isdir(is_project_path_exist):
            test_suite_size_percent = []
            current_project_path = defects4j_project_path + "/" + project_name
            list_of_bug_detecting_tests = utils.get_bug_detecting_tests(project_id, current_project_path)
            for percent in percentage_range:
                test_suites = {}
                test_suite_list = []
                print("for project " + str(project_name) +
                      " with id " + str(project_id) +
                      " for percent " + str(percent))
                for i in range(0, int(test_suite_size)):
                    test_suite_list.append(create_test_suites(
                        int(percent), project_id, current_project_path, list_of_bug_detecting_tests))
                test_suites['percentage'] = int(percent)
                test_suites['test_suites'] = test_suite_list

                test_suite_size_percent.append(test_suites)
            result['project_id'] = project_id
            result['tests'] = test_suite_size_percent
            result['list_of_bug_detecting_tests'] = list_of_bug_detecting_tests
            final_result.append(result)
    return final_result


def create_test_suites(percent, project_id, current_project_path, list_of_bug_detecting_tests):
    result = {}
    modified_classes = utils.get_modified_classes(project_id, current_project_path)
    statement_coverage = utils.get_statement_coverage(project_id, current_project_path, modified_classes)
    checked_coverage = utils.get_checked_coverage(project_id, current_project_path, modified_classes)
    list_of_test_methods = get_relevant_test_methods(modified_classes, statement_coverage)
    statement_coverage_coverable_lines = utils.get_coverable_line_numbers(
        project_id, current_project_path, modified_classes, "statement_coverable_lines")
    checked_coverage_coverable_lines = utils.get_coverable_line_numbers(
        project_id, current_project_path, modified_classes, "checked_coverable_lines")

    # For each modified classes
    result['statement_coverage'] = create_test_suite(
        percent, list_of_test_methods, statement_coverage_coverable_lines, statement_coverage,
        list_of_bug_detecting_tests)
    result['checked_coverage'] = create_test_suite(
        percent, list_of_test_methods, checked_coverage_coverable_lines, checked_coverage,
        list_of_bug_detecting_tests)
    return result


def create_test_suite(percent, list_of_test_methods, coverable_lines, coverage_score, bug_detecting_tests):
    result = {}
    stop_condition_met = False
    score = 0
    created_test_suite_list = []
    times_ran = 0
    while not stop_condition_met:
        times_ran = times_ran + 1
        created_test_suite_list = add_new_test_into_list(list_of_test_methods, created_test_suite_list)
        score = compute_score(
            created_test_suite_list, coverable_lines, coverage_score)
        if score >= percent or len(created_test_suite_list) == len(list_of_test_methods) or times_ran > 100:
            stop_condition_met = True
    result['score'] = score
    result['tests'] = created_test_suite_list
    result['is_bug_detecting_test_included'] = False
    for bug_detecting_test in bug_detecting_tests:
        if bug_detecting_test in created_test_suite_list:
            result['is_bug_detecting_test_included'] = True

    if result['score'] >= percent:
        return result
    else:
        result['score'] = 0
        result['tests'] = []
        result['is_bug_detecting_test_included'] = False
        return result


def add_new_test_into_list(list_of_test_methods, created_test_suite_list):
    current_size = len(created_test_suite_list)
    list_to_shuffle = list(range(0, len(list_of_test_methods)))
    times_ran = 0
    while not len(created_test_suite_list) >= current_size + 1:
        times_ran = times_ran + 1
        random.shuffle(list_to_shuffle)
        selected_key = list_of_test_methods[list_to_shuffle[0]]
        if selected_key not in created_test_suite_list:
            created_test_suite_list.append(selected_key)

        if times_ran > 20000:
            break

    return created_test_suite_list


def compute_score(created_test_suite_list, coverable_lines, coverage_score):
    computed_score = {}
    covered_lines = 0
    for key, value in coverage_score.items():
        for key2, value2 in value.items():
            if key2 in created_test_suite_list:
                if key not in computed_score:
                    computed_score[key] = list(set(value2))
                else:
                    computed_score[key] = list(set(computed_score[key] + value2))

    for key, value in computed_score.items():
        covered_lines = covered_lines + len(value)

    return (covered_lines/coverable_lines) * 100


def get_relevant_test_methods(modified_classes, statement_coverage):
    test_methods = []

    for modified_class in modified_classes:
        for key, value in statement_coverage[modified_class].items():
            test_methods.append(key)

    return test_methods
