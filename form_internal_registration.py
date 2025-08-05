from abstra.forms import (
    TextInput, EmailInput, DateInput, NumberInput, CurrencyInput,
    TextOutput, run
)
from abstra.tasks import get_tasks, send_task
from datetime import datetime

# function to preprocess date format
def preprocessing_date(date):
    if date is not None:
        date = datetime(date.year, date.month, date.day)
        date = date.replace(tzinfo=None)
        date = date.strftime("%Y/%m/%d")
    return date

# get the data from the task payload
tasks = get_tasks()

for task in tasks:
    payload = task.get_payload()
    
    # extracting data from payload
    mismatch_dict = payload.get("mismatch_info", {})
    register_dict = payload["register_info"]
    paths_dict = payload.get("paths", {})
    
    employee_name = register_dict["name"]
    
    # defining the form page
    def internal_info_page(state):
        return [
            TextOutput("Team Additional Data", size="large"),
            TextOutput(f"Please complete the following information about {employee_name}:"),
            DateInput("Start at", key="started_at"),
            TextInput("Position", key="position"),
            TextInput("Department", key="department"),
            EmailInput("Internal Email", key="internal_email"),
            CurrencyInput("Salary", currency="USD", initial_value=0, key="salary"),
            NumberInput("Weekly Work Hours", key="weekly_work_hours")
        ]
    
    # executing the form
    result = run([internal_info_page])
    
    # updating the register dictionary with new data
    register_dict.update(result)
    
    # processing the start date
    register_dict["started_at"] = preprocessing_date(register_dict["started_at"])
    
    # updating register_info variable in the task payload
    payload["register_info"] = register_dict
    
    send_task("internal_info_registered", payload)
    task.complete()