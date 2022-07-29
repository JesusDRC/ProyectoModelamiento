import io
import matplotlib
matplotlib.use('Agg')
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Pronostico:

    def promedioMovil(self, x:str, y:str, xlbl:str, ylbl:str):
        # Convertir en lista los datos separandolos con una ,
        datosX = []
        datosY = []
        for i in x.split(','):
            datosX.append(float(i))
        for i in y.split(','):
            datosY.append(float(i))

        data = {xlbl: datosX, ylbl: datosY}

        movil = pd.DataFrame(data)
        # calculamos para la primera media móvil MMO_3
        for i in range(0,movil.shape[0]-2):
            movil.loc[movil.index[i+2],'MMO_3'] = np.round(((movil.iloc[i,1]+movil.iloc[i+1,1]+movil.iloc[i+2,1])/3),1)
        #  calculamos para la segunda media móvil MMO_4 
        for i in range(0,movil.shape[0]-3):
            movil.loc[movil.index[i+3],'MMO_4'] = np.round(((movil.iloc[i,1]+movil.iloc[i+1,1]+movil.iloc[i+2,1]+movil.iloc[i+3,1])/4),1)
        
        proyeccion = movil.iloc[movil.shape[0]-3:,[1,2,3]]
        p1,p2,p3 =proyeccion.mean()
        # incorporamos al DataFrame
        intervalo = datosX[1]-datosX[0]
        a = movil.append({xlbl:datosX[-1]+intervalo,ylbl:p1, 'MMO_3':p2, 'MMO_4':p3},ignore_index=True)
        # mostramos los resultados
        a['e_MM3'] = a[ylbl]-a['MMO_3']
        a['e_MM4'] = a[ylbl]-a['MMO_4']
         # calculamos el promedio de los cada una de las columnas de df
        m1,m2,m3,m4,m5,m6 =a.mean()
        # Grafica
        img = io.BytesIO()
        plt.figure(figsize=(10,5))
        plt.grid()
        plt.plot(a[ylbl],label=ylbl,marker='o', color='green')
        plt.plot(a['MMO_3'],label=xlbl, marker='*', color='red')
        plt.plot(a['MMO_4'],label=xlbl, marker='+', color='purple')
        plt.legend(loc=2)
        plt.savefig(img, format='png')
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()

        return(a,img_url, round(m5), round(m6), round(m4), round(m3), round(m2), round(m1))

    def suavizacionExponencial(self, x:str, y:str, xlbl:str, ylbl:str):
        # Convertir en lista los datos separandolos con una ,
        datosX = []
        datosY = []
        for i in x.split(','):
            datosX.append(float(i))
        for i in y.split(','):
            datosY.append(float(i))

        data = {xlbl: datosX, ylbl: datosY}

        movil = pd.DataFrame(data)
        alfa = 0.1
        unoalfa = 1. - alfa
        for i in range(0,movil.shape[0]-1):
            movil.loc[movil.index[i+1],'SN'] = np.round(movil.iloc[i,1],1)
        for i in range(2,movil.shape[0]):
            movil.loc[movil.index[i],'SN'] = np.round(movil.iloc[i-1,1],1)*alfa + np.round(movil.iloc[i-1,2],1)*unoalfa
        i=i+1
        intervalo = datosX[1]-datosX[0]
        p1=0
        p2=np.round(movil.iloc[i-1,1],1)*alfa + np.round(movil.iloc[i-1,2],1)*unoalfa
        a = movil.append({xlbl:datosX[-1]+intervalo,ylbl:p1, 'SN':p2},ignore_index=True)
        
        return a

    def regresionLineal(self, x:str, y:str, xlbl:str, ylbl:str):
        # Convertir en lista los datos separandolos con una ,
        datosX = []
        datosY = []
        for i in x.split(','):
            datosX.append(float(i))
        for i in y.split(','):
            datosY.append(float(i))

        data = {xlbl: datosX, ylbl: datosY}
        a = pd.DataFrame(data)
        x = a.index.values
        y = a[ylbl]
        # ajuste de la recta (polinomio de grado 1 f(x) = ax + b)
        p = np.polyfit(x,y,1) # 1 para lineal, 2 para polinomio ...
        yAjuste = p[0]*x + p[1]
        plt.plot(x,y,'b.', color='red')
        # Dibujamos la recta de ajuste
        plt.plot(x,yAjuste, color='purple' )
        img = io.BytesIO()
        plt.title('Ajuste lineal')
        plt.xlabel('Eje x')
        plt.ylabel('Eje y')
        plt.legend(('Datos','Ajuste',), loc="upper left")
        plt.savefig(img, format='png')
        plt.clf()
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()
        
        return img_url
    
    def regresionLinealCuadratica(self, x:str, y:str, xlbl:str, ylbl:str):
        # Convertir en lista los datos separandolos con una ,
        datosX = []
        datosY = []
        for i in x.split(','):
            datosX.append(float(i))
        for i in y.split(','):
            datosY.append(float(i))

        data = {xlbl: datosX, ylbl: datosY}
        a = pd.DataFrame(data)
        x = a.index.values
        y = a[ylbl]

        p = np.polyfit(x,y,2)

        y_ajuste = p[0]*x*x + p[1]*x + p[2]
        # dibujamos los datos experimentales de la recta 
        img = io.BytesIO()
        plt.plot(x,y,'b.', color='green' )
        # Dibujamos la curva de ajuste
        plt.plot(x,y_ajuste, color='cyan')
        plt.title('Ajuste de minimos cuadrados')
        plt.xlabel('Eje x')
        plt.ylabel('Eje y')
        plt.legend(['Datos','Ajuste'], loc="upper left")
        plt.savefig(img, format='png')
        img.seek(0)
        img_url = base64.b64encode(img.getvalue()).decode()
        return img_url
                
