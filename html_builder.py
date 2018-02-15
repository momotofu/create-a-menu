class HTML_Builder():
    """
    A class to simplify building an html string.
    """

    def __init__(self):
        self.output = "<html><body>"

    def add_html(self, html):
        self.output += html

    def get_html(self):
        return self.output + "</body></html>"
