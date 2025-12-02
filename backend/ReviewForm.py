from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class ReviewForm(FlaskForm):
    item_id = HiddenField(validators=[Optional()])

    name = StringField(validators=[Optional(), Length(max=100)])
    seller = StringField(validators=[Optional(), Length(max=100)])
    p_details = TextAreaField(validators=[Optional(), Length(max=2000)])

    title = StringField(validators=[DataRequired(), Length(min=1, max=50)])
    r_details = TextAreaField(validators=[DataRequired(), Length(min=1, max=2000)])

    rating = IntegerField(validators=[DataRequired(), NumberRange(min=1, max=5)])
