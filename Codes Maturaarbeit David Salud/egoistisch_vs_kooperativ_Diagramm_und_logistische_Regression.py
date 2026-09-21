import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.spatial import ConvexHull
import statsmodels.api as sm

nette_strategien = ["alwayscooperate", "titfortat", "two_tits_for_tat", "grofman", "friedman", "shubik"]
nicht_nette_strategien = ["alwaysdefect", "random_strategy", "feld", "own_strategy"]
alle_strategien = nette_strategien + nicht_nette_strategien

gesamttabelle = []

for name in alle_strategien:
    t = pd.read_csv(f"{name}_rang.csv")
    if name in nette_strategien:
        t["Gruppe"] = "nett"
    else:
        t["Gruppe"] = "nicht nett"
    gesamttabelle.append(t)

gesamttabelle = pd.concat(gesamttabelle, ignore_index=True)
gruppen_rang = gesamttabelle.groupby(["T", "R", "P", "S", "Gruppe"], as_index=False)["Rang"].mean()

pivot = gruppen_rang.pivot(index=["T", "R", "P", "S"], columns="Gruppe", values="Rang").reset_index()
pivot["Differenz"] = pivot["nicht nett"] - pivot["nett"]

pivot["Sieger"] = pivot.apply(
    lambda zeile: "nett" if zeile["nett"] < zeile["nicht nett"] else "nicht nett",
    axis=1
)


pivot["Sieger_binaer"] = (pivot["Sieger"] == "nett").astype(int)

X = pivot[["T", "R", "P"]]
X = sm.add_constant(X)
y = pivot["Sieger_binaer"]

modell = sm.Logit(y, X)
ergebnis = modell.fit()
print(ergebnis.summary())

beta0, beta_T, beta_R, beta_P = ergebnis.params["const"], ergebnis.params["T"], ergebnis.params["R"], ergebnis.params["P"]


fig = px.scatter_3d(
    pivot,
    x="T", y="R", z="P",
    color="Sieger",
    color_discrete_map={"nett": "green", "nicht nett": "red"},
    hover_data=["T", "R", "P", "nett", "nicht nett"]
)


punkte_nett = pivot.loc[pivot["Sieger"] == "nett", ["T", "R", "P"]].drop_duplicates().values
punkte_nicht_nett = pivot.loc[pivot["Sieger"] == "nicht nett", ["T", "R", "P"]].drop_duplicates().values

if len(punkte_nett) >= 4:
    hull_nett = ConvexHull(punkte_nett)
    fig.add_trace(
        go.Mesh3d(
            x=punkte_nett[:, 0], y=punkte_nett[:, 1], z=punkte_nett[:, 2],
            i=hull_nett.simplices[:, 0], j=hull_nett.simplices[:, 1], k=hull_nett.simplices[:, 2],
            color="green", opacity=0.15, name="Bereich: nett gewinnt"
        )
    )

if len(punkte_nicht_nett) >= 4:
    hull_nicht_nett = ConvexHull(punkte_nicht_nett)
    fig.add_trace(
        go.Mesh3d(
            x=punkte_nicht_nett[:, 0], y=punkte_nicht_nett[:, 1], z=punkte_nicht_nett[:, 2],
            i=hull_nicht_nett.simplices[:, 0], j=hull_nicht_nett.simplices[:, 1], k=hull_nicht_nett.simplices[:, 2],
            color="red", opacity=0.15, name="Bereich: nicht nett gewinnt"
        )
    )

t_werte = np.linspace(pivot["T"].min(), pivot["T"].max(), 20)
r_werte = np.linspace(pivot["R"].min(), pivot["R"].max(), 20)
T_grid, R_grid = np.meshgrid(t_werte, r_werte)


P_grid = -(beta0 + beta_T * T_grid + beta_R * R_grid) / beta_P

fig.add_trace(
    go.Surface(
        x=T_grid, y=R_grid, z=P_grid,
        colorscale=[[0, "blue"], [1, "blue"]],
        opacity=0.35,
        showscale=False,
        name="Entscheidungsgrenze (P(nett)=0.5)"
    )
)

fig.update_traces(marker=dict(size=3), selector=dict(type="scatter3d"))

fig.write_html("egoistisch_vs_kooperativ_diagramm.html")