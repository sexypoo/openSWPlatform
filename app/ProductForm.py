from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class ProductForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(max=100)])
    
    category = StringField(validators=[DataRequired()])
    price = IntegerField(validators=[DataRequired(),NumberRange(min=0)])
    quantity = IntegerField(default=1, validators=[Optional(),NumberRange(min=1)])
    method = SelectMultipleField(validators=[DataRequired()], choices=[
                                   ('대면 직거래 가능', '대면 직거래 가능'),
                                   ('비대면 직거래 가능', '비대면 직거래 가능'),
                                   ('택배 거래 가능', '택배 거래 가능'),
                                   ('거래 방법 개인 문의 요함', '거래 방법 개인 문의 요함')
                               ])
    details = TextAreaField(validators=[DataRequired(), Length(max=5000)])
    tag = StringField(validators=[Optional()])
    file = FileField( validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], '이미지 파일만 업로드 가능합니다.')
    ])