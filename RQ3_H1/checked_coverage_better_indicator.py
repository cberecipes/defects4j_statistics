from os import path
from collections import defaultdict
from datetime import datetime

from RQ3_H1 import format_as_csv
from util import read_config
from utils import utils

project_config = read_config(['project_details.properties'])


def compute():
    random_number = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
    file_path = 'RQ3_H1/results/does_coverage_increase__' + random_number
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
    final_result = []
    # for each project fixed versions
    for project_id in range(int(project_range[0]), int(project_range[1]) + 1):
        is_project_path_exist = defects4j_project_path + "/" + project_name + "/trace_files/" + str(project_id) + "f"
        if path.isdir(is_project_path_exist):
            result = {}
            scores = {}
            patch_path = defects4j_project_path + "/" + project_name + "/" + "/patches/" + str(project_id) + ".src.patch"
            current_project_path = defects4j_project_path + "/" + project_name
            modified_classes = utils.get_modified_classes(project_id, current_project_path)
            statement_coverage = utils.get_statement_coverage(project_id, current_project_path, modified_classes)
            checked_coverage = utils.get_checked_coverage(project_id, current_project_path, modified_classes)
            coverable_lines = utils.get_coverable_lines(project_id, current_project_path, modified_classes)
            dict_of_modified_coverable_lines = get_modified_coverable_lines(patch_path, coverable_lines)
            list_of_bug_detecting_tests = utils.get_bug_detecting_tests(project_id, current_project_path)
            statement_covering_tests = get_covering_tests(
                statement_coverage, dict_of_modified_coverable_lines, 'statement_coverable_lines')
            checked_covering_tests = get_covering_tests(
                checked_coverage, dict_of_modified_coverable_lines, 'checked_coverable_lines')
            result['project_id'] = project_id
            scores['list_of_bug_detecting_tests'] = list_of_bug_detecting_tests
            scores['coverable_lines'] = dict_of_modified_coverable_lines
            scores['statement_covering_tests'] = statement_covering_tests
            scores['checked_covering_tests'] = checked_covering_tests
            result['scores'] = scores
            final_result.append(result)
    return final_result


def get_covering_tests(coverage, dict_of_modified_coverable_lines, covering_type):
    list_of_covering_tests = []
    for key, covering_lines in dict_of_modified_coverable_lines.items():
        for test_method, i_covering_lines in coverage[key].items():
            covering_test_with_score = {}
            lines_covered = utils.intersection(list(map(int, i_covering_lines)), covering_lines[covering_type])
            detailed_lines_covered = {}
            if len(lines_covered) > 0:
                covering_test_with_score['test'] = test_method
                detailed_lines_covered['class'] = key
                detailed_lines_covered['lines_covered'] = lines_covered
                detailed_lines_covered['bug_fix_code_covered'] = \
                    (len(lines_covered) / len(covering_lines[covering_type])) * 100

                covering_test_with_score['detailed_lines_covered'] = detailed_lines_covered
                list_of_covering_tests.append(covering_test_with_score)

    return list_of_covering_tests


def get_modified_lines(patch_path):
    counts = {}
    class_name = None
    for line in utils.read_file(patch_path):
        if line.startswith("diff --git "):
            class_name = get_class_name(line.split(" "))
            # Some times modified files are not java files, eg .txt etc...
            # class_name will be None if they are not .java file
            if class_name is None:
                break
        if line.startswith("@@ "):
            comma_separated_line = line.split("@@")[1].split("+")[1].split(",")
            try:
                counts[class_name] = counts[class_name] + [*range(int(comma_separated_line[0]),
                                                                  int(comma_separated_line[0])
                                                                  + int(comma_separated_line[1]))]
            except KeyError:
                counts[class_name] = [*range(int(comma_separated_line[0]), int(comma_separated_line[0])
                                             + int(comma_separated_line[1]))]
    return counts


def get_modified_coverable_lines(patch_path, coverable_lines):
    coverable_modified_lines = defaultdict(dict)
    all_modified_lines = get_modified_lines(patch_path)
    for key, value in all_modified_lines.items():
        coverable_modified_lines[key]['statement_coverable_lines'] = \
            utils.intersection(coverable_lines[key]['statement_coverable_lines'], all_modified_lines[key])
        coverable_modified_lines[key]['checked_coverable_lines'] = \
            utils.intersection(coverable_lines[key]['checked_coverable_lines'], all_modified_lines[key])

    return coverable_modified_lines


def get_class_name(contains_class_name):
    for each_element in contains_class_name:
        if each_element.__contains__(".java"):
            return each_element.split("/java/")[1].replace("/", ".").replace(".java", "")

