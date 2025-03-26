# Maxime Lestiboudois


# IMPORTANT
# IL EST PRIMORDIAL DE NE PAS CHANGER LA SIGNATURE DES FONCTIONS
# SINON LES CORRECTIONS RISQUENT DE NE PAS FONCTIONNER CORRECTEMENT

url = "https://www.gutenberg.org/cache/epub/17949/pg17949.txt"
import requests

def addition_lettre_vigenere(a, b):
    positionA = ord(a) - ord('a')  
    positionB = ord(b) - ord('a')

    nouvelle_position = (positionA + positionB) % 26

    resultat_lettre = chr(nouvelle_position + ord('a'))
    return resultat_lettre

def soustraction_lettre_vigenere(a, b):
    positionA = ord(a) - ord('a')  
    positionB = ord(b) - ord('a')

    nouvelle_position = (positionA - positionB) % 26

    resultat_lettre = chr(nouvelle_position + ord('a'))
    return resultat_lettre

def addition_lettre_caesar(a, b):
    positionA = ord(a) - ord('a')

    nouvelle_position = positionA + b 
    nouvelle_position %= 26

    resultat_lettre = chr(nouvelle_position + ord('a'))
    return resultat_lettre


def caesar_encrypt(text, key):
    """
    Parameters
    ----------
    text: the plaintext to encrypt
    key: the shift which is a number

    Returns
    -------
    the ciphertext of <text> encrypted with Caesar under key <key>
    """
    
    clean_text = sanitize_text(text)

    result = ""
    for i in range(0, len(text)):
        result += addition_lettre_caesar(text[i], key)

    return result


def caesar_decrypt(text, key):
    """
    Parameters
    ----------
    text: the ciphertext to decrypt
    key: the shift which is a number

    Returns
    -------
    the plaintext of <text> decrypted with Caesar under key <key>
    """
    clean_text = sanitize_text(text)

    result = ""
    for i in range(0, len(clean_text)):
        result += addition_lettre_caesar(clean_text[i], -key)

    return result

def occurence_analysis(text):
    occurence_vector = [0] * 26
    for i in text:
        position = ord(i) - ord('a')
        occurence_vector[position] +=1

    return occurence_vector

def freq_analysis(text):
    """
    Parameters
    ----------
    text: the text to analyse

    Returns
    -------
    list
        the frequencies of every letter (a-z) in the text.

    """
    # Each value in the vector should be in the range [0, 1]
    freq_vector = [0] * 26
    clean_text = sanitize_text(text)
    text_size = len(clean_text)
    for i in clean_text:
        position = ord(i) - ord('a')
        freq_vector[position] +=1

    for i in range(26):
        freq_vector[i] /= text_size

    return freq_vector


def caesar_break(text, ref_freq):
    """
    Parameters
    ----------
    text: the ciphertext to break
    ref_freq: the output of the freq_analysis function on a reference text

    Returns
    -------
    a number corresponding to the caesar key
    """
    clean_text = sanitize_text(text)
    chi_carre = [0]*26
    
    for n0_decalage in range(26):
        Oi = freq_analysis(caesar_decrypt(clean_text, n0_decalage))   
        for lettre in range(26):
            chi_carre[n0_decalage] += ((Oi[lettre] - ref_freq[lettre])**2)/ref_freq[lettre]
    
    decal_opti = 0
    for i in range(26):
        if chi_carre[decal_opti] > chi_carre[i]:
            decal_opti = i

    return decal_opti


def vigenere_encrypt(text, key):
    """
    Parameters
    ----------
    text: the plaintext to encrypt
    key: the keyword used in Vigenere (e.g. "pass")

    Returns
    -------
    the ciphertext of <text> encrypted with Vigenere under key <key>
    """
    sizeKey = len(key)
    
    clean_text = sanitize_text(text)

    result = ""
    for i in range(0, len(clean_text)):
        result += addition_lettre_vigenere(clean_text[i], key[i%sizeKey])

    return result


def vigenere_decrypt(text, key):
    """
    Parameters
    ----------
    text: the ciphertext to decrypt
    key: the keyword used in Vigenere (e.g. "pass")

    Returns
    -------
    the plaintext of <text> decrypted with Vigenere under key <key>
    """
    clean_text = sanitize_text(text)
    reponse = ""
    for i in range(len(clean_text)):
        reponse += soustraction_lettre_vigenere(clean_text[i], key[i%len(key)])
    return reponse


def coincidence_index(text):
    """
    Parameters
    ----------
    text: the text to analyse

    Returns
    -------
    the index of coincidence of the text
    """
    clean_text = sanitize_text(text)
    N = len(clean_text)
    occurence_vector = occurence_analysis(clean_text)
    
    sum = 0
    for i in range(26):
        sum += occurence_vector[i]*(occurence_vector[i]-1)

    IC = 26 * sum / (N*(N-1))

    return IC

