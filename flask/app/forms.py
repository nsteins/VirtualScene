from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class SearchForm(Form):
    name = StringField('album name',validators=[DataRequired()])
