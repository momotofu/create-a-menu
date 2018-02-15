class HTML_Builder(self):
    """
    A class to simplify building an html string.
    """

    __init__(self):
        self.output = "<html><body>"

    def add_html(self, html):
        output += html

    def get_html(self):
        return output + "</body></html>"
