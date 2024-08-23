from abstra.forms import *
from abstra.common import get_persistent_dir
from datetime import datetime
import abstra.workflows as aw
import dotenv 
import os

aw.set_title("employee_registration_workflow")

assignee = os.getenv("HIRING_RESPONSIBLE_EMAIL")

# setting directory configs to save the files uploaded
destination_dir = get_persistent_dir() / 'register_files'
destination_dir.mkdir(parents=True, exist_ok=True)

# funtion to preprocess date format
def preprocessing_date(date):
    if date != None:
        date = datetime(date.year, date.month, date.day)
        date = date.replace(tzinfo=None)
        date = date.strftime("%Y/%m/%d")
    return date


# personal info page
member_page = (
    Page()
    .display("Personal Data", size="large")
    .read("Full name", key="name")
    .read_email("Email", key="personal_email")
    .read_date("Birth Date", key="birth_date")
    .read_phone("Phone Number", key="phone_number")
    .read("National ID number (e.g. RG in Brazil)", key="identification_number")
    .read("ID number issued by", key="id_emitted_by")
    .read("Individual Taxpayer Registration (e.g. CPF in Brazil)", key="taxpayer_id")
    .read("Shirt size", placeholder="M", key="shirt_size")
)

# address info page
address_page = (
    Page()
    .display("Address Data", size="large")
    .read("Country", key="country")
    .read("Address (without number)", key="address")
    .read("Address number", key="number_address")
    .read("Address complement", required=False, key="complement_address")
    .read("District", key="district")
    .read("Zip code", key="zip_code")
)

# files upload page 
files_upload_page = (
    Page()
    .read_file("Upload a picture of your National ID document's front (.PNG format)", accepted_formats=[".png"])
    .read_file("Upload a picture of your National ID document's back (.PNG format)", accepted_formats=[".png"])
    .read_file("Upload a picture of a recent proof of address (.PNG format)", accepted_formats=[".png"])
)

# bank account info page 
bank_info_page = (
    Page()
    .display("Bank Account Data", size="large")
    .display(
        "Please enter your bank account data. If you're subscribed to a company, please enter the company's bank account data."
    )
    .read("Bank name", placeholder="Goldman Sachs", key="bank_name")
    .read("Bank account number", placeholder="0000000-0" , key="bank_account_number")
    .read("Bank branch code", placeholder="0001", key="bank_branch_code")
)

# doing the forms in step format
step_run = run_steps(
    [member_page, address_page, files_upload_page, bank_info_page]
)

personal_info = step_run[0]
address_info = step_run[1]
files_uploaded = step_run[2]
bank_info = step_run[3]

# assigning the answers to variables
(
    name,
    personal_email,
    birth_date,
    phone_number,
    identification_number,
    id_emitted_by,
    taxpayer_id,
    shirt_size,
) = personal_info.values()

(
    country,
    address,
    number_address,
    complement_address,
    district,
    zip_code
) = address_info.values()

(
    id_front_page,
    id_back_page,
    address_proof
) = files_uploaded.values()

(
    bank_name,
    bank_account_number,
    bank_branch_code
) = bank_info.values()

birth_date = preprocessing_date(birth_date)
phone_number = phone_number.raw
taxpayer_id = taxpayer_id.replace(".", "").replace("-", "")

# saving files on persistent dir and using person's identification number
path_front_page = f"{identification_number}_id_front_page.png"
path_back_page = f"{identification_number}_id_back_page.png"
path_address_proof = f"{identification_number}_address_proof.png"

destination_dir.joinpath(path_front_page).write_bytes(id_front_page.file.read())
destination_dir.joinpath(path_back_page).write_bytes(id_back_page.file.read())
destination_dir.joinpath(path_address_proof).write_bytes(address_proof.file.read())

# forwarding data to the next stage
aw.set_data(
    "assignee",
    [assignee]
)
#example@example.com
aw.set_data(
    "register_info",
    {
        "name": name,
        "personal_email": personal_email,
        "birth_date": birth_date,
        "phone_number": phone_number,
        "identification_number": identification_number,
        "id_emitted_by": id_emitted_by,
        "taxpayer_id": taxpayer_id,
        "country": country,
        "address": address,
        "number_address": number_address,
        "complement_address": complement_address,
        "district": district,
        "zip_code": zip_code,
        "shirt_size": shirt_size,
        "bank_name": bank_name,
        "bank_account_number": bank_account_number,
        "bank_branch_code": bank_branch_code,
    }
)

aw.set_data(
    "paths",
    {
        "id_front_page": f"{destination_dir.joinpath(path_front_page)}",
        "id_back_page": f"{destination_dir.joinpath(path_back_page)}",
        "address_proof": f"{destination_dir.joinpath(path_address_proof)}"
    }
)

aw.set_data(
    "employee_approval_email",
    personal_email
)
