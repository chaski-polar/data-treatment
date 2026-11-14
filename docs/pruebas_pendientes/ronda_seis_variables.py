"""Ronda de tendencias en seis variables elegidas por criterio fisico (antes de mirar resultados).
Metodo: anomalias mensuales sin ciclo estacional -> media anual (>=9 meses) -> Mann-Kendall + pendiente de Sen
(IC 95 % de Sen por pares) en varios periodos, con y sin anios de El Nino extremo (1997-98, 2015-16, 2023-24);
FDR (Benjamini-Hochberg) sobre TODAS las pruebas de la ronda.
Correr con: PYTHONIOENCODING=utf-8 python ronda_seis_variables.py
"""
import json, itertools
import numpy as np, pandas as pd
from scipy import stats

R = 'D:/hackathon/NASA/'
NINO_YEARS = {1998, 2016, 2023}  # anios de pico/cierre del evento extremo en el hemisferio sur (ver nota)


def anual(s: pd.Series, min_meses=9):
    """s indexada por Timestamp mensual. Quita climatologia mensual y promedia por anio."""
    s = s.dropna()
    clim = s.groupby(s.index.month).transform('mean')
    a = (s - clim)
    g = a.groupby(a.index.year)
    return g.mean()[g.count() >= min_meses]


def mk_sen(y: pd.Series):
    x = y.index.values.astype(float); v = y.values
    n = len(v)
    if n < 8: return None
    tau, p = stats.kendalltau(x, v)
    sl = [(v[j] - v[i]) / (x[j] - x[i]) for i in range(n) for j in range(i + 1, n)]
    sen = float(np.median(sl))
    # IC aproximado de Sen (Gilbert): rangos C
    N = len(sl); var = n * (n - 1) * (2 * n + 5) / 18
    C = 1.96 * np.sqrt(var)
    lo = int(max(0, np.floor((N - C) / 2))); hi = int(min(N - 1, np.ceil((N + C) / 2)))
    ss = np.sort(sl)
    return dict(n=n, tau=tau, p=p, sen=sen, lo=float(ss[lo]), hi=float(ss[hi]))


series = {}  # nombre -> (serie mensual, unidad, factor para pendiente por decada)

# 1 Nivel del mar: panel CMEMS (zos, Humboldt) y mareografos PSMSL
pan = pd.read_csv(R + 'drive_aaron/connectivity_panel_monthly.csv', parse_dates=['date'])
def panel(region, band, col):
    q = pan[(pan.region == region) & (pan.depth_band == band)].set_index('date')[col]
    return q
series['Nivel del mar (GLORYS zos, Humboldt)'] = (panel('peru_humboldt', 'surface_2d', 'zos'), 'm')
est = {458: 'Matarani', 475: 'Talara', 771: 'Chimbote', 923: 'San Juan', 1274: 'Callao'}
for k, nom in est.items():
    rows = []
    for ln in open(R + f'datos/peru/nivel_mar_mareografos/psmsl_{k}.rlrdata'):
        t = ln.split(';')
        if len(t) < 2: continue
        try: yr = float(t[0]); val = float(t[1])
        except: continue
        if val <= -99999: continue
        rows.append((pd.Timestamp(int(yr), int(round((yr % 1) * 12 - 0.5)) % 12 + 1, 1), val / 1000.0))
    series[f'Nivel del mar (mareografo {nom})'] = (pd.Series(dict(rows)).sort_index(), 'm')

# 2 Hielo marino antartico (NSIDC, extension)
fr = []
for m in range(1, 13):
    d = pd.read_csv(R + f'datos/pesquerias/hielo_antartico_nsidc/S_{m:02d}.csv', skipinitialspace=True)
    d.columns = [c.strip() for c in d.columns]
    d = d[d.extent > 0]
    fr.append(pd.Series(d.extent.values, index=pd.to_datetime(dict(year=d.year, month=d.mo, day=1))))
series['Hielo marino antartico (extension, NSIDC)'] = (pd.concat(fr).sort_index(), 'M km2')

# 3 TSM serie larga (ERSST v5) en cajas: Nino1+2 (0-10S, 90-80W) y costa sur (10-18S, 80-70W)
import xarray as xr
ds = xr.open_dataset(R + 'datos/tendencias_largas/ersstv5_sst_mnmean.nc')
sst = ds['sst']
for nom, (la, lb, lo1, lo2) in {'Norte-centro (Nino 1+2)': (-10, 0, 270, 280), 'Costa sur': (-18, -10, 280, 290)}.items():
    b = sst.sel(lat=slice(lb, la), lon=slice(lo1, lo2)).mean(['lat', 'lon'])
    series[f'TSM ERSST {nom}'] = (pd.Series(b.values, index=pd.to_datetime(b.time.values)).astype(float), 'C')
