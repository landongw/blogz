""" Runs hashing functions

    Documentation: https://flask-bcrypt.readthedocs.io/en/latest/
"""

from flask import Flask
from flask.ext.bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)


def make_pw_hash(password):
    """ Returns a hashed string with salt in place of the password """

    # salt = make_salt()
    # salt = bcrypt.gensalt(12)
    lhash = bcrypt.generate_password_hash(password, 15).decode('utf8')
    # lhash = hashlib.sha256(str.encode(password)).hexdigest()
    return '{0}'.format(lhash)


def check_pw_hash(password, lhash):
    """ Checks if the password and hash match """

    if bcrypt.check_password_hash(lhash, password):
        return True
    return False
