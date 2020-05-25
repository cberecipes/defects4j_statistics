def format_contents(contents):
    result = [['Project', 'project_id', 'statement_buggy', 'statement_fixed', 'checked_buggy', 'checked_fixed']]
    for project_wise_results in contents:

        project_name = project_wise_results['project_name']
        for project_id_wise_results in project_wise_results['result']:
            tmp_result = [project_name, project_id_wise_results['project_id'],
                          project_id_wise_results['scores']['statement_coverage']['buggy'],
                          project_id_wise_results['scores']['statement_coverage']['fixed'],
                          project_id_wise_results['scores']['checked_coverage']['buggy'],
                          project_id_wise_results['scores']['checked_coverage']['fixed']]
            result.append(tmp_result)

    return result
