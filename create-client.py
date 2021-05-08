from string import Template
import os
import sys
import argparse
import logging

from config import *

parser = argparse.ArgumentParser(description="generate wg client config")
parser.add_argument('name', help='name of client to create')
parser.add_argument('--dry-run', action='store_true', help="creates client config and increments IP but does not apply wg changes")
parser.add_argument('-d', action='store_true', help="enable debug logging")
args = parser.parse_args()

if args.d:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("starting w/ debug logging...")
    logging.debug(args)
else:
    logging.basicConfig(level=logging.INFO)

client_dir = os.path.join(clients_dir, args.name)
os.mkdir(client_dir)

def execute(cmd):
    if not args.dry_run:
        logging.debug(" $" + cmd)
        os.system(cmd)
    else:
        logging.info(" $" + cmd)

logging.debug("reading server pubkey...")
server_publickey_file = open(os.path.join(server_dir, pubkey_filename))
srv_pubkey = server_publickey_file.readline().rstrip()
server_publickey_file.close()

logging.debug("reading server endpoint...")
server_endpoint_file = open(os.path.join(server_dir, endpoint_filename))
srv_endpoint = server_endpoint_file.readline().rstrip()
server_endpoint_file.close()

logging.info("generating client keypair...")
os.system("cd " + client_dir + "; wg genkey | tee privatekey | wg pubkey > publickey")

logging.debug("reading client pubkey...")
pubkey_file = open(os.path.join(client_dir, pubkey_filename), "r")
pubkey = pubkey_file.readline().rstrip()
pubkey_file.close()

logging.debug("reading client privkey...")
privkey_file = open(os.path.join(client_dir, privkey_filename), "r")
privkey = privkey_file.readline().rstrip()
privkey_file.close()

logging.debug("reading lastip file...")
lastip_file = open("lastip", "r")
lastip = int(lastip_file.read())
lastip_file.close()

if lastip >= 254:
    logging.error("out of ips.")
    sys.exit(-1)

logging.debug("updating lastip file...")
ip = lastip+1

lastip_file = open("lastip", "w")
lastip_file.write(str(ip))
lastip_file.close()

clientip ="10.18.0." + str(ip) 

d = {
     "address": clientip + "/24",
     "privateKey": privkey,
     "serverPublicKey": srv_pubkey,
     "serverEndpoint": srv_endpoint
    }

logging.info("writing client config...")
with open('wg0-client.conf.template', 'r') as templateFile:
    template = Template(templateFile.read())
    clientConfig = template.substitute(d)
    with open(os.path.join(client_dir, client_config_filename), 'w') as clientConfigFile:
        clientConfigFile.write(clientConfig)

logging.info("generating client config qr...")
os.system("cd " + client_dir + "; qrencode -t png -o qr_config.png < " + client_config_filename)

logging.info("writing configuration to server...")
execute("sudo wg set wg0 peer {publickey} allowed-ips {clientip}".format(publickey=pubkey,clientip=clientip+"/32")) 

execute("sudo wg")
logging.info("saving server configuration...")
execute("sudo wg-quick save wg0")

logging.info("======================")
logging.info(" created new client w/ ip: " + clientip)
logging.info("======================")

os.system("cd " + client_dir + "; qrencode -t ansiutf8 < " + client_config_filename)