from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired

class PetForm(FlaskForm):
    name = StringField('Enter new pet name: ', validators=[DataRequired()])
    price = IntegerField('Enter price: ', validators=[DataRequired()])
    category = SelectField('Choose a category: ', choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Fish', 'Fish')], validators=[DataRequired()])
    submit = SubmitField('Submit')
    petId = HiddenField()


class OwnerForm(FlaskForm):
    name = StringField('Enter new owner name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')
    ownerId = HiddenField()


class RegisterForm(FlaskForm):
    ownerName = StringField('Enter owner name: ', validators=[DataRequired()])
    petName = StringField('Enter pet name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ModifyOwnershipForm(FlaskForm):
    ownerName = StringField('Enter new owner', validators=[DataRequired()])
    submit = SubmitField('Modify')
    petId = HiddenField()