from abstra.forms import TextInput, TextOutput, run
from abstra.tasks import get_tasks, send_task
import pandas as pd

# replace "_" by " " on the key and capitalize it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()

# get the data from the task payload
tasks = get_tasks()
task = tasks[0]
payload = task.get_payload()

mismatch_dict = payload["mismatch_info"]
register_dict = payload["register_info"]
paths_dict = payload["paths"]

mismatch_df = {transform_to_label(key): register_dict[key] for key in mismatch_dict.keys() if not(mismatch_dict[key])}
mismatch_df = pd.DataFrame(list(mismatch_df.items()), columns=["Label", "Value"])

# build the page where the data provided will be verified and changed if necessary
def correction_page(state):
    widgets = [
        TextOutput("An error was found on the following information. Please verify and correct it if necessary:")
    ]
    
    for index, row in mismatch_df.iterrows():
        widgets.append(
            TextInput(
                row['Label'], 
                key=row['Label'], 
                initial_value=str(row['Value']) if row['Value'] is not None else ""
            )
        )
    
    return widgets

change_register_result = run([correction_page])

# update the register_dict with the new information
for key in mismatch_dict.keys():
    if transform_to_label(key) in change_register_result:
        register_dict[key] = change_register_result[transform_to_label(key)]

payload["register_info"] = register_dict

send_task("partial_registration", payload)
task.complete()