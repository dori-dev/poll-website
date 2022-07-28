from django import template

register = template.Library()


def plural(number: int):
    if not isinstance(number, int):
        return None
    if number in (0, 1):
        return ''
    return 's'


register.filter('plural', plural)

