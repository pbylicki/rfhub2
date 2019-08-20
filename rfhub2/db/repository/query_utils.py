def glob_to_sql(string: str) -> str:
    """Convert glob-like wildcards to SQL wildcards

    * becomes %
    ? becomes _
    % becomes \%
    \\ remains \\
    \* remains \*
    \? remains \?

    This also adds a leading and trailing %, unless the pattern begins with
    ^ or ends with $
    """

    # What's with the chr(1) and chr(2) nonsense? It's a trick to
    # hide \* and \? from the * and ? substitutions. This trick
    # depends on the substitutions being done in order.  chr(1)
    # and chr(2) were picked because I know those characters
    # almost certainly won't be in the input string
    table = (
        (r"\\", chr(1)),
        (r"\*", chr(2)),
        (r"\?", chr(3)),
        (r"%", r"\%"),
        (r"?", "_"),
        (r"*", "%"),
        (chr(1), r"\\"),
        (chr(2), r"\*"),
        (chr(3), r"\?"),
    )

    for (a, b) in table:
        string = string.replace(a, b)

    string = string[1:] if string.startswith("^") else "%" + string
    string = string[:-1] if string.endswith("$") else string + "%"

    return string
