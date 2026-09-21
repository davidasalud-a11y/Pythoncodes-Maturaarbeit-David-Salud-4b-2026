import pandas as pd
import matplotlib
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go
from scipy.spatial import ConvexHull

nette_strategien = ["alwayscooperate", "titfortat", "two_tits_for_tat", "grofman", "friedman", "shubik"]
nicht_nette_strategien = ["alwaysdefect", "random_strategy", "feld", "own_strategy"]
alle_strategien = nette_strategien + nicht_nette_strategien

konfigurationen = pd.read_csv(f"{alle_strategien[0]}_rang.csv")[["T", "R", "P"]].drop_duplicates()

hierarchien = {
    "TRP": (konfigurationen["T"] >= konfigurationen["R"]) & (konfigurationen["R"] >= konfigurationen["P"]),
    "TPR": (konfigurationen["T"] >= konfigurationen["P"]) & (konfigurationen["P"] >= konfigurationen["R"]),
    "RTP": (konfigurationen["R"] >= konfigurationen["T"]) & (konfigurationen["T"] >= konfigurationen["P"]),
    "RPT": (konfigurationen["R"] >= konfigurationen["P"]) & (konfigurationen["P"] >= konfigurationen["T"]),
}

hierarchie_farben = {"TRP": "red", "TPR": "orange", "RTP": "blue", "RPT": "purple"}

hierarchie_hulls = {}
for name, maske in hierarchien.items():
    punkte = konfigurationen[maske].values
    if len(punkte) >= 4:
        hull = ConvexHull(punkte)
        hierarchie_hulls[name] = (punkte, hull)

cmap = matplotlib.colormaps["RdYlGn"]
farben = [mcolors.to_hex(cmap(1 - i / 9)) for i in range(10)]
farbzuordnung = {str(rang): farbe for rang, farbe in zip(range(1, 11), farben)}

for name in alle_strategien:
    strategie_rang = pd.read_csv(f"{name}_rang.csv").sort_values(["T", "R", "P"])
    strategie_rang["Rang"] = strategie_rang["Rang"].astype(int).astype(str)

    fig = px.scatter_3d(
        strategie_rang,
        x="T", y="R", z="P",
        color="Rang",
        color_discrete_map=farbzuordnung,
        category_orders={"Rang": [str(i) for i in range(1, 11)]},
        hover_data=["T", "R", "P", "Score"]
    )

    for hname, (punkte, hull) in hierarchie_hulls.items():
        farbe = hierarchie_farben[hname]

        fig.add_trace(
            go.Mesh3d(
                x=punkte[:, 0], y=punkte[:, 1], z=punkte[:, 2],
                i=hull.simplices[:, 0], j=hull.simplices[:, 1], k=hull.simplices[:, 2],
                color=farbe,
                opacity=0.08,
                flatshading=True,
                lighting=dict(diffuse=0, specular=0, ambient=1),
                hoverinfo="skip",
                name=f"Hierarchie {hname}",
                showlegend=True
            )
        )

    fig.update_traces(marker=dict(size=3), selector=dict(type="scatter3d"))
    fig.update_layout(scene=dict(xaxis_title="T", yaxis_title="R", zaxis_title="P"))
    fig.write_html(f"{name}_diagramm.html")