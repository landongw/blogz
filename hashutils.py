""" Runs hashing functions """

import hashlib
import random
import string


def make_salt():
    """ Creates a salt """

    return ''.join([random.choice(string.ascii_letters) for x in range(5)])


def make_pw_hash(password, salt=None):
    """ Returns a hashed string in place of the password """

    salt = make_salt()
    lhash = hashlib.sha256(str.encode(password)).hexdigest()
    return '{0},{1}'.format(lhash, salt)


def check_pw_hash(password, lhash):
    """ Checks if the password and hash match """

    salt = lhash.split(',')[1]
    if make_pw_hash(password, salt) == lhash:
        return True
    return False
