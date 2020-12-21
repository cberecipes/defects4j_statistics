from os import path
import json
import csv
from collections import defaultdict


def get_statement_coverage(project_id, current_project_path, modified_classes):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "line_coverage.json"
    statement_coverage = read_json_file(file_path)
    updated_statement_coverage = {}
    for modified_class in modified_classes:
        try:
            updated_statement_coverage[modified_class] = statement_coverage[modified_class]
        except KeyError:
            error_text = "KeyError - get_statement_coverage - for the class {2}, in project - {1}, " \
                         "id - {0}".format(project_id, current_project_path.split("/")[-1], modified_class)
            print(error_text)

            updated_statement_coverage[modified_class] = {}

    return updated_statement_coverage


def get_modified_classes(project_id, current_project_path):
    file_path = current_project_path + "/modified_classes/" + str(project_id) + ".src"
    return read_file(file_path)


def get_checked_coverage(project_id, current_project_path, modified_classes):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "checked_coverage.json"
    checked_coverage = read_json_file(file_path)
    updated_checked_coverage = {}
    for modified_class in modified_classes:
        try:
            updated_checked_coverage[modified_class] = checked_coverage[modified_class]
        except KeyError:
            error_text = "KeyError - get_checked_coverage - for the class {2}, in project - {1}, " \
                         "id - {0}".format(project_id, current_project_path.split("/")[-1], modified_class)
            print(error_text)

            updated_checked_coverage[modified_class] = {}

    return updated_checked_coverage


def get_bug_detecting_tests(project_id, current_project_path):
    trigger_tests = []
    file_path = current_project_path + "/trigger_tests/" + str(project_id)
    for line in read_file(file_path):
        if line.strip().startswith("---"):
            trigger_tests.append(line.replace("-", "").strip())

    return trigger_tests


def get_coverable_line_numbers(project_id, current_project_path, modified_classes, for_which_coverage):
    """
    Returns, Number of lines that can be covered in total
    :param project_id:
    :param current_project_path:
    :param modified_classes:
    :param for_which_coverage:
    :return:
    """
    coverable_lines_json = get_coverable_lines(project_id, current_project_path, modified_classes)
    statement_coverable_lines = 0
    for modified_class in modified_classes:
        try:
            statement_coverable_lines = \
                statement_coverable_lines + len(coverable_lines_json[modified_class][for_which_coverage])
        except TypeError:
            error_text = "TypeError - get_coverable_line_numbers -  get_coverable_line_numbers - " \
                         "for the class {2}, project - {1}, id - {0}, type of coverage - {3}".\
                format(project_id, current_project_path.split("/")[-1], modified_class, for_which_coverage)

            print(error_text)
    return statement_coverable_lines


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def get_coverable_lines(project_id, current_project_path, modified_classes):
    required_coverage = {}
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "coverable_lines.json"
    all_class_data = read_json_file(file_path)
    for modified_class in modified_classes:
        try:
            required_coverage[modified_class] = all_class_data[modified_class]
        except KeyError:
            error_text = "KeyError - get_coverable_lines - for the class {2}, in project - {1}, " \
                         "id - {0}".format(project_id, current_project_path.split("/")[-1], modified_class)
            print(error_text)
            required_coverage[modified_class] = []

    return required_coverage


def get_class_name(contains_class_name):
    for each_element in contains_class_name:
        if each_element.__contains__(".java"):
            return each_element.split("/java/")[1].replace("/", ".").replace(".java", "")


def get_modified_lines(patch_path):
    counts = {}
    class_name = None
    for line in read_file(patch_path):
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
            intersection(coverable_lines[key]['statement_coverable_lines'], all_modified_lines[key])
        coverable_modified_lines[key]['checked_coverable_lines'] = \
            intersection(coverable_lines[key]['checked_coverable_lines'], all_modified_lines[key])

    return coverable_modified_lines


def compute_coverage_score(coverage, exclude_this, coverable_line_nr):
    score = {}
    for key, value in coverage.items():
        for key2, value2 in value.items():
            if key2 not in exclude_this:
                try:
                    score[key] = list(set(score[key] + value2))
                except KeyError:
                    score[key] = value2

    score_value = 0
    for key, value in score.items():
        score_value = score_value + len(value)
    try:
        return (score_value/coverable_line_nr)*100
    except ZeroDivisionError:
        print("Divide by zero error")
        return 0


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


def write_json_file(contents, file_path_to_save):
    with open(file_path_to_save, 'a') as result_file:
        result_file.write(json.dumps(contents))
    result_file.close()


def write_list_as_csv(list_as_csv, file_path_to_save):
    with open(file_path_to_save, 'a') as result_file:
        wr = csv.writer(result_file, dialect='excel')
        wr.writerows(list_as_csv)
    result_file.close()


