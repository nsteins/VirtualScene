from app import app
app.run(debug=True)

import sys
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')
