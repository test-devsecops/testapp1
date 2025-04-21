import os, configparser, csv
import http.client, urllib, json

def getAccessToken(url,token,tenant_name):
    conn = http.client.HTTPSConnection(url)
    params = {
        "grant_type": "refresh_token",
        "client_id": "ast-app",
        "refresh_token": token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = urllib.parse.urlencode(params)
    endpoint = f"/auth/realms/{tenant_name}/protocol/openid-connect/token"

    try:
        conn.request("POST", endpoint, body=data, headers=headers)

        res = conn.getresponse()
        res_data = res.read()
        if res.status == 200:
            return json.loads(res_data.decode())['access_token']
        else:
            return None
    except:
        return

def getClientId(tenant_iam_url,tenant_name,acc_token):
    conn = http.client.HTTPSConnection(tenant_iam_url)
    api_url = "/auth/admin/realms/" + tenant_name + "/clients"

    headers = {
        'Authorization': "Bearer " + acc_token,
        'Accept': "application/json; version=1.0",
        'Content-Type': "application/json; version=1.0",
        'User-Agent': "python-requests/2.32.3"
    }

    try:
        print("Retrieving Client Id for ast-app client for role-mapping purposes...")
        conn.request("GET", url=api_url + "?clientId=ast-app", headers=headers)
        res = conn.getresponse()
        data = res.read()
        res_data = json.loads(data.decode("utf-8"))
        client_id = res_data[0]['id']
        print(res.status)
        return client_id
    except Exception as e:
        print('Failed in getting client \'ast-app\' id')
        print(e)

def getGroupsList(file_name):
    try:
        groups_list = []
        groups_items = {}
        with open(file_name,newline='') as csvfile:
            reader = csv.reader(csvfile,delimiter=',')
            tag_idx = 1
            group_name_idx = 0
            role_idx = 2
            for count,row in enumerate(reader):
                if count == 0:
                    for index,header in enumerate(row):
                        if header == 'tag':
                            tag_idx = index
                        elif header == 'displayName':
                            group_name_idx = index
                        elif header == 'role':
                            role_idx = index
                    continue
                group_name = row[group_name_idx]
                role = row[role_idx]
                tag = row[tag_idx]
                groups_list.append(group_name)
                groups_items[group_name] = {'role': role, 'tag': tag}
        return groups_list, groups_items
    except Exception as e:
        print(e)

def getRolesId(tenant_iam_url,tenant_name,acc_token,roles,client_id):
    conn = http.client.HTTPSConnection(tenant_iam_url)
    api_url = "/auth/admin/realms/" + tenant_name + "/clients/" + client_id + "/roles/"
    role_ids = {}

    headers = {
        'Authorization': "Bearer " + acc_token,
        'Accept': "application/json; version=1.0",
        'Content-Type': "application/json; version=1.0",
        'User-Agent': "python-requests/2.32.3"
    }

    try:
        for role in roles:
            print(f"Retrieving Role ID for {role}")
            conn.request('GET', api_url + role, headers=headers)
            res = conn.getresponse()
            data = res.read()
            print(res.status)
            res_data = json.loads(data.decode("utf-8"))
            role_id = res_data['id']
            role_ids[role] = role_id

        return role_ids
    except Exception as e:
        print('Failed in getting roles ids')
        print(e)

def createGroups(tenant_name):
    print(f"Creating Groups on Checkmarx tenant {tenant_name}...")

if __name__ == "__main__":
    # Set up variables from environment vars
    tenant_name = os.environ['CX_TENANT_NAME']
    tenant_iam_url = os.environ['CX_TENANT_IAM_URL']
    tenant_url = os.environ['CX_TENANT_URL']
    token = os.environ['CX_TOKEN']
    client_id = os.environ['CX_CLIENT_ID']
    # read from config file
    config = configparser.ConfigParser()
    config.read('.github/config/config.env')
    groups_file = config.get('INPUT', 'GROUPS_FILE')
    roles = config.get('INPUT', 'ROLES')

    # Retrieve the Access Token from CX
    acc_token = getAccessToken(tenant_iam_url, token, tenant_name)

    # Get list of groups to create on Checkmarx
    groups_list, group_items = getGroupsList(groups_file)

    # Get client id to query roles and do role-mappings
    client_id = getClientId(tenant_iam_url, tenant_name, acc_token)

    # Retrieve the role IDs
    role_ids = getRolesId(tenant_iam_url, tenant_name, acc_token, roles, client_id)
  
    createGroups(tenant_name)
