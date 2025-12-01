# from config import *
# from Utils.utils import *
import json
import logging
from urllib.parse import urlparse
import datetime
import requests
from config import API_PATH
import Utils


# Document: https://github.com/hiddify/hiddify-config/discussions/3209
# It not in uses now, but it will be used in the future.


def get_auth_headers(url):
    """
    Helper function to generate headers with Hiddify-API-Key.
    Extracts the UUID (API Key) from the panel URL.
    """
    try:
        # Assuming the URL structure is like: https://panel.example.com/UUID/
        # or we might need to pass the UUID explicitly if it's not in the base URL in the way we expect.
        # However, looking at config.py: PANEL_ADMIN_ID = urlparse(PANEL_URL).path.split('/')[2]
        # And in utils.py: BASE_URL = urlparse(PANEL_URL).scheme + "://" + urlparse(PANEL_URL).netloc
        # The 'url' argument passed to these functions often includes the path or is just the base.
        # Let's try to extract uuid from the url if possible, or rely on the caller to provide a url that contains it?
        # Actually, in the old code: added_by_uuid = urlparse(url).path.split('/')[2]
        # So we can extract the admin UUID from the URL path.
        
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        # path_parts example: ['', 'UUID', ''] or ['', 'UUID', 'admin', ...]
        if len(path_parts) >= 3:
             api_key = path_parts[1] # Assuming standard hiddify url structure: /<proxy_path>/<uuid>/...
             # Wait, standard structure is /<proxy_path>/<uuid>/...
             # But let's check config.py again. 
             # PANEL_ADMIN_ID = urlparse(PANEL_URL).path.split('/')[2] 
             # This suggests the structure is /<proxy_path>/<uuid>/... where proxy_path is index 1 and uuid is index 2?
             # Let's verify with a user provided example in config.py: 
             # Example: https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4
             # path: /7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4
             # split('/'): ['', '7frgemkvtE0', '78854985-68dp-425c-989b-7ap0c6kr9bd4']
             # Index 0: ''
             # Index 1: '7frgemkvtE0' (Proxy Path)
             # Index 2: '78854985-68dp-425c-989b-7ap0c6kr9bd4' (UUID / Admin Secret)
             
             api_key = path_parts[2]
             return {'Hiddify-API-Key': api_key, 'Content-Type': 'application/json'}
    except Exception as e:
        logging.error(f"Error extracting API key from URL {url}: {e}")
    return {'Content-Type': 'application/json'}


