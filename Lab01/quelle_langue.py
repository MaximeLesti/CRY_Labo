# Fait avec ChatGPT
import numpy as np
from collections import Counter

# Corpus de fréquences des lettres pour le français et l'anglais
freq_fr = np.array([0.149, 0.085, 0.081, 0.038, 0.140, 0.011, 0.064, 0.032, 0.091, 0.004, 0.027, 0.025, 0.084, 0.065, 0.072, 0.046, 0.043, 0.078, 0.022, 0.066, 0.061, 0.090, 0.010, 0.002, 0.003, 0.000])
freq_en = np.array([0.127, 0.091, 0.081, 0.040, 0.131, 0.023, 0.020, 0.060, 0.068, 0.002, 0.022, 0.060, 0.091, 0.030, 0.075, 0.028, 0.014, 0.060, 0.080, 0.085, 0.019, 0.002, 0.010, 0.001, 0.001, 0.000])

def calculate_chi_square(observed, expected):
    chi_square = 0
    for o, e in zip(observed, expected):
        if e > 0:  # Eviter la division par zéro
            chi_square += ((o - e) ** 2) / e
    return chi_square


def identify_language(text):
    # Normaliser le texte (en minuscules et sans caractères non alphabétiques)
    text = text.lower()
    letters = [ch for ch in text if ch.isalpha()]
    
    if len(letters) < 50:
        return "Texte trop court"
    
    # Compter les lettres dans le texte
    letter_count = Counter(letters)
    
    # Calculer la fréquence des lettres dans le texte
    total_letters = sum(letter_count.values())
    letter_freq = np.array([letter_count.get(chr(i + ord('a')), 0) / total_letters for i in range(26)])
    
    # Calculer le test du χ² pour les deux langues
    chi_fr = calculate_chi_square(letter_freq, freq_fr)
    chi_en = calculate_chi_square(letter_freq, freq_en)
    
    
    # Retourner la langue selon le chi carré le plus bas
    if chi_fr > chi_en:
        return "Français"
    elif chi_fr < chi_en:
        return "Anglais"
    else:
        return "Indéterminé"  # Si les valeurs sont trop proches l'une de l'autre

# Test avec un exemple
texte_exemple_en = "La vie est belle quand on prend le temps de profiter des petites choses."
texte_exemple_fr = "Life is beautiful when you take the time to enjoy the little things."

resultat_fr = identify_language(texte_exemple_fr)
resultat_en = identify_language(texte_exemple_en)

print(f"Langue du texte français : {resultat_fr}")
print(f"Langue du texte anglais : {resultat_en}")
