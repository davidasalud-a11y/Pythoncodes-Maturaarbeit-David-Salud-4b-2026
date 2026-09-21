import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

nette_strategien = ["alwayscooperate", "titfortat", "two_tits_for_tat", "grofman", "friedman", "shubik"]
nicht_nette_strategien = ["alwaysdefect", "random_strategy", "feld", "own_strategy"]
alle_strategien = nette_strategien + nicht_nette_strategien


gesamttabelle = []
for name in alle_strategien:
    t = pd.read_csv(f"{name}_rang.csv")
    t["Gruppe"] = "nett" if name in nette_strategien else "nicht nett"
    gesamttabelle.append(t)

gesamttabelle = pd.concat(gesamttabelle, ignore_index=True)


hierarchie_masken_gesamt = {
    "TRP": (gesamttabelle["T"] >= gesamttabelle["R"]) & (gesamttabelle["R"] >= gesamttabelle["P"]),
    "TPR": (gesamttabelle["T"] >= gesamttabelle["P"]) & (gesamttabelle["P"] >= gesamttabelle["R"]),
    "RTP": (gesamttabelle["R"] >= gesamttabelle["T"]) & (gesamttabelle["T"] >= gesamttabelle["P"]),
    "RPT": (gesamttabelle["R"] >= gesamttabelle["P"]) & (gesamttabelle["P"] >= gesamttabelle["T"]),
}




gruppen_rang = gesamttabelle.groupby(["T", "R", "P", "S", "Gruppe"], as_index=False)["Rang"].mean()

pivot = gruppen_rang.pivot(index=["T", "R", "P", "S"], columns="Gruppe", values="Rang").reset_index()
pivot["Sieger"] = pivot.apply(
    lambda zeile: "nett" if zeile["nett"] < zeile["nicht nett"] else "nicht nett",
    axis=1
)

hierarchie_masken_pivot = {
    "TRP": (pivot["T"] >= pivot["R"]) & (pivot["R"] >= pivot["P"]),
    "TPR": (pivot["T"] >= pivot["P"]) & (pivot["P"] >= pivot["R"]),
    "RTP": (pivot["R"] >= pivot["T"]) & (pivot["T"] >= pivot["P"]),
    "RPT": (pivot["R"] >= pivot["P"]) & (pivot["P"] >= pivot["T"]),
}

gruppen_ergebnisse = []
for hname, maske in hierarchie_masken_pivot.items():
    teilmenge = pivot[maske]

    rang_nett = teilmenge["nett"].mean()
    rang_nicht_nett = teilmenge["nicht nett"].mean()

    anzahl_nett = (teilmenge["Sieger"] == "nett").sum()
    anzahl_nicht_nett = (teilmenge["Sieger"] == "nicht nett").sum()
    gesamt = anzahl_nett + anzahl_nicht_nett

    gruppen_ergebnisse.append({
        "Hierarchie": hname,
        "Ø Rang kooperative Gruppe": round(rang_nett, 2),
        "Ø Rang egoistische Gruppe": round(rang_nicht_nett, 2),
        "Anzahl Siege kooperative Gruppe": anzahl_nett,
        "Anzahl Siege egoistische Gruppe": anzahl_nicht_nett,
        "Sieg kooperative Gruppe (%)": round(anzahl_nett / gesamt * 100, 2),
        "Sieg egoistische Gruppe (%)": round(anzahl_nicht_nett / gesamt * 100, 2),
        "Anzahl Konfigurationen": gesamt
    })

gruppen_auswertung = pd.DataFrame(gruppen_ergebnisse).set_index("Hierarchie")
gruppen_auswertung = gruppen_auswertung.reindex(["TRP", "TPR", "RTP", "RPT"])

print("=== Gruppenvergleich (nett vs. nicht nett) pro Hierarchie ===")
print(gruppen_auswertung)
gruppen_auswertung.to_csv("egoistisch_vs_kooperativ_auswertung.csv")



rang_haeufigkeit_gesamt = pd.crosstab(gesamttabelle["Strategie"], gesamttabelle["Rang"])
rang_haeufigkeit_gesamt = rang_haeufigkeit_gesamt.reindex(columns=range(1, 11), fill_value=0)

print("\n=== Rang-Häufigkeit pro Strategie (gesamtes Turnier) ===")
print(rang_haeufigkeit_gesamt)
rang_haeufigkeit_gesamt.to_csv("rang_haeufigkeit_gesamt.csv")


durchschnittsrang_liste = []
for hname, maske in hierarchie_masken_gesamt.items():
    teilmenge = gesamttabelle[maske]
    mittel = teilmenge.groupby("Strategie")["Rang"].mean().rename(hname)
    durchschnittsrang_liste.append(mittel)

durchschnittsrang_strategie_hierarchie = pd.concat(durchschnittsrang_liste, axis=1)


durchschnittsrang_strategie_hierarchie["Gesamt"] = gesamttabelle.groupby("Strategie")["Rang"].mean()

durchschnittsrang_strategie_hierarchie = durchschnittsrang_strategie_hierarchie.round(2)
durchschnittsrang_strategie_hierarchie = durchschnittsrang_strategie_hierarchie[["TRP", "TPR", "RTP", "RPT", "Gesamt"]]
durchschnittsrang_strategie_hierarchie = durchschnittsrang_strategie_hierarchie.sort_values("Gesamt")

print("\n=== Durchschnittsrang pro Strategie: je Hierarchie und gesamtes Turnier ===")
print(durchschnittsrang_strategie_hierarchie)
durchschnittsrang_strategie_hierarchie.to_csv("durchschnittsrang_strategie_hierarchie.csv")