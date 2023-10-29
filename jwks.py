#Author: Oz Birdett (oeb0010)
#Date: 10-29-2023

from http.server import BaseHTTPRequestHandler, HTTPServer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from urllib.parse import urlparse, parse_qs
import base64
import json
import jwt
import datetime
import sqlite3

private_key = None #Set private_key as global variable

db_connection = sqlite3.connect("totally_not_my_privateKeys.db") #Creates or connects to database

#Table schema for database
table_schema = """ 
    CREATE TABLE IF NOT EXISTS keys (
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        key BLOB NOT NULL,
        exp INTEGER NOT NULL
    )
"""

db_connection.execute(table_schema) #Execute the schema
db_connection.commit() #Commit it to the database

hostName = "localhost" #Set host name and port
serverPort = 8080

private_key = rsa.generate_private_key( #Generate private RSA key
    public_exponent=65537,
    key_size=2048,
)
expired_key = rsa.generate_private_key( #Generate expired RSA key
    public_exponent=65537,
    key_size=2048,
)

pem = private_key.private_bytes( #Serialized private key
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
expired_pem = expired_key.private_bytes( #Serialized expired key
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

def save_key(key_bytes, exp): #Save key to database
    db_connection.execute("INSERT INTO keys (key, exp) VALUES (?, ?)", (key_bytes, exp))
    db_connection.commit()

save_key(pem, int(datetime.datetime.utcnow().timestamp())) #Save private key
save_key(expired_pem, int((datetime.datetime.utcnow() - datetime.timedelta(hours=1)).timestamp())) #Save expired key


numbers = private_key.private_numbers()

def read_key(expired=False): #Read private key from database
    current_time = int(datetime.datetime.utcnow().timestamp()) #Get current time
    db_connection.execute("SELECT key FROM keys WHERE exp <= ?" if expired else "SELECT key FROM keys WHERE exp > ?", (current_time,)) #If expired select key if not select unexpired keyt
    cursor = db_connection.cursor()
    row = cursor.fetchone() #Get first row from the result
    cursor.close()
    if row:
        return row[0] #Return key from first column
    return None


def int_to_base64(value): #Convert an integer to a Base64URL-encoded string
    """Convert an integer to a Base64URL-encoded string"""
    value_hex = format(value, 'x')
    # Ensure even length
    if len(value_hex) % 2 == 1:
        value_hex = '0' + value_hex
    value_bytes = bytes.fromhex(value_hex)
    encoded = base64.urlsafe_b64encode(value_bytes).rstrip(b'=')
    return encoded.decode('utf-8')


class MyServer(BaseHTTPRequestHandler): #MyServer class
    def do_PUT(self): #Handles PUT request
        self.send_response(405)
        self.end_headers()
        return

    def do_PATCH(self): #Handles PATCH request
        self.send_response(405)
        self.end_headers()
        return

    def do_DELETE(self): #Handles DELETE request
        self.send_response(405)
        self.end_headers()
        return

    def do_HEAD(self): #Handles HEAD request
        self.send_response(405)
        self.end_headers()
        return

    def do_POST(self): #Handles POST request
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        if parsed_path.path == "/auth": #Check path
            headers = { #Set headers
                "kid": "goodKID"
            }
            token_payload = { #Create token payload
                "user": "username",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }

            if 'expired' in params: #If expired
                headers["kid"] = "expiredKID" #Set header to expired
                token_payload["exp"] = datetime.datetime.utcnow() - datetime.timedelta(hours=1) #Change expiration date
            else: #Leave it the same
                headers["kid"] = "goodKID"
                token_payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            encoded_jwt = jwt.encode(token_payload, pem, algorithm="RS256", headers=headers) #Create JWT Token    
            self.send_response(200) #Send response
            self.end_headers()
            self.wfile.write(bytes(encoded_jwt, "utf-8"))

        self.send_response(405) #Send response
        self.end_headers()
        return

    def do_GET(self): #Handles GET request
        if self.path == "/.well-known/jwks.json": #Check path
            self.send_response(200) #Send response
            self.send_header("Content-type", "application/json") #Set header
            self.end_headers()
            db_connection.execute("SELECT key FROM keys WHERE exp > ?", (int(datetime.datetime.utcnow().timestamp()),)) #Fetch public key
            keys = {
                "keys": [ #Create JSON object
                    {
                        "alg": "RS256",
                        "kty": "RSA",
                        "use": "sig",
                        "kid": "goodKID",
                        "n": int_to_base64(numbers.public_numbers.n),
                        "e": int_to_base64(numbers.public_numbers.e),
                    }
                ]
            }
            self.wfile.write(bytes(json.dumps(keys), "utf-8")) #Write JSON to response
            return

        self.send_response(405) #Send response
        self.end_headers()
        return


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer) #Start HTTP server
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close() #Close server
