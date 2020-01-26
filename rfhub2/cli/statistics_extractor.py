from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from typing import Callable, Dict, Iterable, List, Tuple
from xml.etree.ElementTree import Element, parse

from rfhub2.model import KeywordStatistics


@dataclass
class XmlKeyword:
    library: str
    name: str
    elapsed: int


@dataclass
class ElapsedStats:
    total_elapsed: int
    min_elapsed: int
    max_elapsed: int


StatsKey = Tuple[str, str]


def stats_key(keyword: XmlKeyword) -> StatsKey:
    return keyword.library, keyword.name


class StatisticsExtractor:
    def __init__(self, path: str):
        self.path: str = path
        self.source_time_format: str = "%Y%m%d %H:%M:%S.%f"
        self.destination_time_format: str = "%Y-%m-%d %H:%M:%S.%f"

    def compute_statistics(self) -> List[KeywordStatistics]:
        """
        Returns list of KeywordStatistics extracted from single output.xml file
        """
        keywords = self.parse_xml_keywords()
        return self.aggregate_statistics(keywords)

    def aggregate_statistics(
        self, keywords: List[XmlKeyword]
    ) -> List[KeywordStatistics]:
        """
        Returns list of KeywordStatistics grouped by library/keyword pair.
        """
        execution_time = self.get_execution_time()
        elapsed_stats = self.get_elapsed_stats(keywords)
        statistics = []
        for key, count in Counter(stats_key(keyword) for keyword in keywords).items():
            stats = elapsed_stats[key]
            statistics.append(
                KeywordStatistics(
                    collection=key[0],
                    keyword=key[1],
                    execution_time=execution_time,
                    times_used=count,
                    total_elapsed=stats.total_elapsed,
                    min_elapsed=stats.min_elapsed,
                    max_elapsed=stats.max_elapsed,
                )
            )
        return statistics

    @staticmethod
    def get_elapsed_stats(keywords: List[XmlKeyword]) -> Dict[StatsKey, ElapsedStats]:
        """
        Returns dict of keyword execution stats such as min, max and total elapsed time
        grouped by library/keyword pair.
        """
        result = {}
        for key, group in groupby(sorted(keywords, key=stats_key), stats_key):
            elapsed_times = [kw.elapsed for kw in group]
            result[key] = ElapsedStats(
                total_elapsed=sum(elapsed_times),
                min_elapsed=min(elapsed_times),
                max_elapsed=max(elapsed_times),
            )
        return result

    def parse_xml_keywords(self) -> List[XmlKeyword]:
        """
        Returns list of XmlKeyword objects containing keywords execution data.
        """
        xml_keywords = parse(self.path).findall(".//kw")
        return [
            XmlKeyword(
                xml_keyword.attrib.get("library"),
                xml_keyword.attrib.get("name"),
                self.calc_elapsed(xml_keyword),
            )
            for xml_keyword in xml_keywords
            if xml_keyword.attrib.get("library") is not None
        ]

    def datetime_from_attribute_agg(
        self, element: Element, attr: str, agg_func: Callable[[Iterable[str]], str]
    ) -> datetime:
        return datetime.strptime(
            agg_func(
                tag.attrib.get(attr) for tag in element.iter() if tag.tag == "status"
            ),
            self.source_time_format,
        )

    def calc_elapsed(self, element: Element) -> int:
        return int(
            1000
            * (
                self.datetime_from_attribute_agg(element, "endtime", max)
                - self.datetime_from_attribute_agg(element, "starttime", min)
            ).total_seconds()
        )

    def get_execution_time(self) -> str:
        """
        Returns execution time extracted form robot output.xml file.
        """
        return datetime.strftime(
            datetime.strptime(
                parse(self.path).getroot().attrib.get("generated"),
                self.source_time_format,
            ),
            self.destination_time_format,
        )
