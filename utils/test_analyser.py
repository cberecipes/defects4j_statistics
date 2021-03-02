def find_test_nature(exception_trace_file_path, tests):
    test_details = dict()
    for test in tests:
        test_details.update(search_string_in_file(exception_trace_file_path, test))

    return test_details


def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
    return False


def search_string_in_file(file_name, string_to_search):
    line_number = 0
    read_obj = open(file_name, 'r').readlines()
    try:
        for line in read_obj:
            line_number += 1
            exact_match_line = line.replace("-", "").strip()
            if exact_match_line == string_to_search:
                return {string_to_search: type_of_failure(read_obj[line_number])}
    except IndexError:
        print("exception -> " + string_to_search)

    return {}


def type_of_failure(failure_trace):
    if failure_trace.__contains__("junit"):
        return "green"
    elif failure_trace.__contains__("java"):
        return "red"
    else:
        # Application raised exception
        return "red"


def determine_test_nature(dict_of_test_nature, list_of_tests_to_find):
    set_of_nature = set()
    for test in list_of_tests_to_find:
        set_of_nature.update({dict_of_test_nature[test]})

    if len(set_of_nature) == 1:
        return set_of_nature.pop()
    else:
        return "orange"
