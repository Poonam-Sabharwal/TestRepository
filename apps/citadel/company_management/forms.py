import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import DataRequired
from apps.common import utils


def validate_address_zip(form, field):
    zip = field.data
    # US zip code regex check
    m = re.search(r"^\d{5}(-{0,1}\d{4})?$", zip)
    if not m:
        # Canada zip code regex check
        m = re.search(r"^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d$", zip, flags=re.IGNORECASE)
        return True if m else False
    else:
        return True


class AddUpdateCompanyForm(FlaskForm):
    # hidden fields
    form_type = HiddenField("Form Type", id="form_type", name="form_type", default="add", validators=[DataRequired()])
    row_id = HiddenField("Row Id", id="row_id", name="row_id")
    address_state_option_value_for_update = HiddenField(
        "Address State Option Value For Update ",
        id="address_state_option_value_for_update",
        name="address_state_option_value_for_update",
    )

    # form hidden fields
    full_name = StringField("Full Name", id="full_name", name="full_name", validators=[DataRequired()])
    short_name = StringField("Short Name", id="short_name", name="short_name", validators=[DataRequired()])
    address_street_name_line_1 = StringField(
        "Street Name 1", id="address_street_name_line_1", name="address_street_name_line_1", validators=[DataRequired()]
    )
    address_street_name_line_2 = StringField(
        "Street Name 2", id="address_street_name_line_2", name="address_street_name_line_2"
    )
    address_city = StringField("City", id="address_city", name="address_city", validators=[DataRequired()])
    address_country = SelectField(
        "Country",
        id="address_country",
        name="address_country",
        choices=list(utils.countries_dict.items()),
        validators=[DataRequired()],
    )
    address_state = SelectField(
        "State",
        id="address_state",
        name="address_state",
        choices=[],
        validators=[DataRequired()],
    )
    address_zip = StringField(
        "Zip Code", id="address_zip", name="address_zip", validators=[DataRequired(), validate_address_zip]
    )
