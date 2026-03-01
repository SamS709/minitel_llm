```
+===========================================================================+
|              M   M  III  N   N  III   CCC  H   H   A   TTTTT              |
|              MM MM   I   NN  N   I   C     H   H  A A    T                |
|              M M M   I   N N N   I   C     HHHHH AAAAA   T                |
|              M   M  III  N   N  III   CCC  H   H A   A   T                |
+===========================================================================+
```  
<img src = "images/global.png" width = 400/>

Le but du projet est de pouvoir display une interface pour parler à un LLM sur Minitel.

Matériel requis:

- un **ordi** avec ollama installé
- une **raspberry** avec port usb et wifi
- un **minitel** 
- un **adaptateur** dim 5 broches -> usb


# 1] Configuration

## Le Minitel

**ATTENTION**, le Minitel doit avoir:
- un touche `Fnct`
- une prise dim 5 broches

## L'adaptateur

Il existe des ressources pour construire son adaptateur:
- https://pila.fr/wordpress/?p=361
- ...

J'ai opté pour la méthode du flemmard: ['toutelectrique46'](https://toutelectrique46.tk/) fournit l'adaptateur déjà assemblé.

## L'ordi

Testé sur ubuntu 24.04

## La raspberry

Testé sur ubuntu 22.04

## Installation du projet

Ollama doit être installé sur votre Ordi.

```bash
git clone https://github.com/SamS709/minitel_llm.git
```

Préférez un environnement python virtuel sous python=3.10

```bash
pip install ollama
```

# 2] Connexion ordi -> Minitel

Avant de se lancer dans la configuration Minitel<-Raspberry->Ordi, on va faire les choses plus simplement pour tester si cela fonctionne: Ordi->Minitel

Recette:
1. Brancher l'ordi au Minitel (avec l'adapteteur)
2. Combinaisons de touches sur le Minitel:
    - `Fcnt-T` (ensemble) PUIS `A` (passer le Minitel du mode vidéotex au mode péri-informatique)
    - `Fcnt-T` (ensemble) PUIS `E` (supprimer l'écho local des touches)
    - `Fcnt-P` (ensemble) PUIS `4` (passer la vitesse de transmission à 4800 bauds)
3. Détecter sur quel port usb est branché le minitel (moi c'est ttyUSB0 -> remplacez par le votre par la suite)
4. Tester le câble: 
    ```bash
    stty -F /dev/ttyUSB0 1200 cs7 parenb -parodd -cstopb
    echo "Hellow World" > /dev/ttyUSB0
    ```
    Vous devriez voir s'afficher Hello World à l'écran du Minitel.
5. Ouvrir un terminal sur le Minitel:
    ```bash
    sudo agetty -L ttyUSB0 4800
    ```
    Le display du login peut ne pas s'afficher correctement, ce n'est pas grave, cela se résout tout seul par la suite.
6. (Optionnel) Tester **Minichat** sur le Minitel depuis l'ordi:  
Depuis le Minitel:
    ```bash
    cd minitel_llm
    python main.py
    ```
<img src = "images/minichat.png" width = 200/>


# 3] Connexion raspberry pi -> Minitel

Globalement c'est la même chose, on va juste automatiser la connexion de la raspberry au minitel au démarrage et l'affichage du terminal sur le Minitel. 


Recette:
1. Brancher la Raspberry au Minitel (avec l'adapteteur)
2. Combinaisons de touches sur le Minitel:
    - `Fcnt-T` (ensemble) PUIS `A` (passer le Minitel du mode vidéotex au mode péri-informatique)
    - `Fcnt-T` (ensemble) PUIS `E` (supprimer l'écho local des touches)
    - `Fcnt-P` (ensemble) PUIS `4` (passer la vitesse de transmission à 4800 bauds)
3. Détecter sur quel port usb est branché le minitel (moi c'est ttyUSB0 -> remplacez par le votre par la suite)
4. Automatiser la connexion de la raspberry au Minitel:
    ```bash
    sudo nano /etc/systemd/system/minitel.service
    ```
    Une fois dans le fichier (remplacer ttyUSB0 par votre port):
    ```
    [Unit]
    Description=Minitel Getty on ttyUSB0
    After=dev-ttyUSB0.device
    Requires=dev-ttyUSB0.device

    [Service]
    ExecStart=/sbin/agetty -L ttyUSB0 4800
    Restart=always
    RestartSec=2

    [Install]
    WantedBy=multi-user.target

    sudo systemctl daemon-reload
    sudo systemctl enable minitel.service

    sudo systemctl start minitel.service
    sudo systemctl status minitel.service
    ```
5. Attention, pour que la **connexion automatique** fonctionne, il faut d'abord **allumer le minitel, puis la raspberry**. Il faut par ailleurs à chaque démarrage du Minitel, efcfectuer la combinaison de touches, car il ne possède pas de mémoire.  

<img src = "images/pi.png" width = 200/>  

# 4] Connexion Minitel->ordi 

Pour utiliser un LLM, nous avons besoin des ressources de l'ordi utilisé au 2] (la raspberry ne suffit pas)

Pour se faire:
1. Démarrer le Minitel + combinaisons de touches
2. Démarrer la raspberry (la brancher) -> le terminal devrait s'afficher sur le Minitel
3. A partir du Minitel, ssh dans l'ordi.
4. Exécuter le code python commme montré au 2]6.

# Sources et liens utiles

### Config miitel / ordi
- https://www.furrtek.org/index.php?a=telinux
- https://lea-linux.org/documentations/Utilisation_d%27un_Minitel_comme_terminal
- https://pila.fr/wordpress/?p=361
- https://x0r.fr/blog/5

### Achat câble(s)
- https://toutelectrique46.tk/
- https://www.tindie.com/stores/iodeo/ (souvent en rupture de stock)



