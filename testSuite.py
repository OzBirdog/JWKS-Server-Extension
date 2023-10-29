#Author: Oz Birdett (oeb0010)
#Date: 10-29-2023

import unittest
import requests
import subprocess
import time

class TestMyServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls): #Starts HTTPS server
        cls.server_process = subprocess.Popen(["python", "jwks.py"]) 
        time.sleep(2) 

    @classmethod
    def tearDownClass(cls): #Terminate HTTPS server
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_get_jwks_json(self): #Sends GET request
        response = requests.get("http://localhost:8080/.well-known/jwks.json")
        self.assertEqual(response.status_code, 200) #Checks response

        data = response.json()
        self.assertTrue("keys" in data)
        self.assertTrue(data["keys"])

    def test_auth_with_expired_token(self): #Sends POST request with expired token
        data = {"username": "userABC", "password": "password123"}
        response = requests.post("http://localhost:8080/auth?expired=true", json=data)
        self.assertEqual(response.status_code, 200) #Checks response
 
    def test_auth_with_valid_token(self): #Sends POST request with valid token
        data = {"username": "userABC", "password": "password123"}
        response = requests.post("http://localhost:8080/auth", json=data)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() #Runs test suite
'''
Use of ChatGPT in This Assignment
I used ChatGPT to creat the test case for this assignment. I gave ChatGPT the "jwks.py" file and the "testSuite.py" file I wrote for the last assignment. 
I told ChatGPT to create a new test suite for "jwks.py" that is based on the "testSuite.py" file I gave it. It then gave a suitable test suite file, which
I made into the "testSuite.py" for this assignment.
'''
