import random
from os import path
from datetime import datetime

# from pyaml import print

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
statement_as_rows = []
checked_stmt_as_rows = []


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    for project in project_list:
        for_each_project(project)

    file_name = "{}{}".format(file_path, 'full')
    utils.write_list_as_csv(aggregated_csv, file_name + '.csv')


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    test_suite_size = project_config.get('projects', 'test_suite_size')

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        print("running for {}, with bug-id {}".format(project_name, project_id))
        result = {}
        is_project_path_exist = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        probabilistic_coupling_statement_for_avg = []
        probabilistic_coupling_checked_for_avg = []
        adequacy_based_tests_statement = []
        adequacy_based_tests_checked = []
        list_of_bug_detecting_tests = []
        if path.isdir(is_project_path_exist):
            for i in range(0, int(test_suite_size)):
                current_project_path = defects4j_project_path + "/" + project_name
                list_of_bug_detecting_tests = utils.get_bug_detecting_tests(project_id, current_project_path)

                modified_classes = utils.get_modified_classes(project_id, current_project_path)
                projects_statement_coverage = utils.get_statement_coverage(project_id, current_project_path
                                                                           , modified_classes)

                list_of_all_tests = get_relevant_test_methods(modified_classes, projects_statement_coverage)
                list_of_all_tests = list(dict.fromkeys(list_of_all_tests))
                for stmt_covered_classes in projects_statement_coverage:
                    for bug_detecting_test in list_of_bug_detecting_tests:
                        for statements in projects_statement_coverage[stmt_covered_classes][bug_detecting_test]:
                            statement_as_rows.append(stmt_covered_classes + "." + str(statements))

                projects_checked_coverage = utils.get_checked_coverage(project_id, current_project_path,
                                                                       modified_classes)
                statement_template = pd.DataFrame(index=statement_as_rows, columns=list_of_all_tests)

                for checked_covered_classes in projects_checked_coverage:
                    for bug_detecting_test in list_of_bug_detecting_tests:
                        try:
                            for statements in projects_checked_coverage[checked_covered_classes][bug_detecting_test]:
                                checked_stmt_as_rows.append(checked_covered_classes + "." + str(statements))
                        except KeyError:
                            print("Bug detecting test does not covered this class")

                checked_template = pd.DataFrame(index=checked_stmt_as_rows, columns=list_of_all_tests)

                # print(statement_template)

                for stmt_covered_classes in projects_statement_coverage:
                    for a_test in list_of_all_tests:
                        try:
                            for statements in projects_statement_coverage[stmt_covered_classes][a_test]:
                                statement_template[a_test][stmt_covered_classes + "." + str(statements)] = 1
                        except KeyError:
                            pass

                statement_template.to_csv('statement_template.csv')

                for checked_covered_classes in projects_statement_coverage:
                    for a_test in list_of_all_tests:
                        try:
                            for statements in projects_statement_coverage[checked_covered_classes][a_test]:
                                checked_template[a_test][checked_covered_classes + "." + str(statements)] = 1
                        except KeyError:
                            pass
                checked_template.to_csv('checked_template.csv')

                # for index, row in statement_template.iterrows():
                #     print(row)
                print(statement_template.loc['com.fasterxml.jackson.databind.JavaType.76'])

                exit(0)


                statement_coverage_coverable_lines = utils.get_coverable_line_numbers(
                    project_id, current_project_path, modified_classes, "statement_coverable_lines")
                checked_coverage_coverable_lines = utils.get_coverable_line_numbers(
                    project_id, current_project_path, modified_classes, "checked_coverable_lines")

                projects_checked_coverage = utils.get_checked_coverage(project_id, current_project_path,
                                                                       modified_classes)
                adequacy_based_tests_statement = generate_adequacy_based_tests(statement_coverage_coverable_lines,
                                                                               projects_statement_coverage,
                                                                               list_of_all_tests,
                                                                               list_of_bug_detecting_tests)

                adequacy_based_tests_checked = generate_adequacy_based_tests(checked_coverage_coverable_lines,
                                                                             projects_checked_coverage,
                                                                             list_of_all_tests,
                                                                             list_of_bug_detecting_tests)

                probabilistic_coupling_statement_for_avg.append(get_proper_score(
                                          a_intersection_b(list_of_bug_detecting_tests,
                                                           adequacy_based_tests_statement[-1]['tests']) /
                                          len(adequacy_based_tests_statement[-1]['tests'])))

                probabilistic_coupling_checked_for_avg.append(get_proper_score(
                                          a_intersection_b(list_of_bug_detecting_tests,
                                                           adequacy_based_tests_checked[-1]['tests']) /
                                          len(adequacy_based_tests_checked[-1]['tests'])))

        try:
            aggregated_csv.append([project_name + '-' + str(project_id), mean(probabilistic_coupling_statement_for_avg),
                                   mean(probabilistic_coupling_checked_for_avg)])
        except statistics.StatisticsError:
            pass

        result['project_id'] = project_id
        result['adequacy_based_tests_statement'] = adequacy_based_tests_statement
        result['adequacy_based_tests_checked'] = adequacy_based_tests_checked
        result['list_of_bug_detecting_tests'] = list_of_bug_detecting_tests

        # file_name = "{}{}_{}".format(file_path, project_name, project_id)
        # utils.write_json_file(result, file_name + '.json')


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
    return a.__len__()
    # return [value for value in a if value in b].__len__()


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
