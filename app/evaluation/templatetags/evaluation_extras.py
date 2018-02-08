from django import template
from jsonpath_rw import parse

register = template.Library()


@register.filter
def get_jsonpath(obj: dict, jsonpath):
    """
    Gets a value from a dictionary based on a jsonpath. It will only return
    one result, and if a key does not exist it will return an empty string as
    template tags should not raise errors.

    :param obj: The dictionary to query
    :param jsonpath: The path to the object (singular)
    :return: The most relevant object in the dictionary
    """
    try:
        expr = parse(jsonpath)
        return expr.find(obj)[0].value
    except (AttributeError, IndexError):
        return ''
