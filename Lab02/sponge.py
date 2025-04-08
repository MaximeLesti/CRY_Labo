from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor
import base64

rate = 15
cipher = AES.new(b"\x07"*16, AES.MODE_ECB)
def permutation(b):
    return cipher.encrypt(b)

def pad(message, rate):
    missing = rate - len(message)% rate
    if missing == 0: 
        missing = rate
    message += b"\x80" + b"\x00"*(missing - 1)
    return message 

#Hashes the message to a specific output_size
def sponge(rate, message, output_size):
    #padding
    message = pad(message, rate)
    
    blocks = [message[rate*i:rate*(i+1)] for i in range(len(message)//rate)]
    state = b"\x00"*16
    #absorbing
    for b in blocks:
        state = strxor(state[:rate], b) + state[rate:]
        state = permutation(state)
    #squeezing
    hash  = b""
    while len(hash) < output_size:
        hash += state[:rate]
        state = permutation(state)
    return hash[:output_size]


def sponge_break(hash):
    b1_onConnait = b"{"+b"0x80"+b"0x00"*10
    state_init = b"0x00"*16

    hash_binaire = base64.b64decode(hash)
    outputsize = len(hash_binaire)
    zblocks = [hash_binaire[rate*i:rate*(i+1)] for i in range(outputsize//rate-1, -1, -1)]

    test_block= b"\x00"*16
    blockPlusUn = 1
    for b in zblocks:
        c = 0
        test_block  = b + c.to_bytes(1, byteorder='big')
        test_block = cipher.decrypt(test_block)
        while(test_block[:rate] != zblocks[blockPlusUn]):
            c+=1
            test_block  = b + c.to_bytes(1, byteorder='big')
            test_block = cipher.decrypt(test_block)
        blockPlusUn += 1

        b0= b"\x46"+b"\x4C"+ b"\x41"+b"\x47"+b"\x7B" + b"\x00"*10
        b1 = b"\x00"*3 + b"\x7D" + b"\x80"+b"\x00"*10
        state_1 = strxor(state_init[:rate], b0)+ state_init[rate:]
        state_2 = strxor(test_block[:rate], b1) + test_block[rate:]
        state_2_bis = cipher.encrypt(state_1) 
        while (state_2_bis[4:]!= state_2[4:]):
            b0 = b0[:-1] + bytes([b0[-1] + 1])
            state_1 = strxor(state_init[:rate], b0)+ state_init[rate:]
            state_2_bis = cipher.encrypt(state_1) 

        print(b0)
        state_1 = strxor(state_init[:rate], b0)+ state_init[rate:]



sponge_break(b'ZeSuX70wt/Ym0Bwa3BSq9qHjVpAxEFhrtlXAFpdjK2igvgztDfgGrSFzCr8rZ10hmnY4OvB4669oXEgClmr/KA==')


