#!/usr/bin/env python
'''ballast.py: A DigitalOcean Droplet Manager '''

__author__      =       "Matt Bromiley (@mbromileyDFIR)"
__license__     =       "Apache License v2.0"
__version__     =       "0.1.0-dev"
__maintainer__  =       "Matt Bromiley (@mbromileyDFIR)"
__email__       =       "505forensics@gmail.com"
__status__      =       "Development"

from cmd import Cmd
import os, getpass, json

#DigitalOcean API is obviously used to connect to DigitalOcean
try:
    import digitalocean
except ImportError:
    print "DigitalOcean not found. Please install the DigitalOcean Python library."
    exit()

# Simple-crypt is used to work with the encrypted API key. This gives users a chance to store their DigitalOcean API key on their system for future use.
try:
    from simplecrypt import encrypt, decrypt
except ImportError:
    print "simple-crypt not found. Please install simple-crypt"
    exit()

encrypted_file = '.ballast_api'
d = {}
d_raw = {}

def populate(api_key):
    print "Populating droplets..."
    manager = digitalocean.Manager(token=api_key)
    droplets = manager.get_all_droplets()
    for idx, droplet in enumerate(droplets):
        d[idx] = {'Name':droplet.name,
                  'ID':droplet.id,
                  'Memory (MB)':droplet.memory,
                  'Disk (GB)':droplet.disk,
                  'IP Address':droplet.ip_address,
                  'Created Date':droplet.created_at,
                  'Status':droplet.status,
                  'Image':droplet.image['distribution'] + ' ' + droplet.image['name']
                  }
        d_raw[idx] = droplet

def retrieve_key():
    file = open(encrypted_file,'r')
    ciphertext = file.read()
    print "I found an encrypted API key. Please enter your passphrase to decrypt:"
    passphrase = getpass.getpass()
    print "Attempting to decrypt your API key. Please wait..."
    decrypted_key = decrypt(passphrase, ciphertext)
    return decrypted_key

def store_key():
    api_key = raw_input('Please enter your API key: ')
    passphrase = getpass.getpass('Please enter the passphrase to encrypt your API key: ')
    ciphertext = encrypt(passphrase, api_key)
    file = open('.ballast_api','w')
    file.write(ciphertext)
    return api_key

class Ballast(Cmd):
    def do_list(self, line):
        'List the number of DigitalOcean droplets you have for this API key'
        print "You currently have {0} Droplets:".format(len(d))
        for i in d:
            print "{0} - {1}".format(i, d[i]['Name'])
        print "\nUse info <#> to get more info on a particular droplet"

    def do_info(self, idx):
        'Get info on a particular DigitalOcean droplet. Usage: info <#>'
        try:
            if idx:
                e = d[(int(idx))]
                print json.dumps(e, indent=4,sort_keys=True)
            else:
                print "No ID provided. Usage: info <#>"
        except KeyError:
            print "You have entered an invalid droplet ID. Please try again."

    def do_quit(self, line):
        'Quit ballast'
        return True

    def do_exit(self, line):
        'Quit ballast'
        return True

    def do_refresh(self, line):
        'Refresh the list of DigitalOcean droplets'
        populate(api_key)

    def do_shutdown(self, idx):
        'Shutdown a DigitalOcean droplet. Usage: shutdown <#>'
        try:
            if idx:
                e = d_raw[int(idx)].shutdown()
                if e['action']['type'] == "shutdown":
                    print "{} shutdown successfully.".format(d[int(idx)]['Name'])
                populate(api_key)
            else:
                print "No ID provided. Usage: shutdown <#>"
        except KeyError:
            print "You have entered an invalid droplet ID. Please try again."

    def do_poweron(self, idx):
        'Power on a DigitalOcean droplet. Usage: poweron <#>'
        try:
            if idx:
                e=d_raw[int(idx)].power_on()
                populate(api_key)
            else:
                print "No ID provided. Usage: poweron <#>"
        except KeyError:
            print "You have entered an invalid droplet ID. Please try again."

    def do_rename(self, line):
        'Rename a droplet. Usage: rename <#> <new name>'
        rename_input = line.split()
        d_raw[int(rename_input[0])].rename(rename_input[1])

if __name__ == "__main__":
    os.system('clear')
    print "Welcome to Ballast, a Digital Ocean Droplet Manager"
    if os.path.exists(encrypted_file):
        api_key = retrieve_key()
    else:
        store_choice = raw_input("I was unable to find an encrypted API key. Would you like to store one? (Y/N): ")
        if store_choice.upper() == 'Y':
            api_key = store_key()
        else:
            api_key = raw_input('Please enter your API key (this will not be written to disk): ')

    #The populate function fills the TinyDB instance with information gathered from DigitalOcean. Note that this is done each time the script is run.
    populate(api_key)
    os.system('clear')
    prompt = Ballast()
    prompt.prompt = 'ballast> '
    prompt.cmdloop('''Welcome to Ballast, a tool to help manage your Digital Ocean droplets''')