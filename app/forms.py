from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class Submission(Form):
	submit = SubmitField("Submit")

class LoginForm(Form):
    """Form class for user login."""
    name = TextField('Username', validators=[DataRequired()])
   # remember_me = BooleanField('Remember me', default = False)