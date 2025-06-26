from multiprocessing.context import DefaultContext
from typing import Match, Set
import wave
from multiprocessing import Process, process
import numpy
import struct
import tkinter as tk
from tkinter import filedialog,messagebox
from shutil import copy2
from functools import partial
import os
from tkinter.constants import END, FALSE, RIGHT, TRUE

try:
	import winsound
except ModuleNotFoundError:
	from playsound import playsound

class SetUp:
    alpabeto = ["a","à","b","c","ch","d","e","è","f","g","gh","i","ì","j","k","l","m","n","o","ò","p","q","r","s","t","u","ù","v","w","x","y","z"]
    vocali = ["a","à","e","è","i","ì","o","ò","u","ù"]
    accenti = ["à","è","ì","ò","ù","À","È","Ì","Ò","Ù"]
    punteggiatura = [" ",".",",","!","?",":",";","-","_"]
    speciali = [["♡","cuore"]]
    langages = ["ita","ita1"]
    def ControllaDirectory():
        #salva il path originale e i suoni da dividere
        OriginalDir = os.getcwd()
        LibrerieSuoniPath = OriginalDir + "/data/librerieSuoni"
        LibrerieSuoniScompostiPath = OriginalDir + "/data/suoni"
        TestiPath = OriginalDir + "/data/testi"
        FrasiPath = OriginalDir + "/data/frasi"

        if not os.path.exists(LibrerieSuoniPath):
            os.makedirs(LibrerieSuoniPath)
        if not os.path.exists(LibrerieSuoniScompostiPath):
            os.makedirs(LibrerieSuoniScompostiPath)
        if not os.path.exists(TestiPath):
            os.makedirs(TestiPath)
        if not os.path.exists(FrasiPath):
            os.makedirs(FrasiPath)
    
    def ControllaAudio(alpabeto):
        OriginalDir = os.getcwd()
        librerieDelSuono = os.listdir(OriginalDir + "/data/librerieSuoni")
        librerieDelSuonoGiaPresenti = os.listdir(OriginalDir + "/data/suoni")

        os.chdir(OriginalDir + "/data/suoni")
        for dir in librerieDelSuonoGiaPresenti:
            pass
        if len(librerieDelSuono) == len(librerieDelSuonoGiaPresenti):
            os.chdir(OriginalDir)
            return
        
        os.chdir(OriginalDir)

