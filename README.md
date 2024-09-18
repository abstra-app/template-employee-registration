# Employee Registration Template
## How it works:

This project includes a new employee registration process implemented with Abstra and Python scripts. The new employee fills out a form with their personal data, which is then verified by Abstra AI and sent to the responsible team for approval. After the approval stage, a contract is automatically generated and sent to the parties involved. The system integrates with DocuSign to collect the necessary signatures and with Pandoc to convert the contract file.

Integrations:
  - Docusign
  - Pandoc

To customize this template for your team and build a lot more, [book a demonstration here.](https://meet.abstra.app/demo?url=template-employee-registration)

![A contract generator onboarding workflow built in Abstra](https://github.com/user-attachments/assets/c38cccdc-0279-4054-a93f-450c05454176)

## Initial Configuration
To use this project, some initial configurations are necessary:

1. **Python Version**: Ensure Python version 3.9 or higher is installed on your system.
2. **Integrations**: To connect to DocuSign, this template uses Abstra connectors. To connect, simply open your project in [Abstra Cloud Console](https://cloud.abstra.io/projects/), add the DocuSign connector, and authorize it.
3. **Environment Variables**:

    The following environment variables are required for both local development and online deployment:
    - `DOCUSIGN_API_ID`: DocuSign API account ID used for sending the contract to sign
    - `DOCUSIGN_AUTH_SERVER`: DocuSign Authentication server URL for sending the contract to sign 
    - `API_BASE_PATH`: Base path where the contract will be uploaded on DocuSign service

    In the scripts, we assume that the manager is the signer involved in the hiring process and that another person is responsible for analyzing the new employee data and generating the contract. Below are some details regarding the manager. If another party is involved, please change the key name or add new ones as needed in the `.env` file:
    - `MANAGER_NAME`: Manager`s name
    - `MANAGER_EMAIL`: Manager`s email
    - `HIRING_RESPONSIBLE_EMAIL`: Responsible for hiring email
  
    For local development, create a `.env` file at the root of the project and add the variables listed above (as in `.env.example`). For online deployment, configure these variables in your [environment settings](https://docs.abstra.io/cloud/envvars). 

4. **Dependencies**: To install the necessary dependencies for this project, a `requirements.txt` file is provided. This file includes all the required libraries.

   Follow these steps to install the dependencies:

   1. Open your terminal and navigate to the project directory.
   2. Run the following command to install the dependencies from `requirements.txt`:
        ```sh
        pip install -r requirements.txt
        ```
5. **Access Control**: The generated form is protected by default. For local testing, no additional configuration is necessary. However, for cloud usage, you need to add your own access rules. For more information on how to configure access control, refer to the [Abstra access control documentation](https://docs.abstra.io/concepts/access-control).
   
6. **Pandoc**: To test it locally, please download and install [Pandoc](https://pandoc.org/). Remender to add the path of the executable on the `.env` file.

7. **Database configuration**: Set up your database tables in Abstra Cloud Tables according to the schema defined in `abstra-tables.json`.
   
    To automatically create the table schema, follow these steps:
  
    1. Open your terminal and navigate to the project directory.
  
    3. Run the following command to install the table schema from `abstra-tables.json`:
       ```sh
       abstra restore
       ```
       
    For guidance on creating and managing tables in Abstra, refer to the [Abstra Tables documentation](https://docs.abstra.io/cloud/tables).
  
8. **Contract Template Creation**: Create a contract template in a `.docx` format according to your internal policies and replace our template in the `contract_models` folder by it. Use the following tags in the document where you want specific information to be inserted:

    **Personal Information**
      - {{name}}, {{personal_email}}, {{birth_date}}, {{phone_number}}, {{identification_number}}, {{id_emitted_by}}, {{taxpayer_id}}, {{country}}, {{address}}, {{number_address}}, {{complement_address}}, {{district}}, {{zip_code}}, {{shirt_size}}, {{bank_name}}, {{bank_account_number}}, {{bank_branch_code}}
      
    **Internal Information**
      - {{started_at}}, {{position}}, {{department}}, {{internal_email}}, {{salary}}, {{weekly_work_hours}}

9. **Local Usage**: To access the local editor with the project, use the following command:

   ```sh
      abstra editor path/to/your/project/folder/
   ```

## General Workflow:
To implement this system use the following scripts:

### Employee Registration:
For registering a employee and collecting personal data about it, use:
  - **employee_registration_form.py**: Script to generate a form that collects personal data from a new employee, including document pictures.

### Verification of Information:
  - **ai_personal_info_check.py**: Script to verify if the personal information provided matches the information in the document pictures.
  - **divergence_on_register_form.py**: Script to generate a form for manual approval of the provided information (if the AI detects any mismatch).
  - **partial_employee_registration_form.py**: Script to generate a form for correcting the provided information with potential errors (if the information was rejected in the manual approval step).

### Intern Registration:
  - **internal_registration_form.py**: Script to generate a form to be filled out by a company member, collecting the employee's position information.

### Contract Generation and Approval:
  - **generate_contract_form.py**: Script to automatically generate a contract based on either the existing template in the folder or a new template uploaded via a form.
  - **contract_approval_form.py**: Script to generate a form that allows the employee to review the contract, approve or reject it, and provide comments.
  - **manual_contract_upload_form.py**: Script to generate a form where the employer can review comments made by the employee if the contract was rejected. The employer can then decide to either abandon the hiring process or upload a modified contract.

### Contract Signing:
  - **send_contract_to_sign.py**: Script to send the contract via email for signing by the parties involved using DocuSign.

If you're interested in customizing this template for your team in under 30 minutes, [book a customization session here.](https://meet.abstra.app/demo?url=template-employee-registration)
