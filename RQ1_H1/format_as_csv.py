def format(content):
    result = [['project', 'statement_coverage_score', 'checked_coverage_score'],
              [content[0]['project_name'], content[0]['result']['statement_coverage_score'],
              content[0]['result']['checked_coverage_score']]]

    return result
