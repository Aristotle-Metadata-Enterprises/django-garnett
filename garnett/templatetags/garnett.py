from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def switch_page_language(context, language_code):
    # http://stackoverflow.com/questions/2047622/how-to-paginate-django-with-other-get-variables
    request = context['request']
    dict_ = request.GET.copy()
    dict_['glang'] = language_code
    get_params = dict_.urlencode()
    return f"{request.path}?{get_params}"


@register.filter
def language_display(language, display_language=None):
    if display_language is None:
        return language.display_name()    
    return language.display_name(display_language)
