import abstra.forms as af
import abstra.workflows as aw
from datetime import datetime


# funtion to preprocess date format
def preprocessing_date(date):
    if date != None:
        date = datetime(date.year, date.month, date.day)
        date = date.replace(tzinfo=None)
        date = date.strftime("%Y/%m/%d")
    return date

# get the data from workflow
register_dict = aw.get_data("register_info")

# set variables
employee_name = register_dict["name"]

# form page to internal registration
internal_info_page = (
    af.Page()
    .display("Team Additional Data", size="large")
    .display(f"Please complete the following information about {employee_name}:")
    .read_date("Start at", key="started_at")
    .read("Position", key="position")
    .read("Department", key="department")
    .read_email("Internal Email", key="internal_email")
    .read_currency("Salary", currency="USD", initial_value=0, key="salary")
    .read_number("Weekly Work Hours", key="weekly_work_hours")
    .run()
)

register_dict.update(internal_info_page)

register_dict["started_at"] = preprocessing_date(register_dict["started_at"])

# updates register_info variable on the workflow
aw.set_data("register_info", register_dict)

