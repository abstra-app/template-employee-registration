from abstra.forms import (
    FileInput, MultipleChoiceInput, TextOutput, MarkdownOutput, FileOutput, run
)
from abstra.tasks import get_tasks, send_task

# replace "_" by " " on the key and capitalize it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()

# get variables from task payload
tasks = get_tasks()

for task in tasks:
    payload = task.get_payload()

    comments = payload["comments"]
    contract_dict = payload["contract_path"]
    register_dict = payload["register_info"]
    data_error_log = payload["data_error_log"]
    contract_data_dict = payload["contract_data"]

    def rejection_review_page(state):
        widgets = [
            MarkdownOutput("# Rejection Details and Contract Review"),
            MarkdownOutput("**The contract has been rejected.**")
        ]

        if comments != "":
            widgets.extend([
                MarkdownOutput("**The following comments were made about it:**"),
                TextOutput(f"'{comments}'")
            ])

        if data_error_log:
            widgets.append(
                MarkdownOutput("**The following data was considered incorrect and changed by the employee (Old value -> New value):**")
            )
            
            for key in data_error_log.keys():
                widgets.append(
                    TextOutput(f"{transform_to_label(key)}: {data_error_log[key][0]} -> {data_error_log[key][1]}")
                )
            
            widgets.append(
                MultipleChoiceInput(
                    "Do you approve the changes?",
                    ["Yes", "No"],
                    key="approve_changes"
                )
            )

        widgets.extend([
            MarkdownOutput("**Please review the contract below:**"),
            FileOutput(contract_dict["contract_filepath"], download_text="Click here to download the contract"),
            MultipleChoiceInput(
                "Do you want to give up on the hiring?",
                ["Yes", "No"],
                key="give_hiring"
            )
        ])

        if state.get("give_hiring") == "No":
            widgets.append(
                FileInput(
                    "Upload the adjusted contract",
                    key="corrected_contract",
                    accepted_formats=[".docx"],
                    required=False
                )
            )

        return widgets

    result = run([rejection_review_page])

    if result.get("corrected_contract") is not None:
        open(contract_dict["contract_filepath"], "wb").write(result["corrected_contract"].file.read())

    payload["give_hiring"] = (result["give_hiring"] == "Yes")

    update_dict = {}
    if result.get("approve_changes", "") == "Yes":
        for key in data_error_log.keys():
            update_dict[key] = data_error_log[key][1]

            if contract_data_dict:
                if key in contract_data_dict.keys():
                    contract_data_dict[key] = data_error_log[key][1]

        register_dict.update(update_dict)
        
        payload["register_info"] = register_dict
        payload["contract_data"] = contract_data_dict

    if not payload["give_hiring"]:  # Note that this is a boolean value and it represents if you gave up on the hiring or not
        send_task("manually_approved", payload)

    task.complete()