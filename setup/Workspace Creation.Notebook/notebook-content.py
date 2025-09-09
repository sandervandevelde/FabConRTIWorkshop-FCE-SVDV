# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

%pip install semantic-link-labs

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

import math
import sempy_labs as labs
from string import Template
from sempy import fabric


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

import pandas as pd
import sempy_labs._icons as icons
from typing import Optional
from sempy_labs._helper_functions import (
    resolve_workspace_name_and_id,
    resolve_capacity_id,
    _base_api,
    _create_dataframe,
    _is_valid_uuid,
)
from uuid import UUID
from typing import List

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

#List of Trial Capacities Id
capacity_ids = [
    "0E5EB055-1412-4A8A-B4FA-80478066F1AC",
    "F374D1FB-491F-4435-B73C-6EE3E0348100",
    "FCA24D4D-ABF1-40D4-A6BF-AFA5AFC45647",
    "37C48351-BC07-4CA9-9267-47468B58FDB4",
    "5EB01CF3-B641-4CC8-99CE-F3DAA0524481",
    "97A727E5-9A60-425B-88B2-D43711E23589",
    "2A8CDED3-468E-448C-87B9-5AFE89A9642D",
    "7AB0D7A4-97B8-4AAA-B90E-EEC27DB05093",
    "D6535773-E5B8-4D77-BFA3-52F9B5844447",
    "C4D2F1DB-E6C5-4F4B-ABE3-12C3DCA45744",
]

user_name_assigned = "Workshop"
user_last_name_assigned = "User"
current_user = 1
number_users = 50

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

sp_info = {
    'key_vault_uri': f"https://mrtacatkeyvault.vault.azure.net/",
    'key_vault_tenant_id': f"tenant-id",
    'key_vault_client_id': f"fabric-admin-api-sp-id",
    'key_vault_client_secret': f"fabric-admin-api-sp-secret"
}

license_sku = "a403ebcc-fae0-4ca2-8c8c-7a907fd6c235"
workshop_users_group = "84929829-8dfc-4b5b-a638-fdf6736eef25"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

