import pandas as pd
import random
import os
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import plotly.express as px


print("Aktuelles Arbeitsverzeichnis:", os.getcwd())

RUNDE = 200


def alwayscooperate (runde,eigenehistory, gegnerhistory):    
    return "K"

def alwaysdefect (runde,eigenehistory, gegnerhistory):   
    return "E"

def titfortat (runde,eigenehistory, gegnerhistory):
    if runde == 0:
        return "K"
    else:
        if gegnerhistory[-1] == "E":
            return "E"
        else:
            return "K"

def two_tits_for_tat (runde,eigenehistory, gegnerhistory):
    if runde == 0:
        return "K"
    else:
        if gegnerhistory[-1] == "E":
            return "E" 
        if len(gegnerhistory) >= 2 and gegnerhistory[-2] == "E":
            return "E"
        else:
            return "K"

def grofman (runde,eigenehistory, gegnerhistory):
    if runde == 0:
        return "K"
    else:
        if eigenehistory[-1] != gegnerhistory[-1]:
            if random.random() < 2 / 7:
                return "K"
            else:
                return "E"
        else:
            return "K"

def friedman (runde,eigenehistory, gegnerhistory):
    if runde == 0:
        return "K"
    else:
        if "E" in gegnerhistory:
            return "E"
        else:
            return "K"

def random_strategy (runde,eigenehistory, gegnerhistory):
    if random.random() < 0.5:
        return "K"
    else:
        return "E"

def shubik (runde,eigenehistory, gegnerhistory):
    punish = False
    punish_remaining = 0
    punish_length = 0
    move = "K"  

    for i in range (runde + 1):
        if i == 0:
            move = "K"
        elif punish:
            punish_remaining -= 1
            if punish_remaining <= 0:
                punish = False
            move = "E"
        elif gegnerhistory[i - 1] == "E":
            punish_length += 1
            punish_remaining = punish_length - 1
            punish = punish_remaining > 0
            
            move = "E"
        else:
            move = "K"

    return move

def feld (runde,eigenehistory, gegnerhistory):
    if runde == 0:
        return "K"
    else:
        if gegnerhistory [runde-1] == "E":
            return "E"
        p = 1.0 - 0.5 * (runde / (RUNDE - 1))  
        if random.random() > p:
            return "E"
        return "K"


def own_strategy (runde,eigenehistory, gegnerhistory):
    if runde == 0:
        return "K"
    if runde >= 5:
        for i in range (1, 6):
            if   eigenehistory[-i] == "K" and gegnerhistory[-i] == "K":
                if i == 5:
                    return "E"
            else:
                if gegnerhistory [-1] == "E":
                    return "E"
                else:
                    return "K"
    else:
        if gegnerhistory [-1] == "E":
            return "E"
        else:
            return "K"


strategien = [alwayscooperate, alwaysdefect, titfortat, two_tits_for_tat, grofman, friedman, shubik, feld, random_strategy, own_strategy]


def konfigurationen (low = 1, high = 7, steps = 0.5, s = 0):
    n_steps = round((high - low) / steps) + 1
    values = []
    for i in range (n_steps):
        values.append (round (low + i*steps, 2))
    configs = []
    for T in values:
        for R in values:
            for P in values:
                if P <= T:
                     configs. append ((T, R, P, s))
                elif P <= R:
                    configs. append ((T, R, P, s))
    return configs



def spiele (strategie1, strategie2, T, R, P, S):
    history1 = []
    history2 = []
    score1 = 0
    score2 = 0
    for runde in range (RUNDE):
        move1 = strategie1(runde, history1, history2)
        move2 = strategie2(runde, history2, history1)
        history1.append(move1)
        history2.append(move2)
        if move1 == "K" and move2 == "K":
            score1 += R
            score2 += R
        elif move1 == "K" and move2 == "E":
            score1 += S
            score2 += T
        elif move1 == "E" and move2 == "K":
            score1 += T
            score2 += S
        else:
            score1 += P 
            score2 += P
    return score1, score2

TRP = []
TPR = []
RTP = []
RPT = []

def Turnier (strategien, TRP, TPR, RTP, RPT):
    results = []
    configs = konfigurationen ()
    n = len(strategien)
    for config in configs:
        T, R, P, S = config
        for i in range (n):
            for j in range (i,n):
                s1, s2 = strategien[i], strategien[j]
                score1, score2 = spiele (s1, s2, T, R, P, S)
                results.append ((s1.__name__, T, R, P, S, score1))
                results.append ((s2.__name__, T, R, P, S, score2))
                
                if T > P and P > R:
                    TPR.append((s1.__name__, T, R, P, S, score1))
                    TPR.append((s2.__name__, T, R, P, S, score2))
                if T > R and R > P:
                    TRP.append((s1.__name__, T, R, P, S, score1))
                    TRP.append((s2.__name__, T, R, P, S, score2))
                if R > T and T > P:
                    RTP.append((s1.__name__, T, R, P, S, score1))
                    RTP.append((s2.__name__, T, R, P, S, score2))
                if R > P and P > T:
                    RPT.append((s1.__name__, T, R, P, S, score1))
                    RPT.append((s2.__name__, T, R, P, S, score2))
    
    
    return results

rohdaten = Turnier(strategien, TRP, TPR, RTP, RPT)


df = pd.DataFrame(rohdaten, columns=["Strategie", "T", "R", "P", "S", "Score"])


totals = df.groupby(["T","R","P","S","Strategie"], as_index=False)["Score"].sum()


totals["Rang"] = totals.groupby(["T","R","P","S"])["Score"].rank(ascending=False, method="min")



for strategie in strategien:
    strategie_rang = totals[totals["Strategie"] == strategie.__name__].sort_values(["T","R","P"])
    strategie_rang.to_csv(f"{strategie.__name__}_rang_.csv", index=False)
    

durchscnittsrang_allgemein = totals.groupby("Strategie")["Rang"].mean().sort_values()
durchscnittsrang_allgemein.to_csv("durchschnittsrang_allgemein.csv")

for name, hierarchie_daten in [("TRP", TRP), ("TPR", TPR), ("RTP", RTP), ("RPT", RPT)]:
    df_h = pd.DataFrame(hierarchie_daten, columns=["Strategie", "T", "R", "P", "S", "Score"])
    totals_h = df_h.groupby(["T","R","P","S","Strategie"], as_index=False)["Score"].sum()
    totals_h["Rang"] = totals_h.groupby(["T","R","P","S"])["Score"].rank(ascending=False, method="min")
    
    durchschnitt_h = totals_h.groupby("Strategie")["Rang"].mean().sort_values()
    durchschnitt_h.to_csv(f"Durchschnittsrang_{name}.csv")
    
