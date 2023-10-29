JWKS Server Project 2
CSEC 3550.001
Oz Birdett (oeb0010)
10-29-2023

Description: The following respositry containts the files, "jkws.py" and "testSuite.py", for the JWKS Server Project 2.
As well as screenshot showing the results of both the test suite and the gradebot being run with the JWKS server. Both files
are written in Python and the "jwks.py" file utilizes SQLite3 for the database. The "jwks.py" file is a server that provides
public keys with unique identifeirs for veryifing JSON Web tokens and stores them in a database. The keys are generated using 
RSA, have an expiration, and authentication endpoint. The testSuite.py file has three test cases to run against the JWKS Server 
to check the test coverage.

Execution:

For test coverage:

Run jwks.py in one terminal
Run testSuite.py in another terminal
Check results in terminal of testSuite.py

(It should be noted that "testSuite.py" can be run on its own without "jwks.py" and will show the results in the terminal.)

For test client:

Run jwks.py
Run gradebot from test client repository
Check results in terminal of jwks.py
