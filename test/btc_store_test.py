# Main script to test BTCHeaderStore contract. 
#
# @author Bon Filey <bon@bromleylabs.io>
# @author Anurag Gupta <anurag@bromleylabs.io>
#
# Copyright (c) 2018 Bromley Labs Inc.        

from hexbytes import HexBytes
from bitstring import BitArray
import hashlib
import sys, os
import re
from utils import *
import utils
from web3.auto import w3
from btc_utils import *

GAS_PRICE = int(2.5*1e9) 
GAS = int(4*1e6)
BUILD_DIR = '../contracts/target'
STORE_ABI = os.path.join(BUILD_DIR, 'BTCHeaderStore.abi')
STORE_BIN = os.path.join(BUILD_DIR, 'BTCHeaderStore.bin')
LOGFILE = '/tmp/snark.log'
HEADERS_DATA = './data/btc_headers'

logger = None

# @param contract Contract instance of BTC Headers Contract
def store_header(block_number, headers_file, contract, txn_params, w3):
    _, bbytes = get_header(block_number, headers_file) 
    txn_hash = contract.store_block_header(bbytes, block_number, 
                                           transact = txn_params) 

    status, txn_receipt = wait_to_be_mined(w3, txn_hash)
    logger.info(txn_receipt)

# @param txn_params dict containing 'from', 'gas', 'gasPrice'
def deploy_and_init(w3, ABI, BIN, txn_params):     
    contract_addr = deploy(w3, ABI, BIN, txn_params['from'] , txn_params['gas'],
                           txn_params['gasPrice'])
    if contract_addr is None:
        return None, None
    logger.info('Contract address = %s' % contract_addr)

    _, concise = init_contract(w3, ABI, contract_addr)
 
    return concise, contract_addr

# @dev set mutual addresses in each contracts as they interact
def set_address(contract, addr, txn_params, w3):
    logger.info('Setting verifier address in headers contract')
    txn_hash = contract.set_verifier_addr(addr, transact = txn_params)
    status, txn_receipt = wait_to_be_mined(w3, txn_hash)
    logger.info(txn_receipt)

def main():
    if len(sys.argv) != 4:
        print('Usage: python %s <b2> <b1> <b0>' % sys.argv[0])
        print('bn: block numbers in sequencial order highest first')
        exit(0)
    global logger

    logger = init_logger('TEST', LOGFILE)
    utils.logger = logger 

    block2 = int(sys.argv[1])
    block1 = int(sys.argv[2])
    block0 = int(sys.argv[3])

    txn_params = {'from': w3.eth.accounts[0], 
                  'gas': GAS, 
                  'gasPrice': GAS_PRICE}

    contract, _ = deploy_and_init(w3, STORE_ABI, STORE_BIN, 
                                          txn_params)     
    if contract is None:
        logger.error('Could not deploy contract')
        return 1
    addr = '0x5F088c6280354a62eAeeB6643Adc783Ff0c9F528'  # Some dummy addr
    set_address(contract, addr, txn_params, w3)

    store_header(block2, HEADERS_DATA, contract, txn_params, w3) 
    store_header(block1, HEADERS_DATA, contract, txn_params, w3) 
    store_header(block0, HEADERS_DATA, contract, txn_params, w3) 

    return 0

if __name__== '__main__':
    main()
