from .utils import get_languages, get_current_language
from langcodes import Language


# This allows us to pass the Aristotle settings through to the final rendered page
def languages(request):

    languages = [
        Language.make(language=l)
        for l in get_languages()
    ]
    return {
        "garnett_languages": languages,
        "garnett_current_language": get_current_language()
    }
