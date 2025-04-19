from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    remember_me = BooleanField('로그인 상태 유지')
    submit = SubmitField('로그인')

class RegistrationForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired()])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    phone_number = StringField('전화번호', validators=[DataRequired()])
    account_number = StringField('계좌번호', validators=[Optional()])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('가입하기')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('이미 사용 중인 이름입니다.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('이미 사용 중인 이메일입니다.')

class LinkForm(FlaskForm):
    applicant_id = SelectField('신청자', coerce=int, validators=[DataRequired()])
    worker_id = SelectField('작업자', coerce=int, validators=[DataRequired()])
    applicant_name = StringField('신청자 이름', validators=[DataRequired()])
    applicant_phone = StringField('신청자 전화번호', validators=[DataRequired()])
    worker_name = StringField('작업자 이름', validators=[DataRequired()])
    worker_phone = StringField('작업자 전화번호', validators=[DataRequired()])
    password = StringField('링크 비밀번호', validators=[DataRequired()])
    is_active = BooleanField('활성화 상태', default=True)
    submit = SubmitField('링크 생성') 