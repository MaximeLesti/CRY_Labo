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

    #state_init : state initial
    #state_1 : state après le xor entre le state_init et le premier bloc
    #state_2 state après avoir passé state_1 dans AES
    #state_3 state après le xor du state_2 et le second bloc
    state_init = b"0x00"*16

    hash_binaire = base64.b64decode(hash)
    outputsize = len(hash_binaire)
    zblocks = [hash_binaire[rate*i:rate*(i+1)] for i in range(outputsize//rate)]
    #print(zblocks[1])

    test_block= b"\x00"*16
    state_init = b"\x00"*16

    c = 0  # Début du bruteforce pour les caractères ASCII imprimables

    while test_block[:rate] != zblocks[1]:
        test_block = zblocks[0] + c.to_bytes(1, byteorder='big')
        test_block = permutation(test_block)
        c += 1
    state_3 = cipher.decrypt(test_block)
    state_3 = cipher.decrypt(state_3)
    print(state_3)
    b0= b"FLAG{" + b"\x00"*10 # equivalent à "FLAG{0000000000"
    b1_end = b"}" + b"\x80"+b"\x00"*10  # equivalent à "}800000000000"
    b1 = b"\x00"*15
    state_1 = strxor(state_init[:15], b0)+ state_init[15:]

    for x1 in range(32, 127):
        for x2 in range(32, 127):
            for x3 in range(32, 127):
                x1x2x3 = x1.to_bytes(1, byteorder='big') + x2.to_bytes(1, byteorder='big') + x3.to_bytes(1, byteorder='big')
                b1 = x1x2x3 + b1_end
                state_2 = strxor(state_3[:rate], b1) + state_3[rate:]
                state_1_pot = cipher.decrypt(state_2)
                if(state_1_pot[:5] == state_1[:5]): # and state_1_pot[rate:] == state_1[rate:]):
                    break
            if(state_1_pot[:5] == state_1[:5]): # and state_1_pot[rate:] == state_1[rate:]):
                    break
        if(state_1_pot[:5]== state_1[:5]): # and state_1_pot[15:] == state_1[rate:]):
                    break
    state_2 = strxor(state_3[:15], b1)+ state_3[rate:]
    state_1 = cipher.decrypt(state_2)

    b0 = strxor(state_init[:rate], state_1[:rate])

    print(b0)
    print(b1)






        



sponge_break(b'ZeSuX70wt/Ym0Bwa3BSq9qHjVpAxEFhrtlXAFpdjK2igvgztDfgGrSFzCr8rZ10hmnY4OvB4669oXEgClmr/KA==')


