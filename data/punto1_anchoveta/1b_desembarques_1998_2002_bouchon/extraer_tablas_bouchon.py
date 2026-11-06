# Extrae las tablas de desembarque mensual por puerto de Bouchon et al. 2018 (paginas giradas).
import pymupdf,sys,csv,json
pdf,out=sys.argv[1],sys.argv[2]
PAG={1998:49,1999:50,2000:51,2001:52,2002:53,2003:54}
MES=['ENE','FEB','MARZ','MAR','ABR','MAY','JUN','JUL','AGO','SET','OCT','NOV','DIC','TOTAL']
d=pymupdf.open(pdf);res={}
for anio,pg in PAG.items():
    W=d[pg-1].get_text('words')
    # cabecera de meses: la columna que contiene 'PUERTO\MES'
    hx=[w for w in W if w[4].startswith('PUERTO')][0]
    head=[w for w in W if abs(w[0]-hx[0])<6 and w[4] in MES]
    head=sorted(head,key=lambda w:w[1])
    meses=[(w[4].replace('MARZ','MAR'),(w[1]+w[3])/2) for w in head]
    # nombres de puerto: palabras en mayuscula en la misma fila (y) que 'PUERTO\MES'
    ports=[w for w in W if (abs(w[1]-hx[1])<6 or abs(w[3]-hx[3])<6) and w is not hx and w[4]!='PERU' and w[4].replace('.','').replace('+','').isupper()]
    tabla={}
    for pw in ports:
        cx=(pw[0]+pw[2])/2
        nums=[w for w in W if abs((w[0]+w[2])/2-cx)<7 and w[4].replace(',','').isdigit() and abs((w[1]+w[3])/2-(hx[1]+hx[3])/2)>15]
        fila={}
        for n in nums:
            cy=(n[1]+n[3])/2
            m,dist=min(((m,abs(cy-y)) for m,y in meses),key=lambda t:t[1])
            if dist<23.5:
                if m in fila: print('CHOQUE',anio,pw[4],m)
                fila[m]=fila.get(m,0)+int(n[4].replace(',',''))
            else: print('SIN MES',anio,pw[4],n[4],round(cy))
        tabla['PERU' if pw[4]=='TOTAL' else pw[4]]=fila
    # columna TOTAL PERU (la palabra 'TOTAL' en la fila de puertos)
    res[anio]=tabla
    # control: suma de meses = TOTAL de cada puerto
    for p,f in tabla.items():
        s=sum(v for k,v in f.items() if k!='TOTAL')
        if 'TOTAL' not in f: print(anio,p,'SIN TOTAL')
        elif abs(s-f['TOTAL'])>2: print(anio,p,'suma meses',s,'TOTAL',f['TOTAL'])
    print(anio,'puertos',len(tabla),sorted(tabla))
json.dump(res,open(out,'w'),indent=1)
