from abstra.forms import (
    TextInput, TextareaInput, MultipleChoiceInput, TextOutput, FileOutput, Button, run
)
from abstra.tasks import get_tasks, send_task
from abstra.tables import insert

# replace "_" by " " on the key and capitalize it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()

# get the data from the task payload
tasks = get_tasks()
for task in tasks:
    payload = task.get_payload()

    register_dict = payload["register_info"]
    contract_dict = payload["contract_path"]
    contract_data_dict = payload["contract_data"]

    contract_filename = contract_dict["contract_filename"]
    employee_name = register_dict["name"]
    contract_filepath = contract_dict["contract_filepath"]

    def contract_approval_page(state):
        return [
            TextOutput(f"Document Approval - {contract_filename}", size="large"),
            TextOutput(f'Please read the "{contract_filename}" document related to the hiring of {employee_name} and approve/reject it'),
            FileOutput(contract_filepath, download_text="Click here to download the document"),
            Button("Approve", key="approve_action"),
            Button("Reject", key="reject_action")
        ]

    def contract_rejection_page(state):
        widgets = []
        
        if state.get("reject_action"):
            widgets.extend([
                MultipleChoiceInput(
                    "Does the contract have any error or a clause you disagree with?",
                    ["Yes", "No"],
                    key="is_contract_error"
                )
            ])
            
            if state.get("is_contract_error") == "Yes":
                widgets.extend([
                    TextareaInput(
                        "Comments",
                        required=False,
                        placeholder="Put here your comments about the problems",
                        key="comments"
                    ),
                    MultipleChoiceInput(
                        "Does the contract have error regarding your information?",
                        ["Yes", "No"],
                        key="is_data_error"
                    )
                ])
                
                if state.get("is_data_error") == "Yes":
                    # Add input fields for data correction
                    data_dict = contract_data_dict if contract_data_dict else register_dict
                    for key in data_dict.keys():
                        widgets.append(
                            TextInput(
                                f"{transform_to_label(key)}:",
                                key=key,
                                initial_value=str(data_dict[key]) if data_dict[key] is not None else ""
                            )
                        )
        
        return widgets

    # execute form pages
    result = run([contract_approval_page, contract_rejection_page])

    if result.get("reject_action"):
        payload["approval_status"] = "not_approved"
        data_error_log = {}
        
        if result.get("is_data_error") == "Yes":
            data_dict = contract_data_dict if contract_data_dict else register_dict
            for key in data_dict.keys():
                if key in result and data_dict[key] != result[key]:
                    data_error_log[key] = [data_dict[key], result[key]]

        payload["data_error_log"] = data_error_log
        payload["comments"] = result.get("comments", "")
    else:
        payload["approval_status"] = "approved"
        insert("employee_register", register_dict)

    approval_status = payload["approval_status"]
    send_task(approval_status, payload)
    task.complete()