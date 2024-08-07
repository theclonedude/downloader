# -*- coding: utf-8 -*-
import requests
import json
import re
import certifi
import pymongo
import sys
import argparse
from bson.json_util import dumps, loads


parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
args = parser.parse_args()


client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["setting"]


r = requests.get('https://raino.dev/30pikpak')
r.encoding='utf-8'
#content_regex = r"(?<=<div class=\"notion-callout-text\">).*?(?=<\/div>)"
content_regex = r"最火磁力应用<\/b>(.*)>密码<span"
content = re.search(content_regex,r.text)


#usernames_regex = r"\<span class=\"notion-orange\"\>([^\<]*)\<\/span\>"
#usernames_regex = r"\<span class=\"notion-orange\"\>([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\s*)\<\/span\>"
usernames_regex = r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\s*)"


usernames = re.findall(usernames_regex,content.group())


password_regex = r"密码\<span class=\"notion-orange\"\>([^\<]*)\<\/span\>"
password_pattern = re.search(password_regex, r.text)
if password_pattern:
	password = password_pattern.group(1)
	print(password_pattern.group(1))
else:
	print("找不到密码")
	quit()
	
accounts={}
text="[]"
x = mycol.find_one({"name": "pikpak"})
if x is not None:
	text = x["value"]
accounts = json.loads(text)	

if usernames:
	for username in usernames:
		email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
		if re.search(email_regex,username.strip()) is None:
			continue
		find=list(filter(lambda account:account['username'].strip()==username.strip() and account['password']==password,accounts))
		if find:
			continue
		else:
			account={}
			account['username']=username.strip()
			account['password']=password
			accounts.append(account)
else:
	print("找不到用户名")
	quit()

res = mycol.update_one({"name": "pikpak"}, {"$set": {"value": json.dumps(accounts)}},upsert=True)
