def format_contents(contents):
    result = [['project', 'project_id', 'statement_buggy', 'statement_fixed', 'statement_coverage_increase',
               'checked_buggy', 'checked_fixed', 'checked_coverage_increase',
               'mutation_buggy', 'mutation_fixed', 'mutation_coverage_increase']]
    for project_wise_results in contents:

        project_name = project_wise_results['project_name']
        for project_id_wise_results in project_wise_results['result']:
            tmp_result = [project_name, project_id_wise_results['project_id'],
                          project_id_wise_results['scores']['statement_coverage']['buggy'],
                          project_id_wise_results['scores']['statement_coverage']['fixed'],
                          compute_percent_increase(project_id_wise_results['scores']['statement_coverage']['buggy'],
                                                   project_id_wise_results['scores']['statement_coverage']['fixed']),
                          project_id_wise_results['scores']['checked_coverage']['buggy'],
                          project_id_wise_results['scores']['checked_coverage']['fixed'],
                          compute_percent_increase(project_id_wise_results['scores']['checked_coverage']['buggy'],
                                                   project_id_wise_results['scores']['checked_coverage']['fixed']),

                          project_id_wise_results['scores']['mutation_score']['buggy'],
                          project_id_wise_results['scores']['mutation_score']['fixed'],
                          compute_percent_increase(project_id_wise_results['scores']['mutation_score']['buggy'],
                                                   project_id_wise_results['scores']['mutation_score']['fixed'])
                          ]
            result.append(tmp_result)

    return result


def compute_percent_increase(old_value, new_value):
        try:
            return ((new_value - old_value) / old_value) * 100
        except ZeroDivisionError:
            print("ZeroDivisionError - while computing percent of increase")
            return 0
