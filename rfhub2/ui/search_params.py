from typing import Optional, Tuple

IN_TOKEN = " in:"
NAME_TOKEN = "name:"
TAG_TOKEN = "tags:"
WILDCARD = "*"


class SearchParams:

    DEFAULT = (WILDCARD, None, True, False)

    def __init__(self, pattern: str = WILDCARD) -> None:
        if not pattern or pattern == WILDCARD:
            result = self.DEFAULT
        else:
            result = self.extract_params(pattern)
        self.raw_pattern = pattern
        self.pattern, self.collection_name, self.use_doc, self.use_tags = result

    @staticmethod
    def extract_params(raw_pattern: str) -> Tuple[str, Optional[str], bool, bool]:
        pattern, collection_name, use_doc, use_tags = (
            raw_pattern.strip().lower(),
            None,
            True,
            False,
        )
        if pattern.startswith(NAME_TOKEN):
            pattern = pattern[5:].strip()
            use_doc = False
        query, sep, col_name = pattern.partition(IN_TOKEN)
        if sep == IN_TOKEN and col_name:
            pattern = query.strip()
            collection_name = col_name.strip()
        query, sep, tag_name = pattern.partition(TAG_TOKEN)
        if sep == TAG_TOKEN:
            pattern = tag_name.strip()
            use_doc, use_tags = False, True
        return pattern, collection_name, use_doc, use_tags
