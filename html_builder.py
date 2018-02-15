class HTML_Builder(self):
    output = "<html><body>"

    def add_html(self, html):
        output += html

    def get_html(self):
        return output + "</body></html>"
