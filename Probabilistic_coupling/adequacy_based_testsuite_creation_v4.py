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


results_folder_path = 'Probabilistic_coupling/results/'
project_config = read_config(['project_details.properties'])
random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
file_path = results_folder_path + '/point_biserial_correlation__'
static_correlation_path = results_folder_path + '/correlation_final_lang.txt'
aggregated_csv = [['project_id', 'adequacy_based_tests_statement', 'adequacy_based_tests_checked']]


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    for project in project_list:
        for_each_project(project)


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        print("running for {}, with bug-id {}".format(project_name, project_id))
        is_project_path_exist = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        if path.isdir(is_project_path_exist):
            statement_as_rows = dict()
            checked_stmt_as_rows = dict()
            low_checked_coverage = 0
            # for i in range(0, int(test_suite_size)):
            current_project_path = defects4j_project_path + "/" + project_name
            modified_classes = utils.get_modified_classes(project_id, current_project_path)
            coverable_lines = utils.get_coverable_lines(project_id, current_project_path, modified_classes)
            stmt_modified_coverable_lines = []
            checked_modified_coverable_lines = []
            current_project_path = defects4j_project_path + "/" + project_name
            list_of_bug_detecting_tests = utils.get_bug_detecting_tests(project_id, current_project_path)

            modified_classes = utils.get_modified_classes(project_id, current_project_path)
            projects_statement_coverage = utils.get_statement_coverage(project_id, current_project_path
                                                                       , modified_classes)
            projects_checked_coverage = utils.get_checked_coverage(project_id, current_project_path,
                                                                   modified_classes)
            # print("list_of_bug_detecting_tests: " + ",".join(list_of_bug_detecting_tests))

            # take coverable lines
            for stmt in coverable_lines:
                try:
                    for stmt_line_no in coverable_lines[stmt]['statement_coverable_lines']:
                        stmt_modified_coverable_lines.append(stmt + "." + str(stmt_line_no))
                    for stmt_line_no in coverable_lines[stmt]['checked_coverable_lines']:
                        checked_modified_coverable_lines.append(stmt + "." + str(stmt_line_no))
                except TypeError:
                    pass

            for stmt_coverable_statements in stmt_modified_coverable_lines:
                statement_as_rows[stmt_coverable_statements] = []

            for checked_coverable_statements in checked_modified_coverable_lines:
                checked_stmt_as_rows[checked_coverable_statements] = []

            for stmt_covered_classes in projects_statement_coverage:
                for a_test in projects_statement_coverage[stmt_covered_classes]:
                    for statements in projects_statement_coverage[stmt_covered_classes][a_test]:
                        try:
                            statement_as_rows[stmt_covered_classes + "." + str(statements)].append(a_test)
                        except KeyError:
                            # print("bug detecting test does not cover this statement - statement coverage")
                            pass

            for checked_covered_classes in projects_checked_coverage:
                for a_test in projects_checked_coverage[checked_covered_classes]:
                    for statements in projects_checked_coverage[checked_covered_classes][a_test]:
                        try:
                            checked_stmt_as_rows[checked_covered_classes + "." + str(statements)].append(a_test)
                        except KeyError:
                            # print("bug detecting test does not cover this statement - checked coverage")
                            pass

            # print(dict_of_modified_coverable_lines)
            result_checked = {}
            # result_statement = {}

            # for statements in statement_as_rows:
            #     if statements in stmt_modified_coverable_lines:
            #         result_statement[statements] = divide(len(list_of_bug_detecting_tests),
            #                                               len(statement_as_rows[statements])) + ", " + \
            #                                        str(len(list_of_bug_detecting_tests)) + "/" + \
            #                                        str(len(statement_as_rows[statements]))

            for statements in checked_stmt_as_rows:
                if float(divide(len(a_intersection_b(list_of_bug_detecting_tests, checked_stmt_as_rows[statements])),
                                len(checked_stmt_as_rows[statements]))) > 0 and \
                        float(divide(len(a_intersection_b(list_of_bug_detecting_tests, statement_as_rows[statements])),
                                     len(statement_as_rows[statements]))) > 0:
                    result_checked[statements] = ".".join(statements.split(".")[:-1]) + \
                                                 ", {}-{}".format(project_name, project_id) + ", " + \
                                                 divide(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                             checked_stmt_as_rows[statements])),
                                                        len(checked_stmt_as_rows[statements])) + ", " + \
                                                 divide(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                             statement_as_rows[statements])),
                                                        len(statement_as_rows[statements])) + ", " + \
                                                 str(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                          checked_stmt_as_rows[statements]))) + "/" + \
                                                 str(len(checked_stmt_as_rows[statements])) + ", " + \
                                                 str(len(a_intersection_b(list_of_bug_detecting_tests,
                                                                          statement_as_rows[statements]))) + "/" + \
                                                 str(len(statement_as_rows[statements]))
                    if statements in checked_modified_coverable_lines:
                        pass
                else:
                    low_checked_coverage = low_checked_coverage + 1

            # utils.write_list_as_csv([["target", "statement coverage probabilistic coupling",
            #                           "len(bug detecting tests)/len(covering tests)",
            #                           "checked coverage probabilistic coupling",
            #                           "len(bug detecting tests)/len(covering tests)"]],
            #                         "{}/prob_coupling_{}_{}_{}.csv"
            #                         .format(results_folder_path, "statement", project_name, project_id))
            # utils.write_dict_as_csv(result_statement, "{}/prob_coupling_{}_{}_{}.csv"
            #                         .format(results_folder_path, "statement", project_name, project_id))
            print("low_checked_coverage: " + str(low_checked_coverage))
            if len(result_checked) > 0:
                utils.write_list_as_csv([["target",
                                          "class_name",
                                          "Proj-id",
                                          "checked_pc",
                                          "statement_pc",
                                          "len(bug_detecting_tests)/len(covering_tests)",
                                          "len(bug_detecting_tests)/len(covering_tests)"]],
                                        "{}/prob_coupling_{}_{}.csv"
                                        .format(results_folder_path, project_name, project_id))

                utils.write_dict_as_csv(result_checked, "{}/prob_coupling_{}_{}.csv"
                                        .format(results_folder_path, project_name, project_id))


