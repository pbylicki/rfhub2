from pathlib import Path
from progress.bar import IncrementalBar
from typing import List, Set, Tuple

from rfhub2.cli.api_client import Client
from .statistics_extractor import StatisticsExtractor
from rfhub2.model import KeywordStatistics, KeywordStatisticsList


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
        loaded_statistics = []
        progress_bar = IncrementalBar(
            "Sending statistics",
            max=len(execution_files),
            suffix="%(percent).1f%% - %(eta)ds, elapsed: %(elapsed)ds",
        )
        for execution_file in execution_files:
            statistics = StatisticsExtractor(execution_file).compute_statistics()
            loaded_statistics.append(self.add_statistics(statistics, execution_file))
            progress_bar.next()
        return (
            len([stat for stat in loaded_statistics if stat > 0]),
            sum(loaded_statistics),
        )

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

    def add_statistics(
        self, statistics: List[KeywordStatistics], execution_file: Path
    ) -> int:
        """
        Adds statistics from provided list to app.
        :param statistics: List of KeywordStatistics objects
        :param execution_file: Path to file from statistics where extracted
        :return: number of statistics sent to app
        """
        stats_req = self.client.add_statistics(KeywordStatisticsList.of(statistics))
        if stats_req[0] == 201:
            return len(statistics)
        elif stats_req[0] != 400:
            print(stats_req[1]["detail"])
        else:
            print(f"""Records already exist for file from {execution_file}""")
        return 0

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
            # what looks like robot generator tag, return false
            data = f.read(200)
            return "<robot generator=" in data.lower()
