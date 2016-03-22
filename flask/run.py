from app import app
if __name__=='__main__':
        app.run(debug = False)

import sys
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')
