from collections import defaultdict
from datetime import datetime
from typing import List

from robot.api import ExecutionResult, ResultVisitor

from rfhub2.model import KeywordStatistics


class KeywordsCollector(ResultVisitor):
    def __init__(self):
        self.statistics = defaultdict(list)

    def visit_keyword(self, keyword):
        keyword.body.visit(self)
        self.statistics[keyword.name].append(keyword)


def parse_time(value):
    return datetime.strftime(datetime.strptime(value, "%Y%m%d %H:%M:%S.%f"), "%Y-%m-%d %H:%M:%S.%f")


def compute_statistics(path: str) -> List[KeywordStatistics]:
    """ Returns list of KeywordsStatistics extracted from single output.xml file """
    result = ExecutionResult(path)
    execution_time = parse_time(result.suite.starttime)
    visitor = KeywordsCollector()
    result.visit(visitor)
    statistics = []
    for name, keywords in visitor.statistics.items():
        statistics.append(KeywordStatistics(
            collection=keywords[0].libname if keywords[0].libname is not None else '',
            keyword=keywords[0].kwname,
            execution_time=execution_time,
            times_used=len(keywords),
            total_elapsed=sum(keyword.elapsedtime for keyword in keywords),
            min_elapsed=min(keyword.elapsedtime for keyword in keywords),
            max_elapsed=max(keyword.elapsedtime for keyword in keywords)
        ))
    return statistics
