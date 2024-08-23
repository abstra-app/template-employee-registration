import abstra.workflows as aw
import os
import base64
import dotenv
from uuid import uuid4 as creates_uuid
from docusign_esign import ApiException, ApiClient, EnvelopesApi, Document, Signer, SignHere, Tabs, Recipients, EnvelopeDefinition
from loguru import logger
from abstra.connectors import get_access_token

dotenv.load_dotenv()

# get variables from workflow
employee_approval_email = aw.get_data("employee_approval_email")
contract_dict = aw.get_data("contract_path")
register_dict = aw.get_data("register_info")

contract_filepath = contract_dict["contract_filepath"]
contract_filename = contract_dict["contract_filename"]

# get .env docsign tockens
ACCESS_TOKEN = get_access_token("docusign").token
DOCUSIGN_AUTH_SERVER = os.getenv('DOCUSIGN_AUTH_SERVER')
API_BASE_PATH = os.getenv('API_BASE_PATH')
ACCOUNT_ID = os.getenv("DOCUSIGN_API_ID")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")
MANAGER_NAME = os.getenv("MANAGER_NAME")


# creates envelope
# signer_data expects a dictionary with 2 signers
def make_envelope(signer_data):
    with open(contract_filepath, "rb") as file:
        content_bytes = file.read()
    base64_file_content = base64.b64encode(content_bytes).decode("ascii")

    # Create a document obj
    document = Document(
        document_base64=base64_file_content,
        name=contract_filename,
        file_extension="docx",
        document_id="1"
    )

    # Create models for the signers
    intern_signer = Signer(
        email=signer_data["intern_signer_email"],
        name=signer_data["intern_signer_name"],
        recipient_id=str(creates_uuid()),
        routing_order="1"
    )

    extern_signer = Signer(
        email=signer_data["extern_signer_email"],
        name=signer_data["extern_signer_name"],
        recipient_id=str(creates_uuid()),
        routing_order="2"
    )

    # Create the tabs for the signers
    sign_here_intern = SignHere(
        anchor_string="/sign_intern/",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )
    sign_here_extern = SignHere(
        anchor_string="/sign_extern/",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )

    # Add the tab models (including the sign here tab) to the signers
    intern_signer.tabs = Tabs(sign_here_tabs=[sign_here_intern])
    extern_signer.tabs = Tabs(sign_here_tabs=[sign_here_extern])

    envelope_definition = EnvelopeDefinition(
        email_subject=f"Please sign the following Service Agreement and Other Provisions document",
        documents=[document],
        recipients=Recipients(signers=[intern_signer, extern_signer]),
        status="sent"
    )

    return envelope_definition


signer_data = {
    "intern_signer_email": MANAGER_EMAIL,
    "intern_signer_name": MANAGER_NAME,
    "extern_signer_email": register_dict["personal_email"],
    "extern_signer_name":register_dict["name"],
}

api_client = ApiClient()
api_client.host = API_BASE_PATH
api_client.set_default_header("Authorization", f"Bearer {ACCESS_TOKEN}")

envelope_definition = make_envelope(signer_data)
envelopes_api = EnvelopesApi(api_client)

try:
    results = envelopes_api.create_envelope(
        ACCOUNT_ID, envelope_definition=envelope_definition)
    logger.success(f"Sign Requested. Envelope ID: {results.envelope_id}. Status: {results.status}")
except ApiException as e:
    logger.error(f"Error regarding docsign EnvelopesApi use: {e}")
