import requests

url = "https://currency-converter18.p.rapidapi.com/api/v1/convert"

querystring = {"from":"USD","to":"KZT","amount":"1"}

headers = {
	"X-RapidAPI-Key": "d7af63a666mshc3f4a24426ace55p14ea0cjsn2e3c9e8fe3d9",
	"X-RapidAPI-Host": "currency-converter18.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())