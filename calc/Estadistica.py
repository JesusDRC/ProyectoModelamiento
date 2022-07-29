import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

class Estadistica:

    def __init__(self):

        self.df = pd.read_excel('info/Conjuntodedatosderiesgodesaludmaterna.xlsx')
    
    def datosExcel(self):
        return self.df

    def graficoFechaDolares(self):

        img = io.BytesIO()

        fecha = self.df['fecha'].unique()
        precio = []
        for i in fecha:
            suma = self.df.loc[self.df['fecha'] == i, ['precio-mercado']].sum()[0]
            precio.append(suma)

        plt.figure(figsize=(10,5))
        plt.bar(fecha, precio, color="salmon")
        plt.title('Precio de las Bitcoin en el mercado por fecha')
        plt.xticks(rotation=10)
        plt.ylabel('Precio de las bitcoin en el mercado ')
        plt.savefig(img, format='png')
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()
        return img_url

    def graficoFrecuenciaPrecio(self):

        img = io.BytesIO()

        x = self.df['precio-mercado']
        plt.figure(figsize=(10,5))
        plt.hist(x, bins=None, color="purple")
        plt.title('Frecuencia de el precio de las bitcoins en el mercado ')
        plt.xticks(rotation=10)
        plt.ylabel('Frecuencia')

        plt.savefig(img, format='png')
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()
        return img_url
        
    def graficocriptomonedas(self):
    
        img = io.BytesIO()

        fecha = self.df['fecha'].unique()
        pagos = []
        for i in fecha:
            suma = self.df.loc[self.df['fecha'] == i, ['pagos-moneda']].sum()[0]
            pagos.append(suma)

        plt.figure(figsize=(10,5))
        plt.bar(fecha, pagos, color="cyan")
        plt.title('Pagos de las Bitcoin en el mercado por fecha')
        plt.xticks(rotation=10)
        plt.ylabel('Pagos de las bitcoin en el mercado ')
        plt.savefig(img, format='png')
        img.seek(0)

        img_url = base64.b64encode(img.getvalue()).decode()
        return img_url