import numpy as np

import pandas as pd

# Fonction pour ajouter une variable aléatoire gaussienne à un data frame
def generation_moyenne(Data):
    Data['value_d'] = np.random.normal(Data.moyenne, Data.ecart_type, len(Data))
    Data = Data.drop(columns=['moyenne', 'ecart_type'])
    return Data

def generation_moyenne_autocorr(Data,corr=0.8):

    Data['value_d'] = None

    for techno in set(Data.techno):

        std_vec = (Data[Data['techno'] == techno].ecart_type).to_numpy()
        mean_vec = (Data[Data['techno'] == techno].moyenne).to_numpy()

        cov_matrix = np.zeros((len(std_vec), len(std_vec)))

        cov_matrix[0, 0] = std_vec[0] * std_vec[0]

        for i in range(1, len(cov_matrix)):
            cov_matrix[i, i] = std_vec[i] * std_vec[i]
            cov_matrix[i - 1, i] = std_vec[i - 1] * std_vec[i] * corr
            cov_matrix[i, i - 1] = cov_matrix[i - 1, i]

#On divise par 100 pour que la fonction multivariate_norma ne remonte pas de problème sur la contrainte de symétrie  définie-positive de la matrice

        res = np.random.multivariate_normal(mean_vec/100, cov_matrix/10000, 1).T

        Data.loc[Data.techno == techno, 'value_d'] = res*100

    return Data

# Ajout de la demande dans le dataFrame equilibre
# Il faut éviter les fonctions palier pour s'assurer de limiter des problèmes de discontinuités lors du calcul de l'équilibre
# Comme sur la véritable enchère, on fait des pas de 0,1 €/MWh et on suppose que la fonction volume=f(prix) est linéaire par morceaux
def ajout_demande(prix, volume, equilibre):
    equilibre = equilibre.append(
        {'Sens': 'D', 'Volume_Start': volume, 'Volume_End': volume, 'Prix_Start': 0, 'Prix_End': prix},
        ignore_index=True)

    if prix < 4000:
        equilibre = equilibre.append(
            {'Sens': 'D', 'Volume_Start': volume, 'Volume_End': 0, 'Prix_Start': prix, 'Prix_End': prix + 0.1},
            ignore_index=True)
        equilibre = equilibre.append(
            {'Sens': 'D', 'Volume_Start': 0, 'Volume_End': 0, 'Prix_Start': prix + 0.1, 'Prix_End': prix + 4000},
            ignore_index=True)

    return equilibre


# Ajout de l'offre dans le dataFrame equilibre
def ajout_offre(prix, volume, equilibre, production, techno):
    # On ne produit pas de volume négatif (ce cas peut arriver en raison de la distribution symétrique)
    volume = max(volume, 0)
    equilibre = equilibre.append(
        {'Sens': 'O', 'Volume_Start': volume, 'Volume_End': volume, 'Prix_Start': prix, 'Prix_End': 4000},
        ignore_index=True)

    if prix > 0:
        equilibre = equilibre.append(
            {'Sens': 'O', 'Volume_Start': 0, 'Volume_End': volume, 'Prix_Start': prix - 0.1, 'Prix_End': prix},
            ignore_index=True)
        equilibre = equilibre.append(
            {'Sens': 'O', 'Volume_Start': 0, 'Volume_End': 0, 'Prix_Start': 0, 'Prix_End': prix - 0.1},
            ignore_index=True)

    production = production.append({'techno': techno, 'Volume': volume, 'Prix': prix}, ignore_index=True)

    return [equilibre, production]


# Fonction calculant l'équilibre offre/demande

def calcul_equilibre(equilibre):
    # On échantillonne les courbes d'offre et de demande
    prix = np.unique(pd.concat([equilibre.Prix_Start, equilibre.Prix_End]))
    prix = pd.DataFrame(prix, columns=['Prix_Start_El'])
    prix['Prix_End_El'] = prix['Prix_Start_El'].shift(-1)

    prix.dropna(subset=['Prix_End_El'], inplace=True)

    # On réalise un cross-join sur l'échantillonage et la matrice de départ

    prix['key'] = 0
    equilibre['key'] = 0

    equilibre = prix.merge(equilibre, on='key')

    # on garde les intervalles compris dans l'échantillonage

    equilibre = equilibre[
        (equilibre['Prix_Start_El'] >= equilibre['Prix_Start']) & (equilibre['Prix_End_El'] <= equilibre['Prix_End'])]

    # On somme les offres et les demandes sur le même intervalle

    equilibre = equilibre.groupby(['Prix_Start_El', 'Prix_End_El', 'Sens']).sum()

    # la clé pour le CJ n'est plus nécessaire et il faut supprimer les index

    equilibre = equilibre.drop(columns=['key'])
    equilibre = equilibre.reset_index()

    # on pivote la table pour comparer offre et demande

    equilibre = equilibre.pivot(index=['Prix_Start_El', 'Prix_End_El'], columns='Sens',
                                values=['Volume_Start', 'Volume_End'])

    # s'il y a plus d'offre que de demande à 0 €/MWh
    if equilibre.iloc[1].Volume_Start.D < equilibre.iloc[1].Volume_Start.O:
        clearing_prix = 0
        clearing_volume = equilibre.iloc[1].Volume_Start.D
        return [clearing_prix, clearing_volume]

    # On détermine l'offre maximale

    Offre_Max = max(equilibre.Volume_End.O)

    # On repère le croisement des courbes

    equilibre = equilibre[
        (equilibre.Volume_Start.D > equilibre.Volume_Start.O) & (equilibre.Volume_End.D < equilibre.Volume_End.O)]
    equilibre = equilibre.reset_index()
    # S'il y a un croisement, on trouve notre prix d'équilibre
    if len(equilibre) > 0:
        clearing = (equilibre.Volume_Start.O - equilibre.Volume_Start.D) / (
                equilibre.Volume_End.D - equilibre.Volume_Start.D + equilibre.Volume_Start.O - equilibre.Volume_End.O)
        clearing_prix = clearing.values[0] * (equilibre.Prix_End_El.values[0] - equilibre.Prix_Start_El.values[0]) + \
                        equilibre.Prix_Start_El.values[0]
        clearing_volume = clearing.values[0] * (equilibre.Volume_End.D.values[0] - equilibre.Volume_Start.D.values[0]) + \
                          equilibre.Volume_Start.D.values[0]


    # S'il n'y a pas de croisement, alors il y a défaillance et donc 4000 €/MWh
    else:
        clearing_prix = 4000
        clearing_volume = Offre_Max

    return [clearing_prix, clearing_volume]