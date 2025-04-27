Lestiboudois Maxime  
15/04/2025
# Rapport Laboratoire 2 Cryptographie

## Spongy AES
**1)** Schéma de la construction de spongy.py:
![sponge schéma](image-1.png)

Pour retrouver le message, nous utiliserons pour commencer l'output (hash) reçu. Nous savons que les 15 premiers bytes correspondent au qinze premier bytes au state (l'état) précédent la phase de squeezing. Sachant qu'un state contient 16 bytes, nous allons donc "brute forcé" le dernier byte. Pour cela, nous allons incrémenté la valeur du dernier byte, partant de 0, jusqu'à trouver sa réelle valeur. Nous saurons que nous l'avons trouvé quand, en ayant passé l'état dans le chiffrement AES, ses 15 premiers bytes seront identiques au bytes 15 à 29 de l'output (hash).  
Une fois le dernier state obtenu, nous allons le passer dans le déchiffrement AES. 

Nous obtenons le state 3 noté sur l'image ci-dessus.

Nous savons que notre message est composé des caractères suivants: "FLAG{}", avec 13 caractères entre les accolades. Sachant qu'un caractère équivaut à un byte, nous obtenons un total de 19 bytes dans notre message. Ce dernier étant supérieur à 15 bytes (la taille d'un bloc), nous savons qu'il y aura 2 blocs, le dernier étant complété avec du padding.  
Le padding prendra la forme suivante : "0x80"+ "0x00"*x, soit autant de zéro suivant "0x80" que nécessaire (x) pour compléter le bloc. 

Nous pouvons donc découper nos 2 blocs ainsi (les * remplaçant les caractères inconnus):
1.  FLAG{**********
2. ***}0x80 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00

Sachant que le state initial ne vaut que des 0, nous savons également que state 1 sera égal au premier bloc du message complété avec un 0.

Nous pouvons maintenant brute forcé nos messages. Comme il y a moins d'éléments à trouver pour le second message, nous commencerons par celui-ci.

Nous allons donc itérer sur les trois caractères manquants à l'aide d'une triple boucle for, entre les valeurs 32 et 127, qui sont les caractères. Pour chaque nouvelle combinaison, nous allons "xoré" le résultat du message avec le state 3, passé ce state (équivalent au state 2) dans le déchiffrement AES et comparer les 5 premiers bytes du résultat avec les 5 premiers bytes de l'état numéro 2. Si ces derniers sont équivalents, nous pouvons donc partir du principe que le second bloc du message a été trouvé. 
En sachant que le second bloc du message a été trouvé, nous connaissons donc également la valeur du sate numéro 2. Les 15 premiers bytes de ce state sont le premier bloc du message (sachant qu'il est inutile de faire un xor avec le state initial, ce dernier ne contenant que des zéros). 

Notre message est donc le suivant (découpé en deux blocs):  
b'FLAG{spectacula'
b'rly}\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

Soit **"FLAG{spectaculary}"**

## GCM
**1)** l'erreur est qu'il manque l'étape encadrée ci-dessous:

![alt text](image.png)

**3)** les IV1 et IV2 sont parfaitement identiques.

**4)** Nous utilisons le fait que les IV ainsi que les clés soient identiques pour pouvoir déchiffrer (récupérer) le texte du second message en clair. 

Voici le texte obtenu pour le second message chiffré:
```
b'Pass = memorizes'
```

En effet, nous pouvons grâce au premier message et son 
chiffrement, en les xorant, connaître le chiffrement opéré sur le plaintext pour le chiffrer. Grâce à ce chiffrement et le second ciphertext, en les xorant, nous pouvons récupérer le plaintext du second message. 
(fonction `break_GCM_with_identique_IV`)

**5)** 
À l'aide de la fonction `break_GCM_integrity` et de l'IV fourni dans le fichier de paramètres, nous pouvons déterminer que le texte chiffré en base64 correspondant au texte mChall serait le suivant:  
```
b'zAGm2yORzpIo3o2Zt62P2A=='
```
En ayant connaissance d'un texte clair, de son équivalent chiffré et de son IV, nous pouvons détourner le chiffrement afin de chiffrer un texte nous appartenant.


## Speck
**1)** 
Si l'IV tourne en boucle avec le message, il suffit de répérer la fin du message, comme nous savons qu'il s'agit de la séquence de 4 bytes composée uniquement de zéros. POur retrouver cette séquence, il suffit de prendre un bloc, le passer dans la "matrice" de déchiffrement de Speck (comme nous connaissons la clé) et de xoré ce résultat avec le bloc précédent. Si le résultat final n'est que des zéros, alors le prochain bloc est l'IV.

Nous partons cependant du principe que l'IV n'est donné qu'une fois au début de la transmission.

Nous savons que le message et la suite de 0 mis en boucle sont la séquence qui sera chiffrée.

On peut alors faire ce schéma:

![alt text](image-2.png)

ce schéma peut se simplifier, car nous savons que lorsqu'un bloc est xoré avec des 0, il reste identique:

![alt text](image-3.png)

Il faut alors de répérer un bloc de zéros. Pour cela, il faut prendre un bloc au hasard (excepté le bloc d'indice 0), le passer dans la fonction de déchiffrement Speck et xoré le résultat avec le bloc d'indice précédent. Si le résultat ne donne que des zéros, alors nous avons trouvé ce que nous cherchions.

Maintenant que nous connaissons l'indice i de notre bloc de zéro, nous pouvons trouvé le message:
Pour cela, il faut prendre le bloc chiffré d'indice i + 1 que notre bloc de zéro, le passer dans la fonction de déchiffrement Speck et xoré le résultat avec le le bloc chiffré d'indice i. Le résultat est le message recherché.


**2)** 
Voici le mot de passe trouvé:
```
b'w7wB'
```
Pour pouvoir le trouver, j'ai d'abord analysé le modèle de chiffrement. Je me suis rendu compte que:
```
c1 = Speck(c0 xor m0)
c2 = Speck(c1 xor m1)
c3 = Speck(c2 xor m0)
c4 = Speck(c3 xor m1)
etc.
```
ou cN, est le n-ième bloc du texte chiffré, Speck la fonction de chffriment, m0 le message recherché (le mot de passe) et m1 la suite de zéros suivant le message.

Nous remarquons ainsi que si deux blocs sont identiques et de parité inverse, nous pouvons établir la relation suivante:
```
si 
c1 = c4,  alors :
Speck(c0 xor m0) = Speck(c3 xor m1)
```
Nous pouvons donc déduire:
```
c0 xor m0 = c3 xor m1 
```
et en réarrangeant les éléments:
```
m0 xor m1 = c0 xor c3
```
Comme m1 ne vaut que des zéros:
```
m0 = c0 xor c3
```

Nous trouvons ainsi le mot de passe.

J'ai donc d'abord cherché toutes les pairs de blocs similaires existant dans le texte chiffré, et dont l'indice de position était de parité inverse.  
En ayant toutes ces paires, j'ai pu leur appliquer le raisonnement démontrer ci-dessus, et observer si tous les résultats étaient identiques, ce qui était le cas. J'ai donc ainsi pu déterminer le message, mot de passe, recherché.

Cette méthode n'est possible que parce que la séquence de texte clair est particulière avec le mot de passe et la suite de 0 venant directement après et le fait qu'elle tourne en boucle.



**3)** 
Non, car AES demande une taille de bloc de 16 bytes, au lieu de 4 ici avec Speck. Il faudrait alors ajouter du padding pour remplir chaque bloc ou concaténer le contenu clair.

L'attaque ici repose sur le fait de pouvoir repérer les blocs de zéros, avec AES, cette approche est fortement compromise car il est difficilement possible de voir/connaître les répétitions à cause de la taille des blocs. 




