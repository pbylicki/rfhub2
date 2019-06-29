from typing import Optional, Tuple

IN_TOKEN = " in:"
NAME_TOKEN = "name:"
WILDCARD = "*"


class SearchParams:

    DEFAULT = (WILDCARD, None, True)

    def __init__(self, pattern: str = WILDCARD) -> None:
        if not pattern or pattern == WILDCARD:
            result = self.DEFAULT
        else:
            result = self.extract_params(pattern)
        self.raw_pattern = pattern
        self.pattern, self.collection_name, self.use_doc = result

    @staticmethod
    def extract_params(raw_pattern: str) -> Tuple[str, Optional[str], bool]:
        pattern, collection_name, use_doc = raw_pattern.strip().lower(), None, True
        if pattern.startswith(NAME_TOKEN):
            pattern = pattern[5:].strip()
            use_doc = False
        query, sep, col_name = pattern.partition(IN_TOKEN)
        if sep == IN_TOKEN and col_name:
            pattern = query.strip()
            collection_name = col_name.strip()
        return pattern, collection_name, use_doc
