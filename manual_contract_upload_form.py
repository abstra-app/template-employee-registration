import abstra.forms as af
import abstra.workflows as aw

# get variables from workflow
comments = aw.get_data("comments")
contract_dict = aw.get_data("contract_path")
register_dict = aw.get_data("register_info")
data_error_log = aw.get_data("data_error_log")
contract_data_dict = aw.get_data("contract_data")
 
# replace "_" by " " on the key and captalizes it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()


def render_contract_upload(partial):
    if "give_hiring" in partial.keys():
        if partial["give_hiring"] == "No":
            return af.Page().read_file("Upload the adjusted contract", key="corrected_contract", accepted_formats=[".docx"], required=False)


rejection_reason_page = (
    af.Page()
    .display_markdown('''# Rejection Details and Contract Review''')
    .display_markdown('''**The contract has been rejected.**''')
)    

if comments != "":
    rejection_reason_page = (
        rejection_reason_page
        .display_markdown('''**The following comments were made about it:**''')
        .display(f"'{comments}'")
    )

if data_error_log:
    rejection_reason_page = (
        rejection_reason_page
        .display_markdown('''**The following data was considered incorrect and changed by the employee (Old value -> New value):**''')
    )

    for key in data_error_log.keys():
        rejection_reason_page = (
            rejection_reason_page
            .display(f"{transform_to_label(key)}: {data_error_log[key][0]} -> {data_error_log[key][1]}")
        )
    rejection_reason_page = (
        rejection_reason_page
        .read_multiple_choice(
            '''Do you approve the changes?''',
            ["Yes", "No"],
            key="approve_changes"
        )
    )

rejection_reason_page = (
    rejection_reason_page
    .display_markdown('''**Please review the contract below:**''')
    .display_file(contract_dict["contract_filepath"], download_text="Click here to download the contract")
    .read_multiple_choice(
        "Do you want to give up on the hiring?",
        ["Yes", "No"],
        key="give_hiring"
    )
    .reactive(render_contract_upload)
    .run("Send")
)

if rejection_reason_page.get("corrected_contract", None) is not None:
    open(contract_dict["contract_filepath"], "wb").write(rejection_reason_page["corrected_contract"].file.read())

aw.set_data("give_hiring", (rejection_reason_page["give_hiring"] == "Yes"))

update_dict = {}
if rejection_reason_page.get("approve_changes", "") == "Yes":
    for key in data_error_log.keys():
        update_dict[key] = data_error_log[key][1]

        if contract_data_dict:
            if key in contract_data_dict.keys():
                contract_data_dict[key] = data_error_log[key][1]

    register_dict.update(update_dict)
    
    aw.set_data("register_info", register_dict)
    aw.set_data("contract_data", contract_data_dict)
    