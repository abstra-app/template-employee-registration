from abstra.ai import prompt
import abstra.workflows as aw

# get the data from workflow
register_dict = aw.get_data("register_info")
file_paths = aw.get_data("paths")


# set variables
(
    employee_name,
    employee_personal_email,
    employee_birth_date,
    employee_phone_number,
    employee_identification_number,
    employee_id_emitted_by,
    employee_taxpayer_id,
    employee_country,
    employee_address,
    employee_number_address,
    employee_complement_address,
    employee_district,
    employee_zip_code,
    employee_shirt_size,
    employee_bank_name,
    employee_bank_account_number,
    employee_bank_branch_code,
) = register_dict.values()


# using abstra.ai, check if the information provided on the forms matches with the picure uploaded
national_id_ans = prompt(
    ["The following picture is the front and back of the National ID of a person", open(file_paths["id_front_page"], 'rb'), open(file_paths["id_back_page"], 'rb')],
    instructions=[
        f'Identify the name of this person if you can and compare to this one: {employee_name}',
        f'Identify the birth date of this person if you can and compare to this one: {employee_birth_date}',
        f'Identify the identification number of this person if you can and compare to this one: {employee_identification_number}',
        f'Identify the taxpayer id of this person if you can and compare to this one: {employee_taxpayer_id}',
        f'Identify the home country of this person if you can and compare to this one: {employee_country}'
    ],
    format={
        "name": {"type":"boolean", "description":"Are the names equal ?"},
        "birth_date": {"type":"boolean", "description": "Are the birth dates equal ?"}, 
        "identification_number": {"type":"boolean", "description": "Are the id numbers equal ?"},
        "taxpayer_id": {"type":"boolean", "description": "Are the taxpayer ids equal ?"},
        "country": {"type":"boolean", "description": "Are the countries equal ?"}
    }
)

address_proof_ans = prompt(
    ["The following picture is the front and back of a address proof of a person", open(file_paths["address_proof"], 'rb')],
    instructions=[
        f'Identify the address of this person if you can and compare to this one: {employee_address}',
        f'Identify the address number of this person if you can and compare to this one: {employee_number_address}',
        f'Identify the district of this person if you can and compare to this one: {employee_district}',
        f'Identify the zip code of this person if you can and compare to this one: {employee_zip_code}',
    ],
    format={
        "address": {"type": "boolean", "description": "Are the addresses equal ?"},
        "number_address": {"type": "boolean", "description": "Are the number addresses equal ?"},
        "district":{"type": "boolean", "description": "Are the district equal ?"},
        "zip_code":{"type": "boolean", "description": "Are the zip code equal ?"},
    }
)

ai_check_dict = {}
ai_check_dict.update(national_id_ans)
ai_check_dict.update(address_proof_ans)

# sets boolean variable to thread that represents if passed on the ai test
if all(ai_check_dict.values()):
    aw.set_data("is_register_info_match", True)
else:
    aw.set_data("is_register_info_match", False)

# sets mismatches varible to thread
aw.set_data("mismatch_info", ai_check_dict)
