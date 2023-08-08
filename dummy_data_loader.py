import logging
import mongoengine as me
from mongoengine.queryset.visitor import Q

from apps.common import utils
from apps.models.company_model import AddressCountry, CompanyAddress, CompanyModel, ContactNumber, ContactNumberType

logging.basicConfig(level=logging.INFO)
me.connect(host="mongodb://127.0.0.1:27017/citadel-idp-db-test-1", alias="citadel_frontend_app")


def load_dummy_companies_data():
    for i in range(1, 300):
        company: CompanyModel = CompanyModel.objects(full_name="Full Name " + str(i)).first()
        if company is None:
            company_address = CompanyAddress(
                street_name_line_1="6952 CAMPOS AVE " + str(i),
                street_name_line_2="address line 2 - " + str(i),
                address_city="257 - " + str(i) + " Fireweed Ln",
                address_country=AddressCountry.US,
                address_state=utils.us_states_dict["AK"],
                address_zip="99901",
            )
            company = CompanyModel(
                full_name="Company Full Name " + str(i),
                short_name="Company Short " + str(i),
                address=company_address,
                contact_numbers=[
                    ContactNumber(number="+1-416-666-6666", type=ContactNumberType.MOBILE_1),
                    ContactNumber(number="+1-416-777-7777", type=ContactNumberType.MOBILE_2),
                ],
                is_active=True,
                is_deleted=False,
            )
            company.save()
            company.reload()
            logging.info("Successfully created dummy company with full_name %s", company.full_name)


if __name__ == "__main__":
    load_dummy_companies_data()
