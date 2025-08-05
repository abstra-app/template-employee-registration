from abstra.ai import prompt
from abstra.tasks import get_trigger_task, send_task
import os

# get the data from trigger task
task = get_trigger_task()
payload = task.get_payload()
register_dict = payload["register_info"]
file_paths = payload["paths"]

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

# verify files exist before processing
for file_type, file_path in file_paths.items():
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        # send mismatch if files are missing
        payload["mismatch_info"] = {"file_error": False}
        send_task("ai_mismatch", payload)
        task.complete()
        exit()

try:
    # using abstra.ai, check if the information provided on the forms matches with the picture uploaded
    with open(file_paths["id_front_page"], 'rb') as front_file, \
         open(file_paths["id_back_page"], 'rb') as back_file:
        
        national_id_ans = prompt(
            ["The following pictures are the front and back of the National ID of a person", front_file, back_file],
            instructions=[
                f'Identify the name of this person if you can and compare to this one: {employee_name}',
                f'Identify the birth date of this person if you can and compare to this one: {employee_birth_date}',
                f'Identify the identification number of this person if you can and compare to this one: {employee_identification_number}',
                f'Identify the taxpayer id of this person if you can and compare to this one: {employee_taxpayer_id}',
                f'Identify the home country of this person if you can and compare to this one: {employee_country}'
            ],
            format={
                "name": {"type": "boolean", "description": "Are the names equal?"},
                "birth_date": {"type": "boolean", "description": "Are the birth dates equal?"},
                "identification_number": {"type": "boolean", "description": "Are the id numbers equal?"},
                "taxpayer_id": {"type": "boolean", "description": "Are the taxpayer ids equal?"},
                "country": {"type": "boolean", "description": "Are the countries equal?"}
            }
        )

    with open(file_paths["address_proof"], 'rb') as address_file:
        address_proof_ans = prompt(
            ["The following picture is a proof of address document of a person", address_file],
            instructions=[
                f'Identify the address of this person if you can and compare to this one: {employee_address}',
                f'Identify the address number of this person if you can and compare to this one: {employee_number_address}',
                f'Identify the district of this person if you can and compare to this one: {employee_district}',
                f'Identify the zip code of this person if you can and compare to this one: {employee_zip_code}',
            ],
            format={
                "address": {"type": "boolean", "description": "Are the addresses equal?"},
                "number_address": {"type": "boolean", "description": "Are the number addresses equal?"},
                "district": {"type": "boolean", "description": "Are the districts equal?"},
                "zip_code": {"type": "boolean", "description": "Are the zip codes equal?"},
            }
        )

    ai_check_dict = {}
    ai_check_dict.update(national_id_ans)
    ai_check_dict.update(address_proof_ans)

    # sets boolean variable to thread that represents if passed on the ai test
    if all(ai_check_dict.values()):
        # sends matches to the task
        send_task("ai_match", payload)
    else:
        # sets mismatches to the task
        payload["mismatch_info"] = ai_check_dict
        send_task("ai_mismatch", payload)

except Exception as e:
    print(f"ERROR in AI processing: {e}")
    # if AI fails, assume mismatch and let manual verification handle it
    payload["mismatch_info"] = {
        "ai_error": False,
        "name": False,
        "birth_date": False,
        "identification_number": False,
        "taxpayer_id": False,
        "country": False,
        "address": False,
        "number_address": False,
        "district": False,
        "zip_code": False
    }
    send_task("ai_mismatch", payload)

task.complete()