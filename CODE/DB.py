import http.client
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialize Firebase
cred = credentials.Certificate("D:/OptiPrice/firebase_credentials.json")  # Replace with your JSON key file
firebase_admin.initialize_app(cred)
db = firestore.client()

# API Call to Walmart
conn = http.client.HTTPSConnection("walmart-data.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "2ab6aa1c26msh99cbdca2111eb1ap13df56jsn89409570906f",
    'x-rapidapi-host': "walmart-data.p.rapidapi.com"
}

conn.request("GET", "/walmart-serp.php?url=https%3A%2F%2Fwww.walmart.com%2Fsearch%3Fq%3Dsamsung%2Bgalaxy", headers=headers)

res = conn.getresponse()
data = res.read()
data_json = json.loads(data.decode("utf-8"))  # Convert API response to JSON format

# Store Data in Firestore
doc_ref = db.collection("walmart_prices").document()  # Create a new document
doc_ref.set(data_json)

print("Data successfully stored in Firebase Firestore!")
