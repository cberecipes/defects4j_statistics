import json
import random
from os import path

from util import read_config

project_config = read_config(['project_details.properties'])


def compute():
    for_list_of_projects()


def for_list_of_projects():
    project_list = project_config.get('projects', 'project_list').split(",")
    result = {}
    for project in project_list:
        print("for Project " + project)
        result['tests'] = for_each_project(project)
        result['project'] = project

    print(result)


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    percentage_range = project_config.get('projects', 'test_suite_coverage_percentage').split(",")
    test_suite_size = project_config.get('projects', 'test_suite_size')
    final_result = {}
    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        is_project_path_exist = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        if path.isdir(is_project_path_exist):
            print("for project Id " + str(project_id))
            test_suite_size_percent = []
            for percent in percentage_range:
                print("for project percent " + percent)
                current_project_path = defects4j_project_path + "/" + project_name
                test_suites = {}
                test_suite_list = []
                for i in range(0, int(test_suite_size)):

                    print("for the test suite index number " + str(i + 1))
                    test_suite_list.append(create_test_suites(int(percent), project_id, current_project_path))
                test_suites['percentage'] = percent
                test_suites['test_suites'] = test_suite_list

                test_suite_size_percent.append(test_suites)
            final_result['project_id'] = project_id
            final_result['tests'] = test_suite_size_percent
    return final_result


def create_test_suites(percent, project_id, current_project_path):
    result = {}
    modified_classes = get_modified_classes(project_id, current_project_path)
    statement_coverage = get_statement_coverage(project_id, current_project_path, modified_classes)
    checked_coverage = get_checked_coverage(project_id, current_project_path, modified_classes)
    list_of_test_methods = get_relevant_test_methods_1(modified_classes, statement_coverage)
    list_of_bug_detecting_tests = get_bug_detecting_tests(project_id, current_project_path)

    statement_coverage_coverable_lines = get_coverable_line_numbers(
        get_coverable_lines(project_id, current_project_path, modified_classes),
        modified_classes, "statement_coverable_lines")
    checked_coverage_coverable_lines = get_coverable_line_numbers(
        get_coverable_lines(project_id, current_project_path, modified_classes),
        modified_classes, "checked_coverable_lines")

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
    while not stop_condition_met:
        created_test_suite_list = add_new_test_into_list(list_of_test_methods, created_test_suite_list)
        score = compute_score(
            created_test_suite_list, coverable_lines, coverage_score)
        if score >= percent or len(created_test_suite_list) == len(list_of_test_methods):
            stop_condition_met = True
    result['score'] = score
    result['tests'] = created_test_suite_list
    result['is_bug_detecting_test_included'] = False
    for bug_detecting_test in bug_detecting_tests:
        if bug_detecting_test in created_test_suite_list:
            result['is_bug_detecting_test_included'] = True

    return result


def add_new_test_into_list(list_of_test_methods, created_test_suite_list):
    current_size = len(created_test_suite_list)
    list_to_shuffle = list(range(0, len(list_of_test_methods)))

    while not len(created_test_suite_list) >= current_size + 1:
        random.shuffle(list_to_shuffle)
        selected_key = list_of_test_methods[list_to_shuffle[0]]
        if selected_key not in created_test_suite_list:
            created_test_suite_list.append(selected_key)

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

    # print("---------- score calc ----------")
    # print(len(created_test_suite_list))
    # print(created_test_suite_list)
    # print("covered_lines " + str(covered_lines))
    # print("coverable_lines " + str(coverable_lines))
    # print("covered_lines/coverable_lines " + str((covered_lines/coverable_lines)*100))
    return (covered_lines/coverable_lines) * 100


def get_bug_detecting_tests(project_id, current_project_path):
    trigger_tests = []
    file_path = current_project_path + "/trigger_tests/" + str(project_id)
    for line in read_file(file_path):
        if line.strip().startswith("---"):
            trigger_tests.append(line.replace("-", "").strip())

    return trigger_tests


def get_relevant_test_methods_1(modified_classes, statement_coverage):
    test_methods = []

    for modified_class in modified_classes:
        for key, value in statement_coverage[modified_class].items():
            test_methods.append(key)

    return test_methods


def get_coverable_line_numbers(coverable_lines_json, modified_classes, for_which_coverage):
    statement_coverable_lines = 0
    for modified_class in modified_classes:
        statement_coverable_lines = \
            statement_coverable_lines + len(coverable_lines_json[modified_class][for_which_coverage])
    return statement_coverable_lines


def get_statement_coverage(project_id, current_project_path, modified_classes):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "line_coverage.json"
    statement_coverage = read_json_file(file_path)
    updated_statement_coverage = {}
    for modified_class in modified_classes:
        updated_statement_coverage[modified_class] = statement_coverage[modified_class]

    return updated_statement_coverage


def get_checked_coverage(project_id, current_project_path, modified_classes):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "checked_coverage.json"
    checked_coverage = read_json_file(file_path)
    updated_checked_coverage = {}
    for modified_class in modified_classes:
        updated_checked_coverage[modified_class] = checked_coverage[modified_class]

    return updated_checked_coverage


def get_modified_classes(project_id, current_project_path):
    file_path = current_project_path + "/modified_classes/" + str(project_id) + ".src"
    return read_file(file_path)


def get_coverable_lines(project_id, current_project_path, modified_classes):
    required_coverage = {}
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "coverable_lines.json"
    all_class_data = read_json_file(file_path)
    for modified_class in modified_classes:
        try:
            required_coverage[modified_class] = all_class_data[modified_class]
        except KeyError:
            pass

    return required_coverage


def read_file(file_path):
    if not path.exists(file_path):
        # print("File not exist!" + file_path)
        file_contents = []
    else:
        f = open(file_path, encoding="ISO-8859-1")
        file_contents = f.read().splitlines()
        f.close()
    return file_contents


def read_json_file(file_path):
    if not path.exists(file_path):
        # print("File not exist!" + file_path)
        output = {}
    else:
        with open(file_path, encoding="ISO-8859-1") as fp:
            output = json.load(fp)

    return output