class Audio:
    def GenrateFile(nomeFile, audio, chanels = 1, frequenza = 44100):
        file = wave.open(nomeFile, "wb")

        nframes = len(audio)
        file.setparams((chanels, 2, frequenza, nframes, "NONE", "not compressed"))
        
        dimensione = len(audio)
        for i in range(dimensione):   
            file.writeframes(struct.pack("h", int(audio[i])))

        file.close()

    def AggiungiSilenzio(durata = 0.2, frequenza = 44100):
        silenzio = []
        for el in range(int(durata * frequenza)):
            silenzio.append(0)
        return silenzio

    def Taglia(filePath, usedAlphabet = [], deltaNoise = 2000, pausa = 10000):
        #caricamento del file
        print("\nlavoro sul file:", filePath)
        print("carico il file")
        file = wave.open(filePath, "r")
        frames = file.getnframes()
        AudioStruct = file.readframes(frames)
        AudioArray = numpy.frombuffer(AudioStruct, dtype = numpy.int16)
        AudioArray = AudioArray.tolist()

        #elaborazione del file
        fileTagliati = []
        fileTagliato = []
        paus = 0

        print("divido il file")
        for el in AudioArray:
            if -deltaNoise < el and el < deltaNoise:
                paus += 1
                fileTagliato.append(el)
            
                if(paus > pausa):
                    fileTagliati.append(fileTagliato)
                    fileTagliato = []
                    paus = 0
            else:            
                paus = 0
                fileTagliato.append(el)

        fileTagliati.append(fileTagliato)

        print("ripulisco i files")
        DurataSilenzioPreEPostLEttera = 20
        AudioSenzaSilenzi = []
        for audio in fileTagliati:
            #print("analizzo")
            audiriarrangiato = []
            silenziAllInizio = 0
            silenziAllFine = 0

            primoSilenzio = True
            for el in audio:
                if(-deltaNoise < el and el < deltaNoise and primoSilenzio):
                    silenziAllInizio += 1
                elif(primoSilenzio):
                    primoSilenzio = False

                if(-deltaNoise < el and el < deltaNoise and not primoSilenzio):
                    silenziAllFine += 1
                elif(not primoSilenzio):
                    silenziAllFine = 0

            if(primoSilenzio):
                #print("no")
                continue
            #print(silenziAllInizio, silenziAllFine)
            for i in range(len(audio) - (silenziAllFine - DurataSilenzioPreEPostLEttera)):
                if(i > (silenziAllInizio - DurataSilenzioPreEPostLEttera)):
                    audiriarrangiato.append(audio[i])
            
            AudioSenzaSilenzi.append(audiriarrangiato)
        
        print("equalizzo i files")
        AudiosArrayEq = []
        for audio in AudioSenzaSilenzi:
            AudioArrayEq = []
            maxvalue = numpy.max(audio)
            minvalue = numpy.min(audio)
            massimoAssoluto = 24000
            if maxvalue >= -minvalue:
                mvalue = maxvalue
            else:
                mvalue = -minvalue

            for val in audio:
                valoreEq = (massimoAssoluto * val) / mvalue
                AudioArrayEq.append(valoreEq)
            
            AudiosArrayEq.append(AudioArrayEq)
                        
        print("creo i files")
        NOME = 0
        #print(len(nomi))
        for audio in AudiosArrayEq:
            Audio.GenrateFile(usedAlphabet[NOME] + ".wav",audio = audio)
            NOME += 1
        
        print("ho finito di dividere il file\n")

    def SillabaIta(frase = ""):
        #divide la frase in parole
        parole = []
        parola = ""
        for let in frase:
            if let == " " or let == "," or let == "." or let == "?" or let == "!" or let == ":" or let == ";":
                parole.append(parola)
                parole.append(let)
                parola = ""
            else:
                parola += let
        parole.append(parola)
        del parola  

        #procedo alla divisione
        #ad ogni vocale divido
        primaDivisione = []
        for parola in parole:
            i = 0
            parolaPrimaDivisione = parola
            while i != len(parolaPrimaDivisione) - 1:
                carp = parolaPrimaDivisione[i]
                if carp in SetUp.vocali:
                    i += 1
                    parolaPrimaDivisione = parolaPrimaDivisione[:i] + "-" + parolaPrimaDivisione[i:]
                    
                i += 1
            primaDivisione.append(parolaPrimaDivisione)
            del parola

        #ad ogni doppia divido
        secondaDivisione = []
        for parola in primaDivisione:
            i = 0
            parolaSecondaDivisione = parola
            while i != len(parolaSecondaDivisione) - 1:
                car = parolaSecondaDivisione[i]
                prosCar = parolaSecondaDivisione[i + 1]
                if car == prosCar:
                    i += 1
                    parolaSecondaDivisione = parolaSecondaDivisione[:i] + "-" + parolaSecondaDivisione[i:]
                    
                i += 1
            secondaDivisione.append(parolaSecondaDivisione)
            del parola

        #procedo alla riunione delle sillabe
        #controllo qu + vocale
        primaRiunione = []
        for parola in secondaDivisione:
            if len(parola) <= 4:
                primaRiunione.append(parola)
                continue

            i = 3
            parolaPrimaRiunione = parola
            while i != len(parolaPrimaRiunione):
                car = parolaPrimaRiunione[i]
                PrevistoCutCar = parolaPrimaRiunione[i - 1]
                prevCar = parolaPrimaRiunione[i - 2]
                prevprevCar = parolaPrimaRiunione[i - 3]
                if prevprevCar == "q" and (prevCar == "u" or prevCar == "ù") and PrevistoCutCar == "-" and ((car == "a" or car == "à") or (car == "e" or car == "è") or (car == "i" or car == "ì") or (car == "o" or car == "ò")):
                    parolaPrimaRiunione = (parolaPrimaRiunione[:(i)].removesuffix("-")) + parolaPrimaRiunione[(i):]
                i += 1

            primaRiunione.append(parolaPrimaRiunione)
            del parola

        #controllo doppie
        secondaRiunione = []
        for parola in primaRiunione:
            if len(parola) <= 2:
                secondaRiunione.append(parola)
                continue
            i = 0
            parolaSecondaRiunione = parola
            while i != len(parolaSecondaRiunione)-2:
                car = parolaSecondaRiunione[i]
                PrevistoCutCar = parolaSecondaRiunione[i +1]
                prosCar = parolaSecondaRiunione[i + 2]
                if PrevistoCutCar == "-" and car == prosCar:
                    parolaSecondaRiunione = (parolaSecondaRiunione[:(i)].removesuffix("-")) + parolaSecondaRiunione[(i):]
                    i += 1
                    continue
                i += 1

            secondaRiunione.append(parolaSecondaRiunione)
            del parola

        #vocali spaiate
        terzaRiunione = []
        for parola in secondaRiunione:
            if len(parola) <= 2:
                terzaRiunione.append(parola)
                continue
            i = 0
            parolaTerzaRiunione = parola
            while i != len(parolaTerzaRiunione)-1:
                carp = parolaTerzaRiunione[i]
                PrevistoCutCar = parolaTerzaRiunione[i + 1]

                if (PrevistoCutCar == "-") and  carp in SetUp.vocali:
                    parolaTerzaRiunione = (parolaTerzaRiunione[:(i)].removesuffix("-")) + parolaTerzaRiunione[(i):]
                    i += 1
                    continue
                i += 1

            terzaRiunione.append(parolaTerzaRiunione)
            del parola
        
        #sistemazione delle parole corte 
        quartaRiunione = []
        for parola in terzaRiunione:
            if len(parola) == 3:
                if parola[1] == "-":
                    newParola = parola[:1] + parola[2:]
                    quartaRiunione.append(newParola)
            else:
                quartaRiunione.append(parola)
            del parola

        #metto la frase in un array
        sillabeArray = []
        for parola in quartaRiunione:
            parolaArray = []
            sillaba = ""
            for car in parola:
                if car == "-":
                    parolaArray.append(sillaba)
                    sillaba = ""
                else:
                    sillaba += car
            parolaArray.append(sillaba)


            sillabeArray.append(parolaArray)
    
        return sillabeArray

    def Sillaba1Ita (frase = ""):
        sillabe = []
        lettereCheNonFannoCoseConCeG = ["e","i"]
        leg = ""
        for el in frase:
            if (el == "c" or el == "g") and len(leg) == 0:
                leg += el
            elif len(leg) == 1 and not el in lettereCheNonFannoCoseConCeG:
                leg += "h"
                sillabe.append([leg])
                leg = ""
                if el != "h":
                    sillabe.append(el)
            else:
                if leg != "":
                    sillabe.append([leg]) 
                leg = ""
                sillabe.append(el)
        print(sillabe)
        return sillabe

    def CaricaSillaba(sillaba = "a", libreria = "none", frequenza = 44100, euqalizaznione = 12000, buffer = []):
        if not os.path.exists(libreria):
            print("non esite:",libreria)
            return 0
        
        audioLettereSingole = []
        if len(buffer) == 0:
            
            #carco le letere
            for lettera in sillaba:
                #carico il file
                fileName = libreria + "/" + lettera + ".wav"
                file = wave.open(fileName, "r")

                #converto il file
                frames = file.getnframes()
                AudioStruct = file.readframes(frames)
                AudioArray = numpy.frombuffer(AudioStruct, dtype = numpy.int16)

                audioLettereSingole.append(AudioArray)
                print(len(AudioArray))
        else:
            audioLettereSingole = buffer

        #se è una lettera sola retun quella lettera
        if len(sillaba) == 1:
            print("   una lettera",audioLettereSingole)
            return audioLettereSingole[0]

        #se la sillaba e composta da 2 o piu lettere
        #conta gli elemnti da unire all'inizo e all fine
        SilenziAudio = [[],[],[]]
        for suono in audioLettereSingole:
            spazioIniziale = 0
            spazioFinale = 0
            #conta i frames da elimnare all'inizio
            for el in suono:
                if el <= euqalizaznione and el >= -euqalizaznione:
                    spazioIniziale += 1
                else:
                    break

                #conta i frames da elimnare alla fine
            for i in range(-len(suono)+1,0):
                el = suono[-i]
                if el <= euqalizaznione and el >= -euqalizaznione:
                    spazioFinale += 1
                else:
                    break
            
            SilenziAudio[0].append(spazioIniziale)
            SilenziAudio[1].append(len(suono) - (spazioIniziale + spazioFinale))
            SilenziAudio[2].append(spazioFinale)
        
        #prevedo la lungezza del file finale
        lungAudioUnito = SilenziAudio[0][0]
        lungAudioUnito += SilenziAudio[2][len(SilenziAudio[2]) - 1]
        for i in SilenziAudio[1]:
            lungAudioUnito += i
        del i

        print(lungAudioUnito)

        AudioUnito = []
        PartiAudio = []
        ver = 0
        for p in range(len(sillaba)):
            if p == 0:
                primaParteSolo = SilenziAudio[0][0] + SilenziAudio[1][0] - SilenziAudio[0][1]
                primaParteDoppio = SilenziAudio[0][1] + SilenziAudio[2][0]
                ver += primaParteDoppio + primaParteSolo
                PartiAudio.append(primaParteSolo)
                PartiAudio.append(primaParteDoppio)
            elif p == len(sillaba) - 1:
                ultimaParteSolo = SilenziAudio[2][p] + SilenziAudio[1][p] - SilenziAudio[2][p-1]
                ver += ultimaParteSolo
                PartiAudio.append(ultimaParteSolo)
            else:
                parteSolo = SilenziAudio[1][p] - SilenziAudio[2][p-1] -SilenziAudio[0][p+1]
                parteDoppio = SilenziAudio[2][p] + SilenziAudio [0][p+1]
                ver += parteDoppio + parteSolo
                PartiAudio.append(parteSolo)
                PartiAudio.append(parteDoppio)

        print(PartiAudio,ver)

        for parte in range(len(PartiAudio)):
            lung = PartiAudio[parte]
            print(lung,parte)
            if parte % 2 == 0:
                for el in range(lung):
                    AudioUnito.append(audioLettereSingole[int(parte / 2)][el])
            else:
                print(lung,PartiAudio[parte] + PartiAudio[parte - 1])
                for el in range(lung):
                    if parte == 1:
                        Au1 = audioLettereSingole[int(parte / 2)][PartiAudio[parte - 1] + el]
                    else:
                        Au1 = audioLettereSingole[int(parte / 2) ][PartiAudio[parte - 1] + el]
                    Au2 = audioLettereSingole[int(parte / 2)][el]
                    
                    if abs(Au1) >= abs(Au2):
                        AudioUnito.append(Au1)
                    else:
                        AudioUnito.append(Au2)
            
        return AudioUnito

    def SetUpTaglia(LibreriaDir):
        nomeCompletoLibreria = GUI.OriginalDir + "/Data/suoni/" + LibreriaDir
        os.chdir(GUI.OriginalDir + "/Data/suoni/")
        if not os.path.exists(nomeCompletoLibreria):
            os.makedirs(nomeCompletoLibreria)
        os.chdir(nomeCompletoLibreria)

        nome = GUI.OriginalDir + "/Data/librerieSuoni/" + LibreriaDir + ".wav"

        tagla = Process(target = Audio.Taglia , args = (nome,SetUp.alpabeto))
        tagla.start() 

    def FiltraContenuto(frase):
        Audio.FiltraContenuto.vocaliAccentateAscii = []
        for voc in SetUp.accenti:
            Audio.FiltraContenuto.vocaliAccentateAscii.append(ord(voc))

        Audio.FiltraContenuto.punteggiatura = []
        for pun in SetUp.punteggiatura:
            Audio.FiltraContenuto.punteggiatura.append(ord(pun))

        fraseSisteamta = ""

        inspazio = 0
        for car in frase:
            ocar = ord(car)
            if (ocar in Audio.FiltraContenuto.vocaliAccentateAscii or
                ocar in range(65,91) or ocar in range(97,123)):
                fraseSisteamta += car
                inspazio = 0
            elif ocar in Audio.FiltraContenuto.punteggiatura:
                if inspazio == 0:
                    inspazio += 1
                    fraseSisteamta += " "

        for el in fraseSisteamta:
            fraseSisteamta = fraseSisteamta.removesuffix(" ")

        print("\nfrase:",fraseSisteamta)
        return fraseSisteamta

    def SetUpGeneraOutput(nome,contenuto,libreria,lingua,frasiLoc):
        print("helo")
        contenuto = Audio.FiltraContenuto(contenuto)
        Audio.SetUpGeneraOutput.sillabe = ""
        match lingua:
            case "ita":
                Audio.SetUpGeneraOutput.sillabe = Audio.SillabaIta(contenuto)
                Audio.SetUpGeneraOutput.audiosillabe = [Audio.AggiungiSilenzio(0.1)]
                for parola in Audio.SetUpGeneraOutput.sillabe:
                    for silllaba in parola:
                        print(silllaba)
                        if silllaba == " ":
                            print("spazio")
                            Audio.SetUpGeneraOutput.audiosillabe.append(Audio.AggiungiSilenzio())
                            continue
                        Audio.SetUpGeneraOutput.audiosillabe.append(Audio.CaricaSillaba(silllaba,libreria))
                        print("carica la sillaba:",silllaba)
                Audio.SetUpGeneraOutput.audiosillabe.append(Audio.AggiungiSilenzio(0.1))
            case "ita1":
                Audio.SetUpGeneraOutput.sillabe = Audio.Sillaba1Ita(contenuto)
                Audio.SetUpGeneraOutput.audiosillabe = [Audio.AggiungiSilenzio(0.1)]
                for silllaba in Audio.SetUpGeneraOutput.sillabe:
                    if silllaba == " ":
                        print("spazio")
                        Audio.SetUpGeneraOutput.audiosillabe.append(Audio.AggiungiSilenzio())
                        continue
                    Audio.SetUpGeneraOutput.audiosillabe.append(Audio.CaricaSillaba(silllaba,libreria))
                    print("carica la sillaba:",silllaba)
                Audio.SetUpGeneraOutput.audiosillabe.append(Audio.AggiungiSilenzio(0.1))
            case _:
                pass
        
        
        
        audio = []
        for el in Audio.SetUpGeneraOutput.audiosillabe:
            for i in el:
                audio.append(i)

        os.chdir(frasiLoc)
        Audio.GenrateFile(nome,audio)
        print("generato")

