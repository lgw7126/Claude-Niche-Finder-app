import requests
import xml.etree.ElementTree as ET
import tomllib

with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

key = secrets["PUBLIC_DATA_API_KEY"]

url = (
    f"https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInDong"
    f"?serviceKey={key}&pageNo=1&numOfRows=3"
    f"&divId=dongCd&key=1144010900&indsLclsCd=I2&indsMclsCd=I212"
)

r = requests.get(url)
print("HTTP 상태:", r.status_code)
root = ET.fromstring(r.text)

items = root.findall(".//item")
print(f"결과 개수: {len(items)}개")
print()

for item in items:
    for child in item:
        print(f"  {child.tag}: {child.text}")
    print("---")