def vigenere_break(text, ref_freq, ref_ci):
    """
    Parameters
    ----------
    text: the ciphertext to break
    ref_freq: the output of the freq_analysis function on a reference text
    ref_ci: the output of the coincidence_index function on a reference text

    Returns
    -------
    the keyword corresponding to the encryption key used to obtain the ciphertext
    """
    clean_text = sanitize_text(text)
    ic_tab = [0] *20
    for l in range(1,21):
        sum_ci = 0
        for i in range(l):
            text_key = clean_text[i::l]
            sum_ci += coincidence_index(text_key)
        ic_tab[l-1] = sum_ci/l
    longueur_mot = 0
    for l in range(20):
        if (abs(ic_tab[l] - ref_ci)  < abs(ic_tab[longueur_mot] - ref_ci)):
            longueur_mot = l
    longueur_mot += 1

    key = ""
    for m in range(longueur_mot):
        text_par_lettre = clean_text[m::longueur_mot]
        decalage = caesar_break(text_par_lettre, ref_freq)
        key += chr(decalage +ord("a"))

    return key


def vigenere_improved_encrypt(text, key):
    """
    Parameters
    ----------
    text: the plaintext to encrypt
    key: the keyword used in Vigenere (e.g. "pass")
    
    Returns
    -------
    the ciphertext of <text> encrypted with improved Vigenere under key <key> 
    """
    clean_text = sanitize_text(text)
    cypher_text=""
    sizeKey = len(key)
    keyPlusOne = key
    nb_block = len(clean_text)/sizeKey 
    nb_block_theorie = len(clean_text)//sizeKey
    if( nb_block != nb_block_theorie):
        nb_block += 1
    
    nb_block = int(nb_block)

    for i in range(nb_block):
        cypher_block = vigenere_encrypt(clean_text[i*sizeKey:i*sizeKey+sizeKey:],keyPlusOne)
        cypher_text += cypher_block
        keyPlusOne = vigenere_encrypt(keyPlusOne, cypher_block)

    return cypher_text


def vigenere_improved_decrypt(text, key):
    """
    Parameters
    ----------
    text: the plaintext to decrypt
    key: the keyword used in Vigenere (e.g. "pass")
    
    Returns
    -------
    the plaintext of <text> decrypted with improved Vigenere under key <key>
    """
    clean_text = sanitize_text(text)
    plain_text=""
    sizeKey = len(key)
    keyPlusOne = key
    nb_block = len(clean_text)/sizeKey 
    nb_block_theorie = len(clean_text)//sizeKey
    if( nb_block != nb_block_theorie):
        nb_block += 1
    
    nb_block = int(nb_block)
    for i in range(nb_block):
        plain_block = vigenere_decrypt(clean_text[i*sizeKey:i*sizeKey+sizeKey:],keyPlusOne)
        plain_text += plain_block
        keyPlusOne = vigenere_encrypt(keyPlusOne, clean_text[i*sizeKey:i*sizeKey+sizeKey:])



    return plain_text


def vigenere_improved_break(text, ref_freq, ref_ci):
    """
    Parameters
    ----------
    text: the ciphertext to break
    ref_freq: the output of the freq_analysis function on a reference text
    ref_ci: the output of the coincidence_index function on a reference text

    Returns
    -------
        the keyword corresponding to the key used to obtain the ciphertext
    """
    key = ""
    clean_text = sanitize_text(text)

    
    vigenere_texts = [""]*20
    # Soit blocksize+1 la taille des blocs (soit la taille de la clé)
    #trouver les textes selon les différentes tailles de block (contenus dans le tableau vigenere_texts)
    for blocksize in range(20):
        vigenere_text=""
        nbBlock = len(clean_text) // (blocksize + 1)
        if nbBlock == 0:
            break
        elif len(clean_text) / (blocksize+1) > nbBlock:
            nbBlock += 1
        
        for i in range(nbBlock):
            block = clean_text[i*(blocksize+1):(blocksize+1)*i + blocksize + 1:]
            for j in range(i):
                block = vigenere_decrypt(block, clean_text[j*(blocksize+1):(blocksize+1)*j + blocksize + 1:])
            vigenere_text += block
        vigenere_texts[blocksize] = vigenere_text

    while "" in vigenere_texts:
        vigenere_texts.remove("")

    ci_tab = [0]*len(vigenere_texts)
    i = 0

    for text_possible in vigenere_texts:
        key_possible = vigenere_break(text_possible, ref_freq, ref_ci)
        plain_possible_text = vigenere_decrypt(text_possible, key_possible)
        ci_tab[i] = coincidence_index(plain_possible_text)
        i+=1

    longueur_mot = 0

    for i in range(len(ci_tab)):
        if (abs(ci_tab[i] - ref_ci)  < abs(ci_tab[longueur_mot] - ref_ci)):
            longueur_mot = i

    longueur_mot += 1

    key = ""
    for m in range(longueur_mot):
        text_par_lettre = vigenere_texts[longueur_mot-1][m::longueur_mot]
        decalage = caesar_break(text_par_lettre, ref_freq)
        key += chr(decalage +ord("a"))

    return key


