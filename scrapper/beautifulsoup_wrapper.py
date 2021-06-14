from bs4 import BeautifulSoup

"""
Wraps the find and __getitem__ functions to avoid errors returns None when nothing is found
"""
class SoupWrapper:
    def __init__(self, wrapped_soup):
        self.wrapped_soup = wrapped_soup

    """
    Returns a Tag with text None if nothing is found
    """
    def find(self, *args, **kwargs):
        output = self.wrapped_soup.find(*args, **kwargs)
        # If find fails, return a Tag with None as its text
        if not output:
            output = BeautifulSoup('<b>None</b>', "html.parser").b

        if not isinstance(output, SoupWrapper):
            output = SoupWrapper(output)
        return output

    def find_all(self, *args, **kwargs):
        output = self.wrapped_soup.find_all(*args, **kwargs)
        for elem in output:
            elem = SoupWrapper(elem)
        return output

    """
    Returns the string None when an item is not found
    """
    def __getitem__(self, key):
        try:
            output = self.wrapped_soup[key]
        except KeyError:
            output = "None"
        return output

    def __getattr__(self, name):
        return getattr(self.wrapped_soup, name)