def select(url, endpoint="/admin/user/"):
    try:
        # url passed here usually is SERVER_URL + API_PATH
        # API_PATH is now /api/v2
        # So url is https://domain.com/proxy_path/uuid/api/v2
        # But wait, the V2 API docs say:
        # Base URL: /domain.com/admin_proxy_path/api/v2/admin
        # And the endpoint for users is /admin/user/
        # So the full URL should be .../api/v2/admin/user/
        
        # In the old code: response = requests.get(url + endpoint)
        # url was server['url'] + API_PATH. API_PATH was /api/v1.
        # Now API_PATH is /api/v2.
        # server['url'] includes /proxy_path/uuid ? 
        # Let's check Utils/utils.py: URL = server['url'] + API_PATH
        # server['url'] comes from DB. 
        # In config.py: url = input("[+] Enter your panel URL:") -> https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4
        # So server['url'] is the full path including UUID.
        
        # API V2 Base URL structure from doc: /{proxy_path}/api/v2/admin
        # But we have the UUID in the URL.
        # The doc says: "Note: For enhanced security, it is recommended to include the Hiddify-API-Key in the header of requests rather than directly in the URL."
        # However, we can probably still use the URL as base.
        # But wait, the endpoints in doc are like: /{proxy_path}/api/v2/admin/user/
        # They DO NOT include the UUID in the path for admin actions, they use header.
        # So we need to strip the UUID from the base URL if we want to follow the "header" approach strictly, 
        # OR we need to construct the URL correctly.
        
        # Let's look at the doc again.
        # Base URL: /domain.com/admin_proxy_path/api/v2/admin
        # Our server['url'] is /domain.com/admin_proxy_path/uuid
        
        # So we need to remove the UUID from the end of server['url'] to get the base for API V2 if we use headers.
        # server['url']: https://panel.com/proxy/uuid
        # We want: https://panel.com/proxy/api/v2/admin/user/
        
        # Let's parse the input `url` which is server['url'] + API_PATH (/api/v2)
        # Input `url`: https://panel.com/proxy/uuid/api/v2
        # We need to transform this to: https://panel.com/proxy/api/v2/admin/user/
        # AND extract the uuid for the header.
        
        # Actually, let's look at how `url` is passed.
        # In utils.py: URL = server['url'] + API_PATH
        # server['url'] has the UUID.
        # So URL is .../uuid/api/v2
        
        # We need to be careful. The doc says:
        # /{proxy_path}/api/v2/admin/user/
        # It does NOT have the UUID in the path.
        
        # So we must modify the URL construction.
        
        parsed = urlparse(url)
        # path: /proxy/uuid/api/v2
        path_parts = parsed.path.split('/')
        # ['', 'proxy', 'uuid', 'api', 'v2']
        
        if len(path_parts) >= 5 and path_parts[-1] == 'v2':
             # We assume the structure is correct from config.
             # We need to remove the UUID (index 2) from the path to get the correct API endpoint base?
             # Wait, if I remove UUID, how do I know it's index 2?
             # It is safer to take the config.py's PANEL_URL logic.
             
             # Let's extract UUID for header first.
             # The UUID is likely the segment before 'api' or 'api/v2' if we appended it.
             # But wait, if we appended /api/v2 to .../uuid, then uuid is indeed before api.
             
             # Let's reconstruct the base URL for API V2.
             # We want: https://host/proxy/api/v2
             # We have: https://host/proxy/uuid/api/v2
             
             # Let's try to handle this dynamically.
             # If we send a request to .../uuid/api/v2/admin/user/ with header, will it work?
             # The doc says: /{proxy_path}/api/v2/admin/user/
             # It does NOT mention uuid in path.
             
             # So I should probably strip the UUID from the URL.
             
             # Let's get the UUID.
             uuid = path_parts[-3] # .../uuid/api/v2 -> uuid is -3
             proxy_path = path_parts[-4] # .../proxy/uuid/api/v2 -> proxy is -4
             
             # This seems brittle.
             # Alternative: The user config has the full URL.
             # We can extract UUID from it.
             
             # Let's assume `url` passed to this function is `https://.../proxy/uuid/api/v2`
             # We want to call `https://.../proxy/api/v2/admin/user/`
             
             # Let's use string replacement for now, as it's safer than index assumptions if path varies.
             # We know the UUID format.
             pass

        # For now, let's try to use the provided URL but ensure we send the header.
        # If the server accepts UUID in path for V2, great. If not, we might need to adjust.
        # BUT, the doc explicitly shows: /{proxy_path}/api/v2/admin/user/
        # It does NOT show /{proxy_path}/{uuid}/api/v2/admin/user/
        
        # So we MUST remove the UUID from the path if it exists.
        
        headers = get_auth_headers(url)
        
        # Construct the new URL
        # We need to remove the UUID from the path.
        # We can use the UUID we extracted for the header to remove it from the string.
        api_key = headers.get('Hiddify-API-Key')
        
        real_url = url
        if api_key:
            # Remove /api_key from the url
            # url is .../proxy/uuid/api/v2
            # we want .../proxy/api/v2
            real_url = url.replace(f"/{api_key}", "")
            
        # Now append the endpoint
        # endpoint is /admin/user/
        # real_url is .../api/v2
        # final: .../api/v2/admin/user/
        
        # However, the `endpoint` argument in the old code was `/user/`.
        # I changed the default in signature to `/admin/user/`.
        # But `utils.py` calls `api.select(URL)` without endpoint, so it uses default.
        # `utils.py` calls `api.find(URL, uuid)` -> `find` uses default endpoint.
        
        full_url = f"{real_url}{endpoint}"
        
        response = requests.get(full_url, headers=headers)
        
        if response.status_code == 200:
            # The new API returns a list of users directly or inside a key?
            # Doc says: Response 200: [ { "uuid": ... }, ... ] (Array of Admin/User objects)
            # Old API: returned a dict or list?
            # Old code: Utils.utils.dict_process(url, Utils.utils.users_to_dict(response.json()))
            # users_to_dict expects a list of dicts.
            return Utils.utils.dict_process(url, Utils.utils.users_to_dict(response.json()))
        else:
            logging.error(f"API Select Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logging.error("API error: %s" % e)
        return None

def find(url, uuid, endpoint="/admin/user/"):
    try:
        headers = get_auth_headers(url)
        api_key = headers.get('Hiddify-API-Key')
        real_url = url
        if api_key:
            real_url = url.replace(f"/{api_key}", "")
            
        # V2: GET /admin/user/{uuid}/
        full_url = f"{real_url}{endpoint}{uuid}/"
        
        response = requests.get(full_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"API Find Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error("API error: %s" % e)
        return None

def insert(url, name, usage_limit_GB, package_days, last_reset_time=None, added_by_uuid=None, mode="no_reset",
            last_online="1-01-01 00:00:00", telegram_id=None,
            comment=None, current_usage_GB=0, start_date=None, endpoint="/admin/user/"):
    import uuid as uuid_lib
    # V2 Create User: POST /admin/user/
    # Body: User schema
    
    # Generate UUID if not provided (Old code generated it)
    new_uuid = str(uuid_lib.uuid4())
    
    # added_by_uuid logic from old code
    if not added_by_uuid:
         added_by_uuid = urlparse(url).path.split('/')[2] # This might need adjustment if we strip uuid from url in caller
         # But here 'url' is the raw one passed from utils.
    
    if not last_reset_time:
        last_reset_time = datetime.datetime.now().strftime("%Y-%m-%d")

    data = {
        "uuid": new_uuid,
        "name": name,
        "usage_limit_GB": usage_limit_GB,
        "package_days": package_days,
        "added_by_uuid": added_by_uuid,
        "last_reset_time": last_reset_time,
        "mode": mode,
        "last_online": last_online,
        "telegram_id": telegram_id,
        "comment": comment,
        "current_usage_GB": current_usage_GB,
        "start_date": start_date,
        "enable": True, # V2 requires this? Doc says 'enable': boolean. Old code didn't send it explicitly in dict but maybe implied?
        # Let's check doc for required fields.
        # Required: name.
        # But we should send everything we have.
    }
    
    # Filter None values if necessary, or send as is.
    # V2 doc says nullable: true for many fields.
    
    jdata = json.dumps(data)
    
    try:
        headers = get_auth_headers(url)
        api_key = headers.get('Hiddify-API-Key')
        real_url = url
        if api_key:
            real_url = url.replace(f"/{api_key}", "")
            
        full_url = f"{real_url}{endpoint}"
        
        response = requests.post(full_url, data=jdata, headers=headers)
        
        if response.status_code == 200:
            # Return the UUID
            return new_uuid
        else:
            logging.error(f"API Insert Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error("API error: %s" % e)
        return None

def update(url, uuid, endpoint="/admin/user/", **kwargs):
    try:
        # V2 Update User: PATCH /admin/user/{uuid}/
        
        headers = get_auth_headers(url)
        api_key = headers.get('Hiddify-API-Key')
        real_url = url
        if api_key:
            real_url = url.replace(f"/{api_key}", "")
            
        full_url = f"{real_url}{endpoint}{uuid}/"
        
        # We only need to send the fields that are changing.
        # kwargs contains the changes.
        
        data = kwargs
        jdata = json.dumps(data)
        
        response = requests.patch(full_url, data=jdata, headers=headers)
        
        if response.status_code == 200:
            return uuid
        else:
            logging.error(f"API Update Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error("API error: %s" % e)
        return None

def get_server_status(url):
    try:
        # V2 Server Status: GET /admin/server_status/
        
        headers = get_auth_headers(url)
        api_key = headers.get('Hiddify-API-Key')
        real_url = url
        if api_key:
            real_url = url.replace(f"/{api_key}", "")
            
        full_url = f"{real_url}/admin/server_status/"
        
        response = requests.get(full_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"API Server Status Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error("API error: %s" % e)
        return None