class GUI:
    OriginalDir = os.getcwd()
    infoPannelIsOpen = False
    info = """
Benvenuto nella Kat Kave
Con questo programma puoi creare delle frasi

1) carica una libreria audio
2) inserisci una frase nell'apposito slot e aggiungi un titolo
3) seleziona la lingua e priemi genera
4) troverai il risiultato nella casella output
    """

    def setUpGUI():
        GUI.setUpGUI.root = tk.Tk()
        GUI.setUpGUI.root.title("kat kave") #(__name__.removeprefix("__").removesuffix("__"))
        GUI.setUpGUI.root.geometry("1200x900")
        
        try:
            GUI.setUpGUI.root.iconbitmap(GUI.OriginalDir + r"/katcon.ico")
        except:
            print("icona non trovata")

    def baseUI():
        GUI.baseUI.canvas = tk.Canvas(GUI.setUpGUI.root,bg = "#232323",height=900,width=1200)
        GUI.baseUI.canvas.pack()

        GUI.baseUI.textFrame = tk.Frame(GUI.baseUI.canvas)
        GUI.baseUI.textFrame.place(relheight= 0.92, relwidth= 0.61,relx = 0.03,rely = 0.04)

        GUI.baseUI.voceFrame = tk.Frame(GUI.baseUI.canvas)
        GUI.baseUI.voceFrame.place(relheight= 0.48, relwidth= 0.3,relx = 0.67,rely = 0.04)

        GUI.baseUI.outputFrame = tk.Frame(GUI.baseUI.canvas)
        GUI.baseUI.outputFrame.place(relheight= 0.20, relwidth= 0.3,relx = 0.67,rely = 0.56)

        GUI.baseUI.languageFrame = tk.Frame(GUI.baseUI.canvas)
        GUI.baseUI.languageFrame.place(relheight=0.16,relwidth=0.05,relx=0.92,rely=0.8)

    def SetUpInputFied():
        GUI.SetUpInputFied.titolo = tk.Entry(GUI.baseUI.textFrame,font = ("Time New Roman", 20))
        GUI.SetUpInputFied.titolo.place(relheight= 0.05, relwidth= 1)
        GUI.SetUpInputFied.titolo.insert(0,"Titolo")

        GUI.SetUpInputFied.contenuto = tk.Text(GUI.baseUI.textFrame,font = ("Time New Roman", 12))
        GUI.SetUpInputFied.contenuto.place(relheight= 0.95, relwidth= 1,rely=0.05)
        GUI.SetUpInputFied.contenuto.insert(tk.END,"il testo del messaggio")

    def SetIndex(index):
        GUI.Index = index
        GUI.ShowLoadedAudios()

    def ReloadLibrary(index):
        richediReload = messagebox.askquestion("conferma","vuoi ricaricare la libreria?")
        if richediReload == "yes":
            GUI.LoadLibrary(index)

    def LoadLibrary(index):
        print("carico",GUI.libraries[index].removesuffix(".wav"))
        nomeLibreria = GUI.libraries[index].removesuffix(".wav")
        #nomeCompletoLibreria = GUI.OriginalDir + "/Data/librerieSuoni/" + GUI.libraries[index]
        Audio.SetUpTaglia(nomeLibreria)
        GUI.ShowLoadedAudios()
        pass

    def ShowLoadedAudios():
        GUI.libraries = os.listdir(GUI.OriginalDir + r"/Data/librerieSuoni")
        GUI.loadedLibraries = os.listdir(GUI.OriginalDir + r"/Data/suoni")
        
        for w in GUI.baseUI.voceFrame.winfo_children():
            w.destroy()
        LabelS = []

        head = tk.Label(GUI.baseUI.voceFrame,text = "librerie Audio")
        head.pack()

        for i in range(len(GUI.libraries)):
            libreira = GUI.libraries[i]
            if i == GUI.Index:
                LabelS.append(tk.Button(GUI.baseUI.voceFrame,text = libreira,bg="#707070",command = partial(GUI.SetIndex, i)))
            else:
                LabelS.append(tk.Button(GUI.baseUI.voceFrame,text = libreira,bg="#9e9e9e",command = partial(GUI.SetIndex, i)))
            
            try:
                GUI.loadedLibraries.index(libreira.removesuffix(".wav"))
                b = tk.Button(GUI.baseUI.voceFrame,text = "ricarica",bg="#9e9e9e",command = partial(GUI.ReloadLibrary, i))
                b.place(relwidth = 0.15,relx = 0.85,rely=0.05* i + 0.05,relheight=0.05)
            except:
                b = tk.Button(GUI.baseUI.voceFrame,text = "carica",bg="#707070",command = partial(GUI.LoadLibrary, i))
                b.place(relwidth = 0.15,relx = 0.85,rely=0.05*i  + 0.05,relheight=0.05)
            
            LabelS[i].place(relheight=0.05, relx=0,rely=0.05*i + 0.05,relwidth=0.85)

    def PlaySound(nome):
        nomePercorso = GUI.OriginalDir + "/Data/frasi/" + nome
        try:
            winsound.PlaySound(nomePercorso,winsound.SND_ASYNC)
        except: # function not found
            playsound ( nomePercorso, False )

    def ShowGeneratedFiles():
        print("show")
        GUI.outputs = os.listdir(GUI.OriginalDir + r"/Data/frasi")
        
        head = tk.Label(GUI.baseUI.outputFrame,text = "Output")
        head.pack()
        
        contentFrame = tk.Frame(GUI.baseUI.outputFrame,bg = "#999999")
        contentFrame.place(relwidth=0.95,relheight=0.85,rely=0.15)
        
        canvas_container=tk.Canvas(contentFrame, height=1040)
        frame2=tk.Frame(canvas_container)# bg= "#324890")
        myscrollbar=tk.Scrollbar(GUI.baseUI.outputFrame,orient="vertical",command=canvas_container.yview) # will be visible if the frame2 is to to big for the canvas
        canvas_container.create_window((0,0),window=frame2,anchor='nw')

        for item in GUI.outputs:
            button = tk.Button(frame2,text=item,command=partial(GUI.PlaySound,item))
            button.pack()


        frame2.update() # update frame2 height so it's no longer 0 ( height is 0 when it has just been created )
        canvas_container.configure(yscrollcommand=myscrollbar.set, scrollregion="0 0 0 %s" % frame2.winfo_height()) # the scrollregion mustbe the size of the frame inside it,
                                                                                                                    #in this case "x=0 y=0 width=0 height=frame2height"
                                                                                                                    #width 0 because we only scroll verticaly so don't mind about the width.

        canvas_container.pack()
        myscrollbar.pack(side=RIGHT, fill = "y")

        contentFrame.place(relwidth=0.95,relheight=0.85,rely=0.15)

    def SetLanguageIndex(index):
        GUI.languageIndex = index
        GUI.ShowSelectedLanguage()

    def ShowSelectedLanguage():
        for w in GUI.baseUI.languageFrame.winfo_children():
            w.destroy()
        
        head = tk.Label(GUI.baseUI.languageFrame,text = "langages")
        head.pack()
        relH = 0.8 / len(SetUp.langages)
        for i in range(len(SetUp.langages)):
            ling = SetUp.langages[i]
            if i == GUI.languageIndex:
                GUI.ShowSelectedLanguage.SetLanguageButton = tk.Button(GUI.baseUI.languageFrame,text=ling,bg = "#707070",command = partial(GUI.SetLanguageIndex,i))
                GUI.ShowSelectedLanguage.SetLanguageButton.place(relheight=relH,relwidth=1,rely = 0.2 + relH * i ,relx=0)
            else:
                GUI.ShowSelectedLanguage.SetLanguageButton = tk.Button(GUI.baseUI.languageFrame,text=ling,bg = "#9e9e9e",command = partial(GUI.SetLanguageIndex,i))
                GUI.ShowSelectedLanguage.SetLanguageButton.place(relheight=relH,relwidth=1,rely = 0.2 + relH * i ,relx=0)
            
            pass

    def Info():
        if not GUI.infoPannelIsOpen:
            GUI.Info.infoBox = tk.Frame(GUI.baseUI.canvas,bg = "#c6c6c6")
            GUI.Info.infoBox.place(relheight = 0.92, relwidth = 0.94,rely = 0.04,relx=0.03)
            
            GUI.Info.infoLabel = tk.Label(GUI.Info.infoBox,text = GUI.info,bg = "#c6c6c6")
            GUI.Info.infoLabel.pack()
            GUI.infoPannelIsOpen = True
        else:
            GUI.Info.infoBox.destroy()
            GUI.infoPannelIsOpen = False

    def LoadText():
        nomeFile = filedialog.askopenfilename(initialdir = GUI.OriginalDir,title = "Sciegli il file",filetypes = (("File Txt","*.txt"),("all","*.*")))
        if nomeFile == "":
            return
        
        with open(nomeFile,"r",encoding = "utf-8") as file_in:
            lines = []
            for line in file_in:
                lines.append(line)

        GUI.SetUpInputFied.titolo.delete(0,END)
        GUI.SetUpInputFied.titolo.insert(0,lines[0].removesuffix("\n"))
        index = int(lines[1].removesuffix("\n"))
        
        testo = ""
        for lineIndex in range(2,len(lines)):
            testo += lines[lineIndex]
        
        GUI.SetUpInputFied.contenuto.delete("0.0",END)
        GUI.SetUpInputFied.contenuto.insert(tk.END,testo)
        GUI.SetIndex(index)

    def AddAudioFile():
        nomiFile = filedialog.askopenfilenames(initialdir = GUI.OriginalDir,title = "Sciegli i file",filetypes = (("File Wave","*.wav"),("all","*.*")))
        if nomiFile == "":
            return

        for el in nomiFile:
            nomeFile = []
            for p in range(-len(el)+1, 0):
                i = el[-p]
                if i == "/":
                    break
                else:
                    nomeFile.insert(0,i)

            nomeFilee = ""
            for l in nomeFile:
                nomeFilee += l

            c = 0
            for con in GUI.libraries:
                if con == nomeFilee:
                    c += 1
            
            if c == 0:
                copy2(el,GUI.OriginalDir + r"/Data/librerieSuoni")
                GUI.libraries.append(nomeFilee)
        GUI.ShowLoadedAudios()

    def Split(string):
        retStr = ""
        for el in string:
            if el == "\n":
                retStr += " "
            else:
                retStr += el
        
        for el in string:
            retStr = retStr.removesuffix(" ")
        return retStr
        
    def GenerateOutput():
        GUI.GenerateOutput.nomeFile = GUI.SetUpInputFied.titolo.get() + ".wav"
        GUI.GenerateOutput.libreria = GUI.OriginalDir + "/Data/suoni/" + GUI.libraries[GUI.Index].removesuffix(".wav")
        GUI.GenerateOutput.contenuto = GUI.SetUpInputFied.contenuto.get("0.0",END)
        GUI.GenerateOutput.contenuto = GUI.Split(GUI.GenerateOutput.contenuto)
        GUI.GenerateOutput.language = SetUp.langages[GUI.languageIndex]

        #print("genereo il file:",GUI.GenerateOutput.nomeFile,"con libreria:",
        #GUI.GenerateOutput.libreria,"con contenuto:",GUI.GenerateOutput.contenuto,
        #"in lingua:",GUI.GenerateOutput.language)
        GUI.ShowGeneratedFiles()

        generateFileProcess = Process(target = Audio.SetUpGeneraOutput, args = (GUI.GenerateOutput.nomeFile,GUI.GenerateOutput.contenuto,GUI.GenerateOutput.libreria,GUI.GenerateOutput.language,GUI.OriginalDir + "/data/frasi"))
        generateFileProcess.start()

    def SetUpButton():
        GUI.SetUpButton.generateButton = tk.Button(GUI.baseUI.canvas,text="genera Testo",bg="#9e9e9e",command = GUI.GenerateOutput)
        GUI.SetUpButton.generateButton.place(relwidth=0.25,relheight=0.16,relx= 0.67,rely=0.8)

        #GUI.SetUpButton.caricaTestoButton = tk.Button(GUI.baseUI.textFrame,text="carica Testo",bg = "#9e9e9e",command = GUI.LoadText)
        #GUI.SetUpButton.caricaTestoButton.place(relx=0.9,relwidth=0.1,relheight= 0.05)

        GUI.SetUpButton.caricaLibreriaButton = tk.Button(GUI.baseUI.canvas,text = "carica Libreria",bg="#9e9e9e",command = GUI.AddAudioFile)
        GUI.SetUpButton.caricaLibreriaButton.place(relwidth=0.08,relheight=0.025,relx= 0.67,rely= 0.04)

        GUI.SetUpButton.infoButton = tk.Button(GUI.baseUI.canvas,text = "PANIC BUTTON",bg="#9e9e9e",command = GUI.Info)
        GUI.SetUpButton.infoButton.place(relx= 0.0,rely = 0.0,relwidth = 0.09,relheight = 0.04)   

        GUI.SetUpButton.reloadOutput = tk.Button(GUI.baseUI.canvas,text = "ricarica",bg="#9e9e9e",command = GUI.ShowGeneratedFiles)
        GUI.SetUpButton.reloadOutput.place(relx= 0.67,rely = 0.56,relwidth = 0.06,relheight = 0.03)

    def startGUI():
        GUI.setUpGUI()
        GUI.baseUI()
        GUI.SetIndex(0)
        GUI.SetUpInputFied()
        GUI.SetUpButton()
        GUI.ShowLoadedAudios()
        GUI.ShowGeneratedFiles()
        GUI.SetLanguageIndex(0)
        GUI.ShowSelectedLanguage()
        GUI.setUpGUI.root.mainloop()

if __name__ == "__main__":
    setup = Process(target = SetUp.ControllaDirectory())
    setup.start()

    gui = Process(GUI.startGUI())
    gui.start()