user_template = f"{user_name_assigned}{user_last_name_assigned}$id@mrtacat.onmicrosoft.com"
displayName_template=f"{user_name_assigned} {user_last_name_assigned} $id"
mailNickname_template=f"{user_name_assigned}{user_last_name_assigned}$id"
givenName=user_name_assigned
surname_template=f"{user_last_name_assigned} $id"
password="Workshop1234!"
workspace_template = f"{user_name_assigned} WS $id"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def validate_workspace(workspace_name:str):
    workspace_exists = True
    try:
        fabric.resolve_workspace_id(workspace_name)
    except fabric.exceptions.WorkspaceNotFoundException:
        workspace_exists = False

    return workspace_exists

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def create_user(userPrincipalName: str, displayName: str, mailNickname: str, password: str, givenName: str = None, surname: str = None) -> pd.DataFrame:
    """

    Parameters
    ----------
    userPrincipalName : str | uuid.UUID
        The user principal name.

    Returns
    -------
    pandas.DataFrame
        A pandas dataframe showing properties of a given user.
    """

    payload = {
        "accountEnabled": True,
        "displayName": displayName,
        "mailNickname": mailNickname,
        "userPrincipalName": userPrincipalName,
        "passwordProfile" : {
            "forceChangePasswordNextSignIn": True,
            "password": password
        },
        "usageLocation": "IE",
        "preferredLanguage":"en-US",
        "mail": userPrincipalName,
        "givenName": givenName,
        "surname": surname,
    }

    result = _base_api(request=f"users", client="graph", method="post", payload=payload, status_codes=201).json()

    new_data = {
        "User Id": result.get("id"),
        "User Principal Name": result.get("userPrincipalName"),
        "User Name": result.get("displayName"),
        "Mail": result.get("mail"),
        "Job Title": result.get("jobTitle"),
        "Office Location": result.get("officeLocation"),
        "Mobile Phone": result.get("mobilePhone"),
        "Business Phones": str(result.get("businessPhones")),
        "Preferred Language": result.get("preferredLanguage"),
        "Surname": result.get("surname"),
    }

    return pd.DataFrame([new_data])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def add_user_to_group(user: str | UUID, group_id: str | UUID) -> pd.DataFrame:
    """

    Parameters
    ----------
    userPrincipalName : str | uuid.UUID
        The user principal name.

    Returns
    -------
    pandas.DataFrame
        A pandas dataframe showing properties of a given user.
    """

    payload = {
        "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user}"
    }

    result = _base_api(request=f"groups/{group_id}/members/$ref", client="graph", method="post", status_codes=204, payload=payload)
    print(
        f"{icons.green_dot} The '{user}' user has been added  to group '{group_id}'."
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def assign_license(user: str | UUID, license_sku: str | UUID) -> pd.DataFrame:
    """

    Parameters
    ----------
    user : str | uuid.UUID
        The user ID or user principal name.

    Returns
    -------
    pandas.DataFrame
        A pandas dataframe showing properties of a given user.
    """

    payload = {
        "addLicenses": [
            {
                "disabledPlans": [],
                "skuId": license_sku
            }
        ],
        "removeLicenses": []
    }

    result = _base_api(request=f"users/{user}/assignLicense", client="graph", method="post", payload=payload)

    return result

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def add_user_to_workspace(
    user_id: str | UUID,
    email_address: str,
    role_name: str,
    principal_type: Optional[str] = "User",
    workspace: Optional[str | UUID] = None,
):
    """
    Adds a user to a workspace.

    This is a wrapper function for the following API: `Groups - Add Group User <https://learn.microsoft.com/rest/api/power-bi/groups/add-group-user>`_.

    Parameters
    ----------
    email_address : str
        The email address of the user. Also accepts the user identifier.
    role_name : str
        The `role <https://learn.microsoft.com/rest/api/power-bi/groups/add-group-user#groupuseraccessright>`_ of the user within the workspace.
    principal_type : str, default='User'
        The `principal type <https://learn.microsoft.com/rest/api/power-bi/groups/add-group-user#principaltype>`_.
    workspace : str | uuid.UUID, default=None
        The name or ID of the workspace.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    """

    (workspace_name, workspace_id) = resolve_workspace_name_and_id(workspace)

    role_names = icons.workspace_roles
    role_name = role_name.capitalize()
    if role_name not in role_names:
        raise ValueError(
            f"{icons.red_dot} Invalid role. The 'role_name' parameter must be one of the following: {role_names}."
        )
    plural = "n" if role_name == "Admin" else ""
    principal_types = icons.principal_types
    principal_type = principal_type.capitalize()
    if principal_type not in principal_types:
        raise ValueError(
            f"{icons.red_dot} Invalid princpal type. Valid options: {principal_types}."
        )

    payload = {
        "principal": {
            "id": user_id,
            "type": principal_type,
            "userDetails": {
                "userPrincipalName": email_address,
            }
        },
        "role": role_name,
    }

    _base_api(
        request=f"/v1/workspaces/{workspace_id}/roleAssignments",
        method="post",
        payload=payload,
        status_codes=201,
    )
    print(
        f"{icons.green_dot} The '{email_address}' user has been added as a{plural} '{role_name}' within the '{workspace_name}' workspace."
    )


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

id = "{:03d}".format(current_user)
upn = Template(user_template).safe_substitute(id=id)
displayName=Template(displayName_template).safe_substitute(id=id)
mailNickname=Template(mailNickname_template).safe_substitute(id=id)
surname=Template(surname_template).safe_substitute(id=id)
print(f"userPrincipalName: {upn}, displayName: {displayName},mailNickname: {mailNickname},password: {password}, givenName: {givenName}, surname: {surname}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

users_list = []
user_dict = {}


while current_user <= number_users:
    id = "{:03d}".format(current_user)
    upn = Template(user_template).safe_substitute(id=id)
    displayName=Template(displayName_template).safe_substitute(id=id)
    mailNickname=Template(mailNickname_template).safe_substitute(id=id)
    surname=Template(surname_template).safe_substitute(id=id)
    with labs.service_principal_authentication(
        key_vault_uri=sp_info['key_vault_uri'], 
        key_vault_tenant_id=sp_info['key_vault_tenant_id'],
        key_vault_client_id=sp_info['key_vault_client_id'],
        key_vault_client_secret=sp_info['key_vault_client_secret']):
        result = create_user(userPrincipalName=upn,displayName=displayName,mailNickname=mailNickname,password=password, givenName=givenName, surname=surname)
        user_id = result["User Id"][0]
        upn = result["User Principal Name"][0]
        assign_license(user=user_id,license_sku=license_sku)
        add_user_to_group(user=user_id,group_id=workshop_users_group)
    workspace_name = Template(workspace_template).safe_substitute(id=id)
    workspace_exists = validate_workspace(workspace_name)
    user_dict = {
        "user_id": user_id,
        "upn": upn,
        "workspace": workspace_name,
        "workspace_exists": workspace_exists,
    }
    users_list.append(user_dict)
    current_user = current_user + 1

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

len(users_list)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

chunk_size = math.ceil(number_users/len(capacity_ids))
chunks = [users_list[i:i + chunk_size] for i in range(0, len(users_list), chunk_size)]

for i,capacity_id in enumerate(capacity_ids):
    for i,user in enumerate(chunks[i]):
        # print(f"Creating workspace '{user['workspace']}' for user '{user['upn']} with capacity id '{capacity_id}' with state '{user['workspace_exists']}")        
        fabric.create_workspace(display_name=user['workspace'],capacity_id=capacity_id,description=f"Workspace for the {user['workspace']}")
        add_user_to_workspace(user_id=user['user_id'],email_address=user['upn'],role_name='Contributor',principal_type="User",workspace=user['workspace'])
        labs.add_user_to_workspace(email_address='6f41dc23-74b4-4859-9ee4-ba5629e4443c',role_name='Admin',principal_type="Group",workspace=user['workspace'])
        labs.add_user_to_workspace(email_address='6f35a2e8-dc45-4f91-8061-cb6da80c62d1',role_name='Admin',principal_type="Group",workspace=user['workspace'])
        notebookutils.notebook.run("NB_FabricAPI",90,{"workspace":user['workspace']})

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

workspace = "FabConEU2025 Setup Workspace"

notebookutils.notebook.run("NB_FabricAPITest",90,{"workspace":workspace})

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
