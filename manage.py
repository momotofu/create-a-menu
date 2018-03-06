#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='sqlite:///test_restaurantmenu.db', debug='False', repository='migrations')