def avg(lst):
    return sum(lst) / len(lst)


def get_proper_score(coupling_res):
    return coupling_res if coupling_res <= 1 else 0


def generate_adequacy_based_tests(statement_coverage_coverable_lines, projects_statement_coverage,
                                  list_of_all_tests_orig, list_of_bug_detecting_tests):
    list_of_all_tests = list_of_all_tests_orig.copy()
    adequacy_based_tests = []
    # generate initial test
    score = 0.0
    stop_condition_met = False
    while score == 0.0:
        try:
            test_suite = [list_of_all_tests.pop(random.randint(0, list_of_all_tests.__len__() - 1))]
        except ValueError:
            stop_condition_met = True
            adequacy_based_tests.append({'tests': [1],
                                         'score': 0.1,
                                         'fault_detection_test': False})
            break
        score = compute_score(test_suite, statement_coverage_coverable_lines, projects_statement_coverage)
        fault_detection_test = contained_in(list_of_bug_detecting_tests, test_suite)
        if score > 0:
            adequacy_based_tests.append({'tests': test_suite,
                                         'score': score,
                                         'fault_detection_test': fault_detection_test})

    if list_of_all_tests.__len__() <= 0:
        stop_condition_met = True

    while not stop_condition_met:
        # add new test to initial test suite
        initial_score = adequacy_based_tests[-1]['score']
        initial_test_suite = adequacy_based_tests[-1]['tests']
        current_test = [list_of_all_tests.pop(random.randint(0, list_of_all_tests.__len__() - 1))]

        # compute current score
        current_score = compute_score(initial_test_suite + current_test, statement_coverage_coverable_lines,
                                      projects_statement_coverage)
        # fault_detection_test = contained_in(list_of_bug_detecting_tests, current_test)

        # if current_score > initial_score or fault_detection_test:
        if current_score > initial_score:
            adequacy_based_tests.append({'tests': initial_test_suite + current_test,
                                         'score': current_score,
                                         'fault_detection_test':
                                             contained_in(list_of_bug_detecting_tests,
                                                          initial_test_suite + current_test)})

        if list_of_all_tests.__len__() <= 0:
            stop_condition_met = True

    return adequacy_based_tests