# convertir le texte pour qu'il n'y ait plus de caractères spéciaux 
    # et qu'il soit en minuscule
def sanitize_text(text):
    clean_text = text.lower()

    #Enlever les é
    index = clean_text.find("é")
    while(index !=-1):
        clean_text = clean_text[:index] + "e" + clean_text[index+1:]
        index = clean_text.find("é")
    #Enlever les è
    index = clean_text.find("è")
    while(index !=-1):
        clean_text = clean_text[:index] + "e" + clean_text[index+1:]
        index = clean_text.find("è")
    #Enlever les ë
    index = clean_text.find("ë")
    while(index !=-1):
        clean_text = clean_text[:index] + "e" + clean_text[index+1:]
        index = clean_text.find("ë")
    #Enlever les à
    index = clean_text.find("à")
    while(index !=-1):
        clean_text = clean_text[:index] + "a" + clean_text[index+1:]
        index = clean_text.find("à")
    #Enlever les ç
    index = clean_text.find("ç")
    while(index !=-1):
        clean_text = clean_text[:index] + "c" + clean_text[index+1:]
        index = clean_text.find("ç")
    #Enlever les î
    index = clean_text.find("î")
    while(index !=-1):
        clean_text = clean_text[:index] + "i" + clean_text[index+1:]
        index = clean_text.find("î")
    #Enlever les ï
    index = clean_text.find("ï")
    while(index !=-1):
        clean_text = clean_text[:index] + "i" + clean_text[index+1:]
        index = clean_text.find("ï")
    #Enlever les ô
    index = clean_text.find("ô")
    while(index !=-1):
        clean_text = clean_text[:index] + "o" + clean_text[index+1:]
        index = clean_text.find("ô")
    #Enlever les û
    index = clean_text.find("û")
    while(index !=-1):
        clean_text = clean_text[:index] + "u" + clean_text[index+1:]
        index = clean_text.find("û")
    
    reponse = ""
    for i in clean_text:
        if 'a' <= i <= 'z':
             reponse += i
    
    
    return reponse

def recuperer_livre(url):
    livre = requests.get(url)
    livre.encoding = 'utf-8'

    if livre.status_code == 200:
        return livre.text
    else :
        return "error"


def main():
    
    text = recuperer_livre(url)
    E = freq_analysis(text)
    #Valeurs précalculées
    #E = [0.08776375862635759, 0.009701509014589675, 0.032020254307352246, 0.034675933535647435, 0.16859453850060227, 0.010782180331046056, 0.009604604322194609, 0.00986342571580675, 0.07700979105385693, 0.004837874769698026, 0.0013394927100685201, 0.05513509004776543, 0.026820520243267577, 0.07132921345282459, 0.05452422249317374, 0.02765586322454657, 0.010021662491996163, 0.0682417563546172, 0.07736429049818826, 0.07538326419163087, 0.058736510008169436, 0.017778944450305065, 0.0017038052878069363, 0.004181621473098521, 0.003097270231614481, 0.0018326026637750634]
    #F = 2.015474795510163

    F = coincidence_index(text)

    #################################
    ##########Tester CAESAR##########
    #################################

    print("TESTER CAESAR")
    print("Texte à chiffrer avec Caesar:\n", text)
    cypher_text = caesar_encrypt(text, 8)
    print("Texte à chiffré avec Caesar:\n", cypher_text)
    key = caesar_break(cypher_text, E)
    print("Clé cassant Caesar", key)
    print("Texte déchiffré par la clé: \n", caesar_decrypt(cypher_text, key))


    #################################
    #########Tester Vigenere#########
    #################################
    
    print("TESTER VIGENERE")
    vigenere_file = open("vigenere.txt", "r", encoding="utf-8")
    vigenere_text = vigenere_file.read()
    key = vigenere_break(vigenere_text, E, F)
    print("Clé cassant Vigenère:", key)
    print("Texte déchiffré par la clé: \n", vigenere_decrypt(vigenere_text, key))



    #################################
    ####Tester Vigenere Improved#####
    #################################

    vigenere_improved_file = open("vigenere_improved.txt", "r", encoding="utf-8")
    cypher_text_vigenere_improved = vigenere_improved_file.read()
    
    key = vigenere_improved_break(cypher_text_vigenere_improved, E, F)
    print("Clé cassant Vigenère Improved:", key)
    print("Texte déchiffré par la clé: \n", vigenere_improved_decrypt(cypher_text_vigenere_improved, key))
    











if __name__ == "__main__":
    main()

