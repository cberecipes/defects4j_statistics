from os import path
from datetime import datetime

from RQ2_H1 import format_as_csv
from util import read_config
from utils import utils
from utils.utils import *

project_config = read_config(['project_details.properties'])


def compute():
    random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
    file_path = 'RQ2_H1/results/does_coverage_increase__' + random_number
    result = for_list_of_projects()
    formatted_result = format_as_csv.format_contents(result)

    utils.write_list_as_csv(formatted_result, file_path + '.csv')
    utils.write_json_file(result, file_path + '.json')


def for_list_of_projects():
    project_list = project_config.get('projects', 'project_list').split(",")
    result = []
    for project in project_list:
        result.append({'project_name': project, 'result': for_each_project(project)})
    return result


def for_each_project(project_name):
    project_range = project_config.get('projects', project_name).split(",")
    defects4j_project_path = project_config.get('paths', 'defects4j_project_path')
    # for each project fixed versions
    final_result = []
    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        project_path = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        if path.isdir(project_path):
            result = {}
            scores = {}
            current_project_path = defects4j_project_path + "/" + project_name
            modified_classes = get_modified_classes(project_id, current_project_path)
            list_of_bug_detecting_tests = get_bug_detecting_tests(project_id, current_project_path)
            statement_coverage = get_statement_coverage(project_id, current_project_path, modified_classes)
            checked_coverage = get_checked_coverage(project_id, current_project_path, modified_classes)

            sc_coverable_line_nr = get_coverable_line_numbers(
                project_id, current_project_path, modified_classes, "statement_coverable_lines")
            cc_coverable_line_nr = get_coverable_line_numbers(
                project_id, current_project_path, modified_classes, "checked_coverable_lines")

            statement_coverage_buggy = compute_coverage_score(statement_coverage,
                                                              list_of_bug_detecting_tests, sc_coverable_line_nr)

            checked_coverage_buggy = compute_coverage_score(checked_coverage,
                                                            list_of_bug_detecting_tests, cc_coverable_line_nr)

            statement_coverage_fixed = compute_coverage_score(statement_coverage, [], sc_coverable_line_nr)

            checked_coverage_fixed = compute_coverage_score(checked_coverage, [], cc_coverable_line_nr)

            result['project_id'] = project_id
            scores['statement_coverage'] = {'buggy': statement_coverage_buggy,
                                            'fixed': statement_coverage_fixed,
                                            'list_of_bug_detecting_tests': list_of_bug_detecting_tests}
            scores['checked_coverage'] = {'buggy': checked_coverage_buggy,
                                          'fixed': checked_coverage_fixed,
                                          'list_of_bug_detecting_tests': list_of_bug_detecting_tests}

            scores['mutation_score'] = {'buggy': get_mutation_score('mutation_score_buggy', project_path),
                                        'fixed': get_mutation_score('mutation_score', project_path),
                                        'list_of_bug_detecting_tests': list_of_bug_detecting_tests}

            result['scores'] = scores
            final_result.append(result)

    return final_result


def get_mutation_score(score_type, score_path):
    return utils.read_json_file(score_path + '/mutation_score.txt')[score_type]
