#!/usr/bin/env python
# -=- encoding: utf-8 -=-

PROGRAM = "SFLvault"
VERSION = "0.1"

SERVER = 'http://localhost:5000/vault/rpc'
CONFIG_FILE = '~/.sflvault/config'

import optparse
import sys
import xmlrpclib
from Crypto.PublicKey import ElGamal
from Crypto.Cipher import AES, Blowfish
from Crypto.Util import randpool
from base64 import b64decode, b64encode
import pickle

from pprint import pprint


### Setup variables and functions
#
# Setup default action = help
#
action = 'help'
if (len(sys.argv) > 1):
    # Take out the action.
    action = sys.argv.pop(1)
    if (action in ['-h', '--help']):
        action = 'help'

    # Fix for functions
    action = action.replace('-', '_')

#
# Config file setup
#
## TODO: check if ~/.sflvault exists
##        or create it (mode 0700)
##       check if modes for ~/.sflvault are 0700
##        or halt with error message
##       check for ownership of that dir, or halt with error
##       check if ~/.sflvault/config exists
##        or create it (mode 0600, correct ownership)
##       check if ~/.sflvault/config is mode 0700
##        or halt with error message
##       check for ownership of that file, or halt with error
##       check if ~/.sflvault/key exists
##        check if it's not 0700
##         if not, halt with error (give the command to fix it)
##       check for ownership of that file, or halt with error
##       parse the config file, return the ConfigParser
##       --
##       define a func to write back to the config file
##       and enforce permissions
cfg = ConfigParser.ConfigParser()
cfg.readfp()
def vaultConfigCheck():
    """Checks for ownership and modes for all paths and files, à-la SSH"""
    pass

def vaultConfigRead():
    """Return the ConfigParser object, fully loaded"""
    pass

def vaultConfigWrite(cfg):
    """Write the ConfigParser element to disk."""
    pass

#
# Command line parser
#
parser = optparse.OptionParser()


#
# Random number generators setup
#
pool = randpool.RandomPool()
pool.stir()
pool.randomize()
randfunc = pool.get_bytes # We'll use this func for most of the random stuff


#
# XML-RPC server setup.
#
srv = xmlrpclib.Server(SERVER)



#
# Helper functions
#
def authenticate():

    pprint(srv.sflvault.login('admin'))

    sys.exit()

### TODO: two functions that violate DRY principle, they are in lib/base.py
def vaultSerial(something):
    """Serialize with pickle.dumps + b64encode"""
    return b64encode(pickle.dumps(something))

def vaultUnserial(something):
    """Unserialize with b64decode + pickle.loads"""
    return pickle.loads(b64decode(something))


###
### On définit les fonctions qui vont traiter chaque sorte de requête.
###
class SFLvaultFunctions(object):
    def help(self, error = None):
        print "%s version %s" % (PROGRAM, VERSION)
        print "---------------------------------------------"
        print "Here is a quick overview of the commands:"
        print "  adduser       add a user"
        print "  deluser       remove a user"
        print "  [add more]    yes please"
        print "---------------------------------------------"
        print "Call: sflvault [command] --help for more details on"
        print "each of those commands."
        if (error):
            print "---"
            print "ERROR: %s" % error
        exit();
    
    def adduser(self):
        if (len(sys.argv) != 2):
            print "Usage: adduser [username]"
            sys.exit()
        username = sys.argv.pop(1)

        retval = srv.sflvault.adduser(username)

        if (retval['error']):
            print "Vault error: %s" % retval['message']
        else:
            print "Vault says: %s" % retval['message']

    def addcustomer(self):
        print "Do addcustomer"

    def addserver(self):
        print "Do addserver"

    def grant(self):
        pass
    
    def setup(self):
        if (len(sys.argv) != 3):
            print "Usage: setup [username] [vault-url]"
            sys.exit()
        username = sys.argv.pop(1)
        url      = sys.argv.pop(1)
        ## TODO: use the 'url', and not the hard-coded one.

        # Generate a new key:
        print "Generating new ElGamal key-pair..."
        eg = ElGamal.generate(1536, randfunc)

        # Marshal the ElGamal key
        pubkey = (eg.p, eg.g, eg.y)

        print "Sending request to vault..."
        # Send it to the vault, with username
        retval = srv.sflvault.setup(username, vaultSerial(pubkey))

        # If Vault sends a SUCCESS, save all the stuff (username, url)
        # and encrypt privkey locally (with Blowfish)
        print "Vault says: %s" % retval['message']

        pprint(retval)
        if (retval['error']):
            print "We'd stop everything."
            # Drop and error message (from vault also)
            pass
        else:
            print "Ok, we'd save everything :)"
            # Save all (username, url)
            # Encrypt privkey locally (with Blowfish)
            pass

        # TODO: remove this, login test
        retval = srv.sflvault.login(username)
        if not retval['error']:
            # decrypt token.
            cryptok = eg.decrypt(vaultUnserial(retval['cryptok']))
            retval2 = srv.sflvault.authenticate(username, vaultSerial(cryptok))

            print "WOAH"
            pprint(retval2)
    
    def deluser(self):
        pass
    
    def connect(self):
        authenticate()
    
    def search(self):
        print "Do search, and show and help to select."

    def show(self):
        print "Search using xmlrpc:show(), with the service_id, and DECRYPT"
        
    def list_users(self):
        print "Do addserver"

    def list_customers(self):
        pass








###
### Execute requested command-line command
###
f = SFLvaultFunctions()

# Call the appropriate function of the 'f' object, according to 'action'

try:
    getattr(f, action)()
except AttributeError:
    getattr(f, 'help')("Unknown action: %s" % action)