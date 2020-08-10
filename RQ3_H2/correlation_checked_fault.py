import random
from os import path
from datetime import datetime

from RQ3_H2 import point_biserial_correlation_v3
from util import read_config
from utils import utils


project_config = read_config(['project_details.properties'])
random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
file_path = 'RQ3_H2/results/point_biserial_correlation__'
static_correlation_path = 'RQ3_H2/results/correlation_final_lang.txt'


# result = utils.read_json_file('RQ3_H2/results/point_biserial_correlation__7203284079767766139.json')
# formatted_result = point_biserial_correlation_v3.compute(result)
# utils.write_list_as_csv(formatted_result['for_csv'], file_path + '.csv')
# utils.write_list_as_csv(formatted_result['point_biserial_result'], file_path + '_correlation.txt')
#
# utils.write_json_file(result, file_path + '_all.json')
# visualize.visualize_correlation_as_bar(formatted_result['point_biserial_result'][1][0],
#                                        formatted_result['point_biserial_result'][1][1], 'test')


def compute():
    project_list = project_config.get('projects', 'project_list').split(",")
    # result = []
    for project in project_list:
        for_each_project(project)
        # utils.write_json_file(tests, file_path + '_' + project + '.json')
        #
        # formatted_result = point_biserial_correlation_v3.compute([{'tests': tests}])
        # utils.write_list_as_csv(formatted_result['for_csv'], file_path + '.csv')
        # utils.write_list_as_csv(formatted_result['point_biserial_result'], file_path + '_correlation.txt')
        #
        # utils.write_json_file([{'tests': tests}], file_path + '_all.json')
        #
        # utils.write_list_as_csv([[formatted_result['point_biserial_result'][1][0],
        #                          formatted_result['point_biserial_result'][1][1],
        #                          str(project) + '-' + str(tests[0]['project_id'])]],
        #                         static_correlation_path)

        #
        # visualize.visualize_correlation_as_bar(formatted_result['point_biserial_result'][1][0],
        #                                        formatted_result['point_biserial_result'][1][1],
        #                                        str(project) + '_' + str(tests[0]['project_id']))
    #
    #     result.append({'tests': tests})
    # return result


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    test_suite_size = project_config.get('projects', 'test_suite_size')

    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        print("running for project id {}".format(project_id))
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

        if len(result) > 0:
            file_name = "{}{}_{}".format(file_path, project_name, project_id)

            try:
                formatted_result = point_biserial_correlation_v3.compute([{'tests': [result]}])
                utils.write_json_file([result], file_name + '.json')
                utils.write_list_as_csv(formatted_result['for_csv'], file_name + '.csv')
                utils.write_list_as_csv(formatted_result['point_biserial_result'], file_name + '_correlation.txt')

                # utils.write_json_file([{'tests': [result]}], file_path + '_all.json')

                utils.write_list_as_csv([[formatted_result['point_biserial_result'][1][0],
                                          formatted_result['point_biserial_result'][1][1],
                                          str(project_name) + '-' + str([result][0]['project_id'])]],
                                        static_correlation_path)
            except ValueError:
                utils.write_json_file(["Error while computing coverage scores"], file_name + '.error')


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
    tmp_statement_result = create_test_suite(
       percent, list_of_test_methods, statement_coverage_coverable_lines, statement_coverage,
       list_of_bug_detecting_tests)
    tmp_checked_result = create_test_suite(
        percent, list_of_test_methods, checked_coverage_coverable_lines, checked_coverage,
        list_of_bug_detecting_tests)

    if not (len(tmp_checked_result.items()) <= 0 or len(tmp_statement_result.items()) <= 0):
        result['statement_coverage'] = tmp_statement_result
        result['checked_coverage'] = tmp_checked_result

    return result


def create_test_suite(percent, list_of_test_methods, coverable_lines, coverage_score, bug_detecting_tests):
    result = {}
    stop_condition_met = False
    score = 0
    created_test_suite_list = []
    wrk_list_of_test_methods = list_of_test_methods.copy()

    while not stop_condition_met:

        if len(wrk_list_of_test_methods) > 0:
            score = add_new_test_into_list_return_score(wrk_list_of_test_methods, created_test_suite_list,
                                                        coverable_lines, coverage_score, bug_detecting_tests, score)
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


def add_new_test_into_list_return_score(list_of_test_methods, created_test_suite_list, coverable_lines, coverage_score,
                                        bug_detecting_tests, score):
    selected_key = list_of_test_methods.pop(random.randint(0, len(list_of_test_methods) - 1))
    # score = compute_score(created_test_suite_list, coverable_lines, coverage_score)
    created_test_suite_list.append(selected_key)
    new_score = compute_score(created_test_suite_list, coverable_lines, coverage_score)

    # print(new_score)
    # if selected_key in bug_detecting_tests:
    #     print(selected_key)
    #     print(bug_detecting_tests)

    if not (new_score > score or selected_key in bug_detecting_tests):
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
