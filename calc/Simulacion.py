import matplotlib
matplotlib.use('Agg')
import random
import io
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

class Simulacion:

    def modeloInventario(self):
        D = 5000.00
        Co = 25.00
        Ch = 0.60
        P = 4.35
        Tespera = 6
        DiasAno = 365

        Q = round(sqrt(((2*Co*D)/Ch)),2)
        N = round(D / Q,2)
        R = round((D / DiasAno) * Tespera,2)
        T = round(DiasAno / N,2)
        CoT = N * Co
        ChT = round(Q / 2 * Ch,2)
        MOQ = round(CoT + ChT,2)
        CTT = round(P * D + MOQ,2)

        data = {'datos':
            {
                'Q':Q,
                'CoT':CoT,
                'ChT':ChT,
                'MOQ':MOQ,
                'CTT': CTT,
                'N': N,
                'R':R,
                'T':T
            }
        }
        
        indice = ['Q','Costo_ordenar','Costo_Mantenimiento','Costo_total','Diferencia_Costo_Total']
        periodo = np.arange(1,19)
        Lista = self.generarLista(Q)
        Lista.sort()
        dfQ = pd.DataFrame(index=periodo, columns=indice).fillna(0)
        dfQ['Q'] = Lista
        for period in periodo:
            dfQ['Costo_ordenar'][period] = D * Co / dfQ['Q'][period]
            dfQ['Costo_Mantenimiento'][period] = dfQ['Q'][period] * Ch / 2
            dfQ['Costo_total'][period] = dfQ['Costo_ordenar'][period] + dfQ['Costo_Mantenimiento'][period]
            dfQ['Diferencia_Costo_Total'][period] = dfQ['Costo_total'][period] - MOQ
        data ['df'] = dfQ
        dfG = dfQ.loc[:,'Costo_ordenar':'Costo_total']
        
        img = io.BytesIO()
        plt.figure(figsize=(10,5))
        plt.grid()
        plt.plot(dfG)
        plt.legend(('Costo Ordenar','Costo Mantenimiento','Costo total'), loc="center")
        plt.savefig(img, format='png')
        plt.clf()
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()

        data['img_url'] = img_url

        return data
        
    def generarLista(self, Q):
        n=18
        Q_Lista = []
        i=1
        Qi = Q
        Q_Lista.append(Qi)
        for i in range(1,9):
            Qi = Qi - 60
            Q_Lista.append(Qi)
        
        Qi = Q
        for i in range(9, n):
            Qi = Qi + 60
            Q_Lista.append(Qi)
        
        return Q_Lista

    def banco(self):
        landa = 4.432
        nu = 6.5 
        #La probabilidad de hallar el sistema ocupado o utilización del sistema:
        p=landa/nu
        #La probabilidad de que no haya unidades en el sistema este vacía u ocioso : 
        Po = 2.53  - (landa/nu)
        #Longitud esperada en cola, promedio de unidades en la línea de espera:
        Lq = landa*landa / (nu * (nu - landa))
        #/ (nu * (nu - landa))
        # Número esperado de clientes en el sistema(cola y servicio) : 
        L = landa /(nu - landa)
        #El tiempo promedio que una unidad pasa en el sistema:
        W = 1 / (nu - landa)
        #Tiempo de espera en cola:
        Wq = W - (1.0 / nu)
        #La probabilidad de que haya n unidades en el sistema: 
        n= 1
        Pn = (landa/nu)*n*Po

        i = 0
        # Landa y nu ya definidos
        # Atributos del DataFrame
        numClientes=100
        i = 0
        indice = ['ALL','ASE','TILL','TISE','TIRLL','TIISE','TIFSE','TIESP','TIESA']

        Clientes = np.arange(numClientes)
        dfLE = pd.DataFrame(index=Clientes, columns=indice).fillna(0.000)
        np.random.seed(100)
        for i in Clientes:
            if i == 0:
                dfLE['ALL'][i] = round(random.random(),2)
                dfLE['ASE'][i] = round(random.random(),2)
                dfLE['TILL'][i] = round(-1/landa*np.log(dfLE['ALL'][i]),2)
                dfLE['TISE'][i] = round(-1/nu*np.log(dfLE['ASE'][i]),2)
                dfLE['TIRLL'][i] = round(dfLE['TILL'][i],2)
                dfLE['TIISE'][i] = round(dfLE['TIRLL'][i],2)
                dfLE['TIFSE'][i] = round(dfLE['TIISE'][i] + dfLE['TISE'][i],2)
                dfLE['TIESA'][i] = round(dfLE['TIESP'][i] + dfLE['TISE'][i],2)
            else:
                dfLE['ALL'][i] = round(random.random(),2)
                dfLE['ASE'][i] = round(random.random(),2)
                dfLE['TILL'][i] = round(-1/landa*np.log(dfLE['ALL'][i]),2)
                dfLE['TISE'][i] = round(-1/nu*np.log(dfLE['ASE'][i]),2)
                dfLE['TIRLL'][i] = round(dfLE['TILL'][i] + dfLE['TIRLL'][i-1],2)
                dfLE['TIISE'][i] = round(max(dfLE['TIRLL'][i],dfLE['TIFSE'][i-1]),2) 
                dfLE['TIFSE'][i] = round(dfLE['TIISE'][i] + dfLE['TISE'][i],2)
                dfLE['TIESP'][i] = round(dfLE['TIISE'][i] - dfLE['TIRLL'][i],2)
                dfLE['TIESA'][i] = round(dfLE['TIESP'][i] + dfLE['TISE'][i],2)
        columnas = ["A_LLEGADA","A_SERVICIO","TIE_LLEGADA","TIE_SERVICIO",
            "TIE_EXACTO_LLEGADA","TIE_INI_SERVICIO","TIE_FIN_SERVICIO","TIE_ESPERA","TIE_SALIDA"]
        nuevas_columnas = pd.core.indexes.base.Index(columnas)
        dfLE.columns = nuevas_columnas
        img = io.BytesIO()
        plt.figure(figsize=(10,5))
        plt.grid()
        for i in columnas:
            plt.plot(dfLE.loc[:,i])
        plt.legend(columnas, loc="upper left")
        plt.savefig(img, format='png')
        plt.clf()
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()

        return {'img_url': img_url, 'df': dfLE}
    
    def simulacionmontecarlo(self, n, x0, a, c, m):
        if(n<=0 or x0<=0 or a<=0 or c <= 0 or m<=0):
            raise Exception('Solo puede ingresar valores positivos!')
        x = [1] * n
        r = [0.1] * n
        for i in range(0, n):
            x[i] = ((a*x0)+c) % m
            x0 = x[i]
            r[i] = x0 / m
        d = {'Xn': x, 'ri': r }
        df = pd.DataFrame(data=d)
        

        # Grafica
        img = io.BytesIO()
        plt.figure(figsize=(10,5))
        plt.plot(r,marker='+', color='cyan')
        plt.xlabel('Serie')
        plt.ylabel('Aleatorios')
        plt.savefig(img, format='png')
        plt.clf()
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()
        
        return (df, img_url)
    
        
s = Simulacion()