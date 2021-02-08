from django import template
from garnett.utils import lang_param
from langcodes import Language

register = template.Library()


@register.simple_tag(takes_context=True)
def switch_page_language(context, language_code):
    # http://stackoverflow.com/questions/2047622/how-to-paginate-django-with-other-get-variables
    request = context["request"]
    dict_ = request.GET.copy()
    dict_[lang_param()] = language_code
    get_params = dict_.urlencode()
    return f"{request.path}?{get_params}"


@register.filter
def language_display(language, display_language=None):
    if type(language) is str:
        language = Language(language)
    if display_language is None:
        return language.display_name()
    return language.display_name(display_language)


@register.inclusion_tag("garnett/language_selector.html", takes_context=True)
def language_selector(context, selector):
    context.update({"selector": selector})
    return {
        "selector": selector,
        "request": context["request"],
        "garnett_languages": context["garnett_languages"],
        "garnett_current_language": context["garnett_current_language"],
    }
