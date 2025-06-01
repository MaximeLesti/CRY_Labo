from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode

def encrypt(m, key):
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(m)


def keygen():
    phi = 65537
    e = 65537
    n = 1
    while gcd(phi, e) != 1:
        n = 1
        phi = 1
        p = random_prime(2^1048)
        q = next_prime(p + ZZ.random_element(2^15)) #to ensure that both primes have similar sizes
        n = p*q
        phi = (p-1)*(q-1)
    return RSA.construct((int(n), int(e), int(inverse_mod(e,phi))), consistency_check=True)
    

def decrypt(c, key):
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(c)

def test():
    message = b"Hello Teacher"
    print("Message original: ", message)
    key = keygen()         
    pub_key = key.publickey()

    #Chiffrement
    c = encrypt(message, pub_key)
    print(c)

    #Déchiffrement
    d = decrypt(c, key)
    print(d)

def break_rsa():
    key_compressed = b'-----BEGIN PUBLIC KEY-----\nMIIBJzANBgkqhkiG9w0BAQEFAAOCARQAMIIBDwKCAQYitCZ29wPq+/L/JVHTNyyj\nij8tPEhKjqD082utm8sQjzvHlKFHE1upCymZoocpSg+aFEnW3uLwFZjhmJkAMkR8\nRXEzemDMM3nJ2jbypHMWOmU9/5719mMAl3P7TOKEkd7gnvf1sJntA1YD7SfzfJLJ\n5sJnBJLaY3cgh3TQJmAkZapgcylWqEGdNujvE3P9SW40C3IWehDpKO3QnwW1m27E\n0GPfgSsOhHQA0ZKFePUSFswMc/zbLiLAJJavSYfRbmGu4QoZqRqTAN4zH9gYoX31\nMH18h+ZbMz4NBdsMYVv08tJkmDp+0LWU67raglAAivn0VpyYgoJMkNVoOd9HOSLC\nJnktUKuxAgMBAAE=\n-----END PUBLIC KEY-----'
    c_compressed = b'AxgUKxEsOYS3Upx3ChChKlHA2y7lxpK/NQH1xfDSXOnR6bE5h7G30Dk6dERnoZzwW8EH9FIIPb2K/ZK9nnoMogBc8UCIwN/Xpue5+3eSqeox2icy6loa2gIB/Om0YXTIbGMGrN/Kh1NO8J0V0LEfRGSPgSu0yr2WjG1/Wy3AGkOUPHvjnVkMae0VOq6OuNwcCBqrV6VqVF9HR3MaDeYBsYlJrULqd0EAHLlmm46rAQtuixB556PlJciGrrf5K8drGrveMeL52f3zdsfHmgJI6NVMBkzBgDQDIbKtExX4MOsC0fhYkgQIue72xOWVqhsq5f7pmdHC2mXuer76XxegRNnD3LEUZA=='
    key = RSA.import_key(key_compressed)
    c = b64decode(c_compressed)

    e = key.e
    n = key.n

    #Attaque de Fermat
    a = ceil(sqrt(n))
    b2 = a**2 -n
    while not is_square(b2):
        a+=1
        b2 = a**2 -n
    b = sqrt(b2)
    p = a - b
    q = a + b

    #Calculer la valeur de d, la clé de déchiffrement
    phi = (p-1)*(q-1)
    d = inverse_mod(e, phi)

    #Reconstruire la clé
    private_key = RSA.construct((int(n), int(e), int(d), int(p), int(q)), consistency_check=True)
    #Déchiffrement
    plain_text = decrypt(c, private_key)

    print(plain_text)





def main():
    #test()
    break_rsa()

main()
