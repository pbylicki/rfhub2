from collections import Counter
from datetime import datetime
from typing import Dict, List
from xml.etree import ElementTree as et


class StatisticsExtractor:
    def __init__(self, path: str):
        self.path: str = path
        self.source_time_format: str = "%Y%m%d %H:%M:%S.%f"
        self.destination_time_format: str = "%Y-%m-%d %H:%M:%S.%f"

    def compute_statistics(self) -> List[Dict]:
        """
        Returns list of dicst with aggregated statistics extracted from single output.xml file
        """
        keywords = self.parse_xml_keywords()
        return self.aggregate_statistics(keywords)

    def aggregate_statistics(self, keywords: List[Dict]) -> List[Dict]:
        """
        Returns list of dicts aggregated data grouped by library/keyword combination.
        """
        execution_time = self.get_execution_time()
        statistics = [
            {
                "collection": k[0],
                "keyword": k[1],
                "execution_time": execution_time,
                "times_used": v,
                "total_elapsed": 0,
                "min_elapsed": 2147483647,
                "max_elapsed": 0,
            }
            for k, v in Counter(
                (keyword["library"], keyword["name"]) for keyword in keywords
            ).items()
        ]
        return self.get_elapsed_times(keywords, statistics)

    @staticmethod
    def get_elapsed_times(keywords: List[Dict], statistics: List[Dict]) -> List[Dict]:
        """
        Returns list of dicts with data about execution times such as min, max and total elapsed time.
        """
        for stat in statistics:
            for keyword in keywords:
                if (
                    keyword["library"] == stat["collection"]
                    and keyword["name"] == stat["keyword"]
                ):
                    stat["total_elapsed"] += keyword["elapsed"]
                    stat["min_elapsed"] = min(stat["min_elapsed"], keyword["elapsed"])
                    stat["max_elapsed"] = max(stat["max_elapsed"], keyword["elapsed"])
        return statistics

    def parse_xml_keywords(self) -> List[Dict]:
        """
        Returns list of dicts containing keywords execution data.
        """
        xml_keywords = et.parse(self.path).findall(".//kw")
        return [
            {
                "library": xml_keyword.attrib.get("library"),
                "name": xml_keyword.attrib.get("name"),
                "elapsed": int(
                    1000
                    * (
                        datetime.strptime(
                            max(
                                tag.attrib.get("endtime")
                                for tag in xml_keyword.iter()
                                if tag.tag == "status"
                            ),
                            self.source_time_format,
                        )
                        - datetime.strptime(
                            min(
                                tag.attrib.get("starttime")
                                for tag in xml_keyword.iter()
                                if tag.tag == "status"
                            ),
                            self.source_time_format,
                        )
                    ).total_seconds()
                ),
            }
            for xml_keyword in xml_keywords
            if xml_keyword.attrib.get("library") is not None
        ]

    def get_execution_time(self) -> str:
        """
        Returns execution time extracted form robot output.xml file.
        """
        return datetime.strftime(
            datetime.strptime(
                et.parse(self.path).getroot().attrib.get("generated"),
                self.source_time_format,
            ),
            self.destination_time_format,
        )
