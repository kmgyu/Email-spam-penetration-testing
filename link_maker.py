import requests


TOKEN = 'blablabala'
url = 'https://api-ssl.bitly.com/v4/shorten'

headers = {
    'Authorization' : f'Bearer {TOKEN}',
    'Content-Type' : 'application/json',
    
}

body1 ={
  "long_url": "https://dev.bitly.com",
  "domain": "bit.ly",
  "group_guid": "Ba1bc23dE4F",
  "title": "Bitly API Documentation",
  "tags": [
    "bitly",
    "api"
  ],
  "deeplinks": [
    {
      "app_id": "com.bitly.app",
      "app_uri_path": "/store?id=123456",
      "install_url": "https://play.google.com/store/apps/details?id=com.bitly.app&hl=en_US",
      "install_type": "promote_install"
    }
  ]
}

body2 = {
  "long_url": "https://www.youtube.com/watch?v=1Z3Q29stte0",
  "domain": "bit.ly",
#   "group_guid": "mokpo_univ_hacking_test"
}

response = requests.post(url=url, json=body2, headers=headers)
print(response.json())