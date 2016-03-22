import os
activate_this = '/path/to/your/virtualenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/var/www/html/VirtualScene')

from run import app as application
