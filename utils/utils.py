from os import path
import json


def get_statement_coverage(project_id, current_project_path, modified_classes):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "line_coverage.json"
    statement_coverage = read_json_file(file_path)
    updated_statement_coverage = {}
    for modified_class in modified_classes:
        updated_statement_coverage[modified_class] = statement_coverage[modified_class]

    return updated_statement_coverage


def get_modified_classes(project_id, current_project_path):
    file_path = current_project_path + "/modified_classes/" + str(project_id) + ".src"
    return read_file(file_path)


def get_checked_coverage(project_id, current_project_path, modified_classes):
    file_path = current_project_path + "/trace_files/" + str(project_id) + "f/" + "checked_coverage.json"
    checked_coverage = read_json_file(file_path)
    updated_checked_coverage = {}
    for modified_class in modified_classes:
        updated_checked_coverage[modified_class] = checked_coverage[modified_class]

    return updated_checked_coverage


def get_bug_detecting_tests(project_id, current_project_path):
    trigger_tests = []
    file_path = current_project_path + "/trigger_tests/" + str(project_id)
    for line in read_file(file_path):
        if line.strip().startswith("---"):
            trigger_tests.append(line.replace("-", "").strip())

    return trigger_tests


def read_file(file_path):
    if not path.exists(file_path):
        # print("File not exist!" + file_path)
        file_contents = []
    else:
        f = open(file_path, encoding="ISO-8859-1")
        file_contents = f.read().splitlines()
        f.close()
    return file_contents


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
            pass

    return required_coverage


def read_json_file(file_path):
    if not path.exists(file_path):
        # print("File not exist!" + file_path)
        output = {}
    else:
        with open(file_path, encoding="ISO-8859-1") as fp:
            output = json.load(fp)

    return output