def contained_in(lst, sub):
    return [value for value in lst if value in sub].__len__() > 0


def a_intersection_b(a, b):
    # return a.__len__()
    return [value for value in a if value in b]


def create_test_suites(percent, project_id, current_project_path, list_of_bug_detecting_tests):
    result = {}
    modified_classes = utils.get_modified_classes(project_id, current_project_path)
    projects_statement_coverage = utils.get_statement_coverage(project_id, current_project_path, modified_classes)
    projects_checked_coverage = utils.get_checked_coverage(project_id, current_project_path, modified_classes)
    list_of_test_methods = get_relevant_test_methods(modified_classes, projects_statement_coverage)
    statement_coverage_coverable_lines = utils.get_coverable_line_numbers(
        project_id, current_project_path, modified_classes, "statement_coverable_lines")
    checked_coverage_coverable_lines = utils.get_coverable_line_numbers(
        project_id, current_project_path, modified_classes, "checked_coverable_lines")

    # For each modified classes
    tmp_statement_result = create_test_suite(
       percent, list_of_test_methods, statement_coverage_coverable_lines, projects_statement_coverage,
       list_of_bug_detecting_tests)
    tmp_checked_result = create_test_suite(
        percent, list_of_test_methods, checked_coverage_coverable_lines, projects_checked_coverage,
        list_of_bug_detecting_tests)

    if len(tmp_checked_result.items()) > 0:
        result['checked_coverage'] = tmp_checked_result

    if len(tmp_statement_result.items()) > 0:
        result['statement_coverage'] = tmp_statement_result

    return result


def create_test_suite(percent, list_of_test_methods, coverable_lines, projects_coverage_dict, bug_detecting_tests):
    result = {}
    stop_condition_met = False
    score = 0
    created_test_suite_list = []
    wrk_list_of_test_methods = list_of_test_methods.copy()

    while not stop_condition_met:

        if len(wrk_list_of_test_methods) > 0:
            score = add_new_test_into_list_return_score(wrk_list_of_test_methods, created_test_suite_list,
                                                        coverable_lines, projects_coverage_dict, bug_detecting_tests,
                                                        score)
        else:
            stop_condition_met = True

        if score >= percent:
            stop_condition_met = True

    if score >= percent:
        result['score'] = score
        # result['t_score'] = percent
        result['tests'] = created_test_suite_list
        result['is_bug_detecting_test_included'] = False
        for bug_detecting_test in bug_detecting_tests:
            if bug_detecting_test in created_test_suite_list:
                result['is_bug_detecting_test_included'] = True
        return result
    else:
        return result


def add_new_test_into_list_return_score(list_of_test_methods, created_test_suite_list, coverable_lines,
                                        projects_coverage_dict, bug_detecting_tests, score):
    selected_key = list_of_test_methods.pop(random.randint(0, len(list_of_test_methods) - 1))
    # score = compute_score(created_test_suite_list, coverable_lines, coverage_score)
    created_test_suite_list.append(selected_key)
    new_score = compute_score(created_test_suite_list, coverable_lines, projects_coverage_dict)

    # print(new_score)
    # if selected_key in bug_detecting_tests:
    #     print(selected_key)
    #     print(bug_detecting_tests)

    if not new_score > score:
        created_test_suite_list.remove(selected_key)

    return new_score


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


def list_a_contains_b(a, b):
    return not set(a).isdisjoint(b)


def divide(a, b):
    try:
        # return str(a / b)
        return str(1) if a / b > 1 else str(a / b)
    except ZeroDivisionError:
        return str(0)
