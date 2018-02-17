from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
import query_db
from html_builder import HTML_Builder as HB

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += """<form method='POST'
                action='/'><h2>What would you like me to say?</h2><input
                name='message'><input type='submit'
                value='Submit'></form>"""

                output += "</body></html>"

                self.wfile.write(bytes(output.encode()))
                print(output)
                return

            if self.path.endswith('restaurants'):
                # send the client a response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = query_db.get_all(session, Restaurant)

                # start an output object
                output = HB()

                # add link to create a new restaurant
                output.add_html("""
                    <nav>
                        <a href='/restaurants/new'>Add a new restaurant</a>
                    </nav>
                    """
                    )

                # populate output with restaurant names
                for restaurant in restaurants:
                    output.add_html("""
                        <h3> %s </h3>
                        <div>
                            <a href='/%s/edit'>edit</a>
                            <a href='/%s/delete'>delete</a>
                        </div>
                        """ % (restaurant.name, restaurant.id, restaurant.id)
                        )

                # send response to client
                self.wfile.write(output.get_html().encode())
                return

            if self.path.endswith('/delete'):
                # send the client a response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                test = int(self.path.replace('/delete', '')[1:])
                restaurant = query_db.get_one(
                    session,
                    Restaurant,
                    test
                    )

                # start an output object
                output = HB()

                # add link to create a new restaurant
                output.add_html("""
                    <nav>
                        <a href='/restaurants'>go to restaurants</a>
                    </nav>
                    <h1>Are you sure you want to delete %s </h1>
                    <form method='POST'>
                        <input type='submit' name="should_delete" value='Yes'>
                        <input type='submit' name="should_delete" value='No'>
                    </form>
                    """ % restaurant.name
                    )

                # send response to client
                self.wfile.write(output.get_html().encode())
                return

            if self.path.endswith('/edit'):
                # send the client a response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                test = int(self.path.replace('/edit', '')[1:])
                restaurant = query_db.get_one(
                    session,
                    Restaurant,
                    test
                    )

                # start an output object
                output = HB()

                # add link to create a new restaurant
                output.add_html("""
                    <nav>
                        <a href='/restaurants'>go to restaurants</a>
                    </nav>
                    <h1> edit the name of your restaurant </h1>
                    <form method='POST'>
                        <label> Restaurant name:
                            <input name='name' placeholder='%s'>
                        </label>
                        <input type='submit' value='SUBMIT'>
                    </form>
                    """ % restaurant.name
                    )

                # send response to client
                self.wfile.write(output.get_html().encode())
                return

            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                # start an output object
                output = HB()

                # add link to create a new restaurant
                output.add_html("""
                    <nav>
                        <a href='/restaurants'>back to restaurants</a>
                    </nav>
                    """
                    )

                # populate output with submission form
                output.add_html("""
                    <h1> Create a new restaurant </h1>
                    <form method='POST' action='/restaurants/new'>
                        <label>
                            <input name='name' type='text'>
                        </label>
                        <input type='submit' value='SUBMIT'>
                    </form>
                    """
                    )

                # send response to client
                self.wfile.write(output.get_html().encode())
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)


    def do_POST(self):
        try:
            if self.path.endswith('/delete'):
                # send the client a response
                self.send_response(303)
                self.send_header('content-type', 'text/html')

                # get parameters
                length = int(self.headers.get('content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)

                if 'should_delete' in params:
                    should_delete = params['should_delete'][0].lower()
                else:
                    self.send_header('Location', '/%s/delete' % uid)
                    self.end_headers()
                    return

                if should_delete == 'yes':
                    try:
                        uid = int(self.path.replace('/delete', '')[1:])
                        restaurant = query_db.get_one(
                            session,
                            Restaurant,
                            uid
                            )
                        query_db.delete(session, restaurant)
                        session.commit()

                        self.end_headers()

                        # start output
                        output = HB()
                        output.add_html("""
                            <nav>
                                <a href="/restaurants">Back to restaurants</a>
                            </nav>
                            <h1> %s was successfuly deleted </h1>
                            """ % restaurant.name
                            )

                        # send a response to the client
                        self.wfile.write(output.get_html().encode())
                        return

                    except:
                        session.rollback()
                        self.send_response(500)
                        self.send_header('content-type', 'text/html')
                        self.end_headers()
                        raise
                        return

                else:
                    self.send_header('location', '/restaurants')
                    self.end_headers()
                    return

            if self.path.endswith('/edit'):
                # send the client a response
                self.send_response(303)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                # get parameters
                length = int(self.headers.get('content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)

                uid = int(self.path.replace('/edit', '')[1:])

                if 'name' in params:
                    name = params['name'][0]
                else:
                    self.send_header('Location', '/%s/edit' % uid)
                    self.end_headers()
                    return

                restaurant = query_db.get_one(
                    session,
                    Restaurant,
                    uid
                    )
                restaurant.name = name

                try:
                    query_db.update(session, restaurant)
                    session.commit()

                    # start an output object
                    output = HB()

                    # add link to create a new restaurant
                    output.add_html("""
                        <nav>
                            <a href='/restaurants'>go to restaurants</a>
                        </nav>
                        <h1>Successfuly edited % s</h1>
                        """ % restaurant.name
                        )

                    # send response to client
                    self.wfile.write(output.get_html().encode())
                    return

                except:
                    session.rollback()
                    self.send_response(500)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    raise
                    return

            if self.path.endswith('/restaurants/new'):
                self.send_response(303)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                length = int(self.headers.get('content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)

                if 'name' in params:
                    name = params['name'][0]
                else:
                    self.send_header('Location', '/restaurants/news')
                    self.end_headers()
                    return

                output = HB()

                try:
                    new_restaurant = Restaurant(name=name)
                    session.add(new_restaurant)
                    session.commit()

                    # populate output with success message
                    output.add_html("""
                        <h1> Successfully created % s </h1>
                        <a href='/restaurants'>Back to restaurants</a>
                        """ % new_restaurant.name
                        )

                    # send response to client
                    self.wfile.write(output.get_html().encode())
                    return

                except:
                    session.rollback()

                    output.add_html("""
                        <h1>Failed to create new restaurant</h1>
                        <a href='/restaurants/new'>Try again</a>
                        """
                        )

                    # send response to client
                    self.wfile.write(output.get_html().encode())
                    return

        except IOError:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        # A python defined exception when the user
        # presses control-C on their keyboard
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
