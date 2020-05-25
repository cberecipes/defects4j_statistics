def format_contents(contents):
    result = [['Project', 'project_id',
               'ratio_statement_coverage',
               'ratio_checked_coverage',
               'score_statement_coverage',
               'score_checked_coverage']]

    for project_wise_results in contents:
        project_name = project_wise_results['project_name']
        for project_wise_result in project_wise_results['result']:
            tmp_result = [project_name,
                          project_wise_result['project_id'],
                          compute_ratio(len(project_wise_result['scores']['list_of_bug_detecting_tests']),
                                        len(project_wise_result['scores']['statement_covering_tests'])),
                          compute_ratio(len(project_wise_result['scores']['list_of_bug_detecting_tests']),
                                        len(project_wise_result['scores']['checked_covering_tests'])),
                          get_max_score(project_wise_result['scores']['statement_covering_tests']),
                          get_max_score(project_wise_result['scores']['checked_covering_tests'])
                          ]
            result.append(tmp_result)

    return result


def get_max_score(list_of_coverage_details):
    test_score = []
    for i_test in list_of_coverage_details:
        test_score.append(i_test['detailed_lines_covered']['bug_fix_code_covered'])

    return max(test_score) if len(test_score) > 0 else 0


def compute_ratio(bug_detecting_len, covering_len):
    if covering_len == 0:
        return covering_len
    return bug_detecting_len / covering_len
