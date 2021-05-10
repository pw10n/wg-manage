# wg-manage
Scripts to provision clients for Wireguard. Written to run on the same Linux box as the Wireguard server.

## prerequisites
 * wireguard - installed, configured and running.
 * qrencode - installed.

## limitations
 * currently only supports /24

## setup
1. Create a directory called `server` and a directory called `clients`
2. In the `server` directory, create a file called `publickey` containing the server's publickey
3. In the `server` directory, create a file called `endpoint` containing the server's endpoint (eg. some.server.com:51820)
4. Create a file called `lastip` with the starting ip number you want. (eg. putting 0 in the file will start with 10.18.0.1 for the first client)

## usage
`python3 create-client.py my-client`
This creates a new directory `clients/my-client` containing they keys, a qr png (for a mobile client to scan), and a config file (for all other clients).