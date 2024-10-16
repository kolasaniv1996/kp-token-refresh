import requests
import json
import argparse
import time

# Configuration
APPNAME = 'xx'
APPSECRET = 'xx'
APPURL = 'xx'
REALM = 'runai'

# Token variables
token = None
token_expiration_time = 0

def login():
    global token, token_expiration_time
    payload = f"grant_type=client_credentials&client_id={APPNAME}&client_secret={APPSECRET}"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = f"{APPURL}/auth/realms/{REALM}/protocol/openid-connect/token"
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code // 100 == 2:
        response_data = json.loads(r.text)
        token = response_data['access_token']
        # Set token expiration time with a buffer of 60 seconds
        token_expiration_time = time.time() + response_data['expires_in'] - 60
    else:
        print("Login error: " + r.text)
        exit(1)

def get_token():
    global token
    if time.time() >= token_expiration_time:
        login()
    return token

def update_project_settings(cluster_id, department_id, settings):
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    jsonpayload = json.dumps(settings)
    
    url = f"{NEW_APPURL}/v1/k8s/clusters/{cluster_id}/departments/{department_id}?excludePermissions=true"
    r = requests.put(url, headers=headers, data=jsonpayload)
 
    if r.status_code // 100 == 2:
        print(f"Department {department_id} settings updated successfully")
        return r.json()
    else:
        print(f"Update failed for department {department_id}: {r.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Update Run:AI department settings")
    parser.add_argument("--cluster", required=True, help="Cluster ID")
    parser.add_argument("--departments", required=True, nargs='+', type=int, help="List of department IDs")
    parser.add_argument("--interactive-time-limit", type=int, help="Interactive job time limit in seconds")
    parser.add_argument("--training-time-limit", type=int, help="Training job time limit in seconds")
    args = parser.parse_args()

    login()
    
    settings = {}
    if args.interactive_time_limit is not None:
        settings["interactiveJobTimeLimitSecs"] = args.interactive_time_limit
    if args.training_time_limit is not None:
        settings["trainingJobTimeLimitSecs"] = args.training_time_limit

    for department_id in args.departments:
        result = update_project_settings(args.cluster, department_id, settings)
        if result:
            print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