for nom in ['Rey Jorge', 'Peninsula']:
    pass

# 3b TSM satelital por zona (monitor)
mon = json.load(open(R + 'pruebas/json_pagina/monitor_data.json', encoding='utf-8'))['records']
mdf = pd.DataFrame(mon); mdf['date'] = pd.to_datetime(mdf['date']); mdf = mdf.set_index('date')
for z in ['paita', 'chimbote', 'callao', 'pisco', 'ilo']:
    series[f'TSM satelital {z}'] = (mdf[f'sst_{z}_c'], 'C')

# 4/5 Oxigeno y temperatura 100-200 m (Humboldt) del panel
series['Oxigeno 100-200 m (Humboldt)'] = (panel('peru_humboldt', 'subsurface_100_200m', 'o2'), 'mmol/m3')
series['Temperatura 100-200 m (Humboldt)'] = (panel('peru_humboldt', 'subsurface_100_200m', 'thetao'), 'C')

# 6 Viento (ERA5/CCMP segun datos.js): componente v (meridional; negativa = hacia el ecuador) y rapidez
dj = open(R + 'repos/chaski-polar-estetica/public/assets/data/datos.js', encoding='utf-8').read()
dj = json.loads(dj[dj.find('{'):dj.rfind('}') + 1])
m0 = pd.Period(dj['meses_inicio'], 'M') if isinstance(dj['meses_inicio'], str) else None
for z, nom in {'peru_norte_paita_sechura': 'Paita', 'peru_centro_norte_chimbote': 'Chimbote', 'peru_centro_callao': 'Callao',
               'peru_sur_pisco': 'Pisco', 'peru_sur_ilo': 'Ilo'}.items():
    u = np.array(dj['series'][z]['viento_u_m_s'], dtype=float); v = np.array(dj['series'][z]['viento_v_m_s'], dtype=float)
    idx = pd.period_range(m0, periods=len(u), freq='M').to_timestamp() if m0 is not None else None
    sp = pd.Series(np.hypot(u, v), index=idx); sv = pd.Series(v, index=idx)
    series[f'Viento rapidez {nom} (hasta 2016)'] = (sp[sp.index < '2017-01-01'], 'm/s')
    series[f'Viento v {nom} (hasta 2016)'] = (sv[sv.index < '2017-01-01'], 'm/s')

# Periodos
def periodos(nombre, y):
    a, b = y.index.min(), y.index.max()
    out = [('completo', a, b)]
    for ini in (1998, 2003, 2010, 1979, 1950, 1980, 1990, 1900):
        if ini > a and ini < b - 10: out.append((f'desde {ini}', ini, b))
    return out

filas = []
for nom, (s, un) in series.items():
    s = s.copy(); s.index = pd.to_datetime(s.index)
    s = s[~s.index.duplicated()]
    y = anual(s)
    for per, a, b in periodos(nom, y):
        yy = y[(y.index >= a) & (y.index <= b)]
        for variante, yv in (('todos los anios', yy), ('sin anios Nino extremo', yy[~yy.index.isin(NINO_YEARS)])):
            r = mk_sen(yv)
            if r: filas.append(dict(variable=nom, unidad=un, periodo=f'{int(yv.index.min())}-{int(yv.index.max())}', tipo=per, variante=variante, **r))
df = pd.DataFrame(filas)
# FDR sobre todas las pruebas
p = df.p.values; o = np.argsort(p); m = len(p)
q = np.empty(m); q[o] = np.minimum.accumulate((p[o] * m / (np.arange(m) + 1))[::-1])[::-1]
df['q_fdr'] = np.minimum(q, 1)
for c in ('sen', 'lo', 'hi'): df[c + '_decada'] = df[c] * 10
df['signif_fdr'] = df.q_fdr < 0.05
df.to_csv(R + 'pruebas/fitoplancton/tablas/ronda_seis_variables.csv', index=False, encoding='utf-8')
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
print('pruebas totales:', len(df), '| significativas FDR 5 %:', int(df.signif_fdr.sum()))
c = df[(df.tipo.isin(['completo'])) | (df.tipo.str.startswith('desde'))]
print(df[df.variante == 'todos los anios'][['variable', 'periodo', 'n', 'sen_decada', 'lo_decada', 'hi_decada', 'p', 'q_fdr', 'signif_fdr']].round(4).to_string())
print('\nSIN anios Nino extremo, solo significativas FDR:')
print(df[(df.variante != 'todos los anios') & df.signif_fdr][['variable', 'periodo', 'n', 'sen_decada', 'p', 'q_fdr']].round(4).to_string())
