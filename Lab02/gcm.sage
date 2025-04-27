from Crypto.Cipher import AES
from Crypto.Util import strxor
from Crypto import Random
import hashlib
import base64


BLOCK_SIZE = 16
IV_SIZE = 12
COUNTER_SIZE = BLOCK_SIZE - IV_SIZE


def xor(a,b):
    return strxor.strxor(a,b)

#Converts a 128 bit string into a polynomial in GF(2^128) 
#x has to be the unknown in the polynomial. 
def strToPoly(s,x):
    if len(s) != BLOCK_SIZE:
        raise Exception("Need " + str(BLOCK_SIZE) + " bytes string")
    res = 0
    for i in range(BLOCK_SIZE):
        res *= x^8
        temp = s[i]
        for j in range(8):
            res += x^j* ((temp >>j)&1)
    return res

#Converts a polynomial in GF(2^128) into a 128 bitstring
def polyToStr(p):
    coefs = p.polynomial().coefficients(sparse=False)
    coefs.reverse()
    res = 0
    for c in coefs:
        res*= 2
        if c == 1:
            res += 1 
    resStr  = b""
    for i in range(BLOCK_SIZE):
        resStr = (int(res & 0xff)).to_bytes(1,"little") + resStr
        res = res >> 8
    return resStr

#Multiply the 128bit string by the polynomial H. 
#Returns a 128bit-string 
def multByH(b,H,x):
    p = strToPoly(b,x)
    return polyToStr(p*H)

#Increases by 1 ctr which is a bitstring counter. 
def increaseCounter(ctr):
    ctr_int = int.from_bytes(ctr, "big")
    ctr_int += 1
    return int(ctr_int).to_bytes(BLOCK_SIZE, byteorder="big")

# Convert python bytes to GCM NIST format
# The inverse of this function is f itself
def f(x):
    b = '{:0{width}b}'.format(int.from_bytes(x, 'little'), width=128)
    return int(b[::-1], 2).to_bytes(16, 'little')

def authenticate(key, ct, T):
    if len(ct)% BLOCK_SIZE != 0:
        raise Exception("Error: the content to authenticate need to have a length multiple of the blocksize")
    cipher = AES.new(key, AES.MODE_ECB)
    G.<y> = PolynomialRing(GF(2)) #Ring of polynomials over Z_2
    F.<x> = GF(2^128, modulus = y^128 + y^7 + y^2 + y + 1) #GF(2^128) with the GCM modulus
    H = strToPoly(f(cipher.encrypt(b"\x00"*BLOCK_SIZE)), x) 
    tag = b"\x00"*BLOCK_SIZE
    for i in range(len(ct)//BLOCK_SIZE):
        tag = xor(tag, f(ct[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)]))
        tag = multByH(tag, H, x)
    tag = xor(tag, f(T))
    return f(tag) #La fonction f est appelée pour avoir le bon format. 


def CTR(key, IV, m):
    cipher = AES.new(key, AES.MODE_ECB)
    if len(m)%BLOCK_SIZE != 0:
        raise Exception("ERROR: the message length has to be a multiple of the block size")
    ctr = (IV + b"\x00"*(COUNTER_SIZE-1)+b"\x02") 
    ciphertext = []
    for i in range(len(m)//BLOCK_SIZE):
        #Encrypt bloc
        current = m[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)]
        res = xor(current, cipher.encrypt(ctr))
        ciphertext.append(res)
        ctr = increaseCounter(ctr)
    return b"".join(ciphertext)



#Performs the GCM Encryption function whithout AD
#m the message to encrypt. It has to be a multiple of 128 bits. 
#Returns a ciphertext and a tag
def GCM_Encrypt(key, IV, m):
    ciphertext = CTR(key, IV, m)
    cipher = AES.new(key, AES.MODE_ECB)
    tag = authenticate(key, ciphertext, cipher.encrypt((IV + b"\x00"*(COUNTER_SIZE -1) + b"\x01")))
    return (ciphertext, tag)

def GCM_Decrypt(key, IV, ct, tag):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = CTR(key, IV, ct)
    tag_check = authenticate(key, ct, cipher.encrypt((IV + b"\x00"*(COUNTER_SIZE -1) + b"\x01")))
    if(tag != tag_check):
        raise Exception("ERROR: Tag incorrect")
    return plaintext


def test_GCM():
    import os
    # Génération de la clé et de l'IV
    key = os.urandom(BLOCK_SIZE)
    IV = os.urandom(IV_SIZE)
    # Message doit être multiple de BLOCK_SIZE
    message = b"Ceci est un test de chiffrement GCM!" + b"\x00" * (BLOCK_SIZE - (len(b"Ceci est un test de chiffrement GCM!") % BLOCK_SIZE))
    print("Message original:", message)
    # Chiffrement
    ct, tag = GCM_Encrypt(key, IV, message)
    print("Chiffrement réussi. \nCiphertext:", ct.hex())
    print("Tag:", tag.hex())
    # Déchiffrement
    decrypted = GCM_Decrypt(key, IV, ct, tag)
    if decrypted:
        print("Déchiffrement réussi. \nMessage:", decrypted)
        assert decrypted == message, "Le message déchiffré ne correspond pas au message original!"
        print("Test réussi : Le message initial et le message déchiffré sont identiques.")
    else:
        print("Échec du déchiffrement ou message falsifié.")




def break_GCM_with_identique_IV(m1, iv, c1, t1, c2, t2):
    if len(m1)%BLOCK_SIZE != 0 or len(c1)%BLOCK_SIZE != 0 or len(c2)%BLOCK_SIZE != 0:
        raise Exception("ERROR: the message length has to be a multiple of the block size")
    plaintext = []
    for i in range(len(m1)//BLOCK_SIZE):
        Ek = xor(m1[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)], c1_binaire[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)])
        plaintext.append(xor(c2[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)], Ek))
    


    return b"".join(plaintext)

def break_GCM_integrity(m1, t1, c1, iv, mChall):
    if len(m1)%BLOCK_SIZE != 0 or len(c1)%BLOCK_SIZE != 0 or len(m1) < len(mChall):
        raise Exception("ERROR: problem of text size")
    ciphertext = []
    for i in range(len(mChall)//BLOCK_SIZE):
        Ek = xor(m1[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)], c1_binaire[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)])
        ciphertext.append(xor(mChall[BLOCK_SIZE*i: BLOCK_SIZE*(i+1)], Ek))
    

    return base64.b64encode(b"".join(ciphertext))

test_GCM()
m1 = b'This is a Test !'
iv_binaire = base64.b64decode(b'XCxpa/Kra6qi78G/')
c1_binaire = base64.b64decode(b'qVn/hjPI/voP3q2T5Jjrug==')
t1_binaire = base64.b64decode(b'cyVkbTE867/u/+ifbqolFg==')
c2_binaire = base64.b64decode(b'rVDlhjOcrbcLk5aE/pau6A==')
t2_binaire = base64.b64decode(b'aFH9iMJiXDNYKvrn19+c5w==')
mChall = b'100.00CHF to ADC'

print(break_GCM_with_identique_IV(m1, iv_binaire, c1_binaire, t1_binaire, c2_binaire, t2_binaire))

print(break_GCM_integrity(m1, t1_binaire, c1_binaire, iv_binaire, mChall))
