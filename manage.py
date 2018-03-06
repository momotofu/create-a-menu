#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(repository='migrations', url='sqlite:///restaurantmenu.db', debug='False')
