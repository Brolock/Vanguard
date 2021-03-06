from bs4 import BeautifulSoup

'''
Returns a newly created BeautifulSoup wrapped in SoupWrapper
'''
def WrappedSoup(*args, **kwargs):
    return SoupWrapper(BeautifulSoup(*args, **kwargs))

'''
Wraps the find and __getitem__ functions to avoid errors and exceptions
'''
class SoupWrapper:
    def __init__(self, wrapped_soup):
        self.wrapped_soup = wrapped_soup

    '''
    Returns a Tag with text None if nothing is found
    '''
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
        result = []
        for elem in output:
            result.append(SoupWrapper(elem))
        return result

    '''
    Returns the string None when an item is not found
    '''
    def __getitem__(self, key):
        try:
            output = self.wrapped_soup[key]
        except KeyError:
            output = "None"
        return output

    def __getattr__(self, name):
        return getattr(self.wrapped_soup, name)
