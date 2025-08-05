from abstra.forms import (
    TextInput, EmailInput, DateInput, PhoneInput, FileInput,
    TextOutput, run
)
from abstra.common import get_persistent_dir
from datetime import datetime
from abstra.tasks import send_task
import os

print("Iniciando formulário de registro pessoal...")

assignee = os.getenv("HIRING_RESPONSIBLE_EMAIL")
print(f"Responsável pelo processo: {assignee}")

# Configurando diretório para salvar os arquivos enviados
destination_dir = get_persistent_dir() / 'register_files'
destination_dir.mkdir(parents=True, exist_ok=True)
print(f"Diretório de arquivos configurado: {destination_dir}")

# Função para preprocessar formato de data
def preprocessing_date(date):
    if date is not None:
        date = datetime(date.year, date.month, date.day)
        date = date.replace(tzinfo=None)
        date = date.strftime("%Y/%m/%d")
    return date

# Definindo as páginas do formulário
def personal_info_page(state):
    return [
        TextOutput("Personal Data", size="large"),
        TextInput("Full name", key="name"),
        EmailInput("Email", key="personal_email"),
        DateInput("Birth Date", key="birth_date"),
        PhoneInput("Phone Number", key="phone_number"),
        TextInput("National ID number (e.g. RG in Brazil)", key="identification_number"),
        TextInput("ID number issued by", key="id_emitted_by"),
        TextInput("Individual Taxpayer Registration (e.g. CPF in Brazil)", key="taxpayer_id"),
        TextInput("Shirt size", placeholder="M", key="shirt_size")
    ]

def address_info_page(state):
    return [
        TextOutput("Address Data", size="large"),
        TextInput("Country", key="country"),
        TextInput("Address (without number)", key="address"),
        TextInput("Address number", key="number_address"),
        TextInput("Address complement", key="complement_address", required=False),
        TextInput("District", key="district"),
        TextInput("Zip code", key="zip_code")
    ]

def files_upload_page(state):
    return [
        TextOutput("Document Upload", size="large"),
        FileInput(
            "Upload a picture of your National ID document's front (.PNG format)",
            key="id_front_page",
            accepted_formats=[".png"]
        ),
        FileInput(
            "Upload a picture of your National ID document's back (.PNG format)",
            key="id_back_page",
            accepted_formats=[".png"]
        ),
        FileInput(
            "Upload a picture of a recent proof of address (.PNG format)",
            key="address_proof",
            accepted_formats=[".png"]
        )
    ]

def bank_info_page(state):
    return [
        TextOutput("Bank Account Data", size="large"),
        TextOutput(
            "Please enter your bank account data. If you're subscribed to a company, please enter the company's bank account data."
        ),
        TextInput("Bank name", placeholder="Goldman Sachs", key="bank_name"),
        TextInput("Bank account number", placeholder="0000000-0", key="bank_account_number"),
        TextInput("Bank branch code", placeholder="0001", key="bank_branch_code")
    ]

# Executando o formulário com as páginas definidas
print("Executando formulário...")
result = run([
    personal_info_page,
    address_info_page,
    files_upload_page,
    bank_info_page
])

print("Formulário preenchido com sucesso!")
print(f"Dados coletados: {list(result.keys())}")

# Extraindo os dados do resultado
name = result["name"]
personal_email = result["personal_email"]
birth_date = result["birth_date"]
phone_number = result["phone_number"]
identification_number = result["identification_number"]
id_emitted_by = result["id_emitted_by"]
taxpayer_id = result["taxpayer_id"]
shirt_size = result["shirt_size"]

country = result["country"]
address = result["address"]
number_address = result["number_address"]
complement_address = result["complement_address"]
district = result["district"]
zip_code = result["zip_code"]

id_front_page = result["id_front_page"]
id_back_page = result["id_back_page"]
address_proof = result["address_proof"]

bank_name = result["bank_name"]
bank_account_number = result["bank_account_number"]
bank_branch_code = result["bank_branch_code"]

# Processando os dados
print("Processando dados...")
birth_date = preprocessing_date(birth_date)
phone_number = phone_number.raw if hasattr(phone_number, 'raw') else str(phone_number)
taxpayer_id = taxpayer_id.replace(".", "").replace("-", "")

print(f"Data de nascimento processada: {birth_date}")
print(f"Telefone processado: {phone_number}")
print(f"CPF processado: {taxpayer_id}")

# Salvando arquivos no diretório persistente usando o número de identificação da pessoa
path_front_page = f"{identification_number}_id_front_page.png"
path_back_page = f"{identification_number}_id_back_page.png"
path_address_proof = f"{identification_number}_address_proof.png"

print(f"Salvando arquivos para ID: {identification_number}")
destination_dir.joinpath(path_front_page).write_bytes(id_front_page.file.read())
destination_dir.joinpath(path_back_page).write_bytes(id_back_page.file.read())
destination_dir.joinpath(path_address_proof).write_bytes(address_proof.file.read())
print("Arquivos salvos com sucesso!")

# Preparando dados para enviar para o próximo estágio
payload = {
    "assignee": assignee,
    "register_info": {
        "name": name,
        "personal_email": personal_email,
        "birth_date": birth_date,
        "phone_number": phone_number,
        "identification_number": identification_number,
        "id_emitted_by": id_emitted_by,
        "taxpayer_id": taxpayer_id,
        "country": country,
        "address": address,
        "number_address": number_address,
        "complement_address": complement_address,
        "district": district,
        "zip_code": zip_code,
        "shirt_size": shirt_size,
        "bank_name": bank_name,
        "bank_account_number": bank_account_number,
        "bank_branch_code": bank_branch_code,
    },
    "paths": {
        "id_front_page": str(destination_dir.joinpath(path_front_page)),
        "id_back_page": str(destination_dir.joinpath(path_back_page)),
        "address_proof": str(destination_dir.joinpath(path_address_proof))
    },
    "employee_approval_email": personal_email
}

print(f"Enviando task 'registration' com payload preparado...")
send_task("registration", payload)
print("Task enviada com sucesso! Processo de registro iniciado.")