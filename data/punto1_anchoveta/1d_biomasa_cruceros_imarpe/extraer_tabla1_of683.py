# Extrae la Tabla 1 (biomasa desovante acustica por crucero, 1964-2020) del Oficio 683-2021-IMARPE/PCD.
import pymupdf,re,csv,sys
pdf,out=sys.argv[1],sys.argv[2]
d=pymupdf.open(pdf)
txt=''
on=False
for p in d:
    t=p.get_text()
    if 'Tabla 1.' in t: on=True
    if on:
        txt+='\n'+t
        if 'Tabla 2' in t: break
txt=txt.split('Tabla 2')[0]
L=[l.strip() for l in txt.split('\n') if l.strip()]
i=L.index('Índice')+1
rows=[];num=re.compile(r'^\d+$');flt=re.compile(r'^\d{4}\.\d+$')
while i<len(L):
    if num.match(L[i]) and (not rows or int(L[i])==rows[-1][0]+1):
        n=int(L[i]);j=i+1;fu=[]
        while not flt.match(L[j]): fu.append(L[j]);j+=1
        mes,bio,a,b,idx=L[j:j+5]
        rows.append([n,' '.join(fu),mes,bio,a,b,idx]);i=j+5
    else: i+=1
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['n_obs','fuente','mes_decimal','biomasa_desovante_millones_t','par_alfa','par_beta','indice'])
    w.writerows(rows)
print(len(rows),rows[0],rows[-1])
