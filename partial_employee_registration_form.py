import abstra.forms as af
import abstra.workflows as aw
import pandas as pd

# get the data from workflow
mismatch_dict = aw.get_data("mismatch_info")
register_dict = aw.get_data("register_info")
paths_dict = aw.get_data("paths")


# replace "_" by " " on the key and captalizes it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()


mismatch_df = {transform_to_label(key): register_dict[key] for key in mismatch_dict.keys() if not(mismatch_dict[key])}
mismatch_df = pd.DataFrame(list(mismatch_df.items()), columns=["Label", "Value"])

# build the page where the data provided will be verified and changed if necessary
change_register_page = (
    af.Page()
    .display("An error was found on the following information. Please verify and correct it if necessary:")
)

for index, row in mismatch_df.iterrows():
    change_register_page = change_register_page.read(row['Label'], key=row['Label'], initial_value=row['Value'])

change_register_page = change_register_page.run()

# update the register_dict with the new information
for key in mismatch_dict.keys():
    if transform_to_label(key) in change_register_page.keys():
        register_dict[key] = change_register_page[transform_to_label(key)]

aw.set_data("register_info", register_dict)