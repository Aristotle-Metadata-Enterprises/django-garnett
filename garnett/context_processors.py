from .utils import get_languages, get_current_language


def languages(request):
    return {
        "garnett_languages": get_languages(),
        "garnett_current_language": get_current_language(),
    }
