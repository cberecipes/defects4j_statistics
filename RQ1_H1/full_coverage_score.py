from datetime import datetime

from RQ1_H1 import format_as_csv
from util import read_config
from utils.utils import *

project_config = read_config(['project_details.properties'])


def compute():
    random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
    file_path = 'RQ1_H1/results/coverage_score' + random_number
    output = for_selected_project()
    formatted_score = format_as_csv.format(output)

    write_list_as_csv(formatted_score, file_path + '.csv')


def for_selected_project():
    project_list = project_config.get('projects', 'project_list').split(",")
    result = []
    if len(project_list) > 1:
        print("reduce number of projects to 1")
        exit(0)

    for project in project_list:
        result.append({'project_name': project, 'result': compute_score(project)})
    return result


def compute_score(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    project_range = range(int(project_range[0]), int(project_range[1]) + 1)
    if len(project_range) > 1:
        print("reduce number of project counts to 1")
        exit(0)

    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    result = {}
    for project_id in project_range:
        current_project_path = defects4j_project_path + "/" + project_name
        all_classes = get_all_classes(project_id, current_project_path)
        current_project_path + "/trace_files/" + str(project_id) + "f/" + "line_coverage.json"

        statement_coverage = get_statement_coverage(project_id, current_project_path, all_classes)
        checked_coverage = get_checked_coverage(project_id, current_project_path, all_classes)

        sc_coverable_line_nr = get_coverable_line_numbers(
            project_id, current_project_path, all_classes, "statement_coverable_lines")
        cc_coverable_line_nr = get_coverable_line_numbers(
            project_id, current_project_path, all_classes, "checked_coverable_lines")

        statement_coverage_score = compute_coverage_score(statement_coverage,
                                                          [], sc_coverable_line_nr)

        checked_coverage_score = compute_coverage_score(checked_coverage,
                                                        [], cc_coverable_line_nr)

        result['project_id'] = project_id
        result['statement_coverage_score'] = statement_coverage_score
        result['checked_coverage_score'] = checked_coverage_score

    return result


def get_all_classes(project_id, current_project_path):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "line_coverage.json"
    statement_coverage = read_json_file(file_path)
    return [st for st in statement_coverage]


def get_all_tests(project_id, current_project_path):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "all_test_methods"
    all_test_methods = read_file(file_path)

    return [tm.split("(")[1].split(")")[0] + "::" + tm.split("(")[0] for tm in all_test_methods]