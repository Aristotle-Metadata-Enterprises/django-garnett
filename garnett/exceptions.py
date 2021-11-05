class LanguageStructureError(Exception):
    """
    A language structure isn't a dictionary
    """

    pass


class LanguageContentError(Exception):
    """
    A language in a language dictionary has non-string content
    """

    pass


class LanguageSelectionError(Exception):
    """
    A language in a language dictionary has non-string content
    """

    pass
