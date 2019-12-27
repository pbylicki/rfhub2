from pathlib import Path
from typing import Dict, List, Set, Tuple

from .api_client import Client
from .statistics_extractor import StatisticsExtractor


class StatisticsImporter:
    def __init__(self, client: Client, paths: Tuple[Path, ...]) -> None:
        self.client = client
        self.paths = paths

    def import_data(self) -> Tuple[int, int]:
        """
        Wrapper for import_libraries and import_statistics to unify modules.
        :return: Number of libraries and keyword loaded
        """
        return self.import_statistics()

    def import_statistics(self) -> Tuple[int, int]:
        """
        Import keywords executions statistics such as min/max/total elapsed time,
        number of times used and execution timestamp.
        :return: Number of libraries and keyword loaded
        """
        execution_files = self.get_execution_files_paths()
        statistics = [
            stat
            for execution_file in execution_files
            for stat in StatisticsExtractor(execution_file).compute_statistics()
        ]
        return self.add_statistics(statistics)

    def get_execution_files_paths(self) -> Set[Path]:
        """
        Traverses all given paths and returns set with paths
        pointing to RFWK output.xml files to import to app.
        :return: Set of Paths object pointing to output.xml files to import
        """
        return {
            p
            for path in self.paths
            for p in Path(path).rglob("*.xml")
            if self._is_valid_execution_file(p)
        }

    def add_statistics(self, statistics: List[Dict]) -> Tuple[int, int]:
        """
        Adds statistics from provided list to app.
        :param statistics: List of statistics object
        :return: list of dictionaries with collection name and number of keywords.
        """
        collections, keywords = set(), set()
        for stat in statistics:
            stat_req = self.client.add_statistics(stat)
            if stat_req[0] == 201:
                collections.add(stat["collection"])
                keywords.add(".".join((stat["collection"], stat["keyword"])))
            elif stat_req[0] != 400:
                print(stat_req[1]["detail"])
                raise StopIteration
            else:
                print(
                    f"""Record already exists for provided collection: {stat["collection"]}, keyword: {stat[
                        "keyword"]} and execution_time: {stat["execution_time"]}"""
                )

        return len(collections), len(keywords)

    @staticmethod
    def _is_valid_execution_file(path: Path) -> bool:
        """
        Checks if file is xml file containing apropriate string.
        This is simplified approach to quick check file.
        :param path:
        :return:
        """
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            # read the first few lines; if we don't see
            # what looks like robot tag data, return false
            data = f.read(200)
            return "<robot generator=" in data.lower()
