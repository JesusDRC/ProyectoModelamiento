
from flask import Flask, request
from flask.templating import render_template
from calc.Aleatorio import Aleatorio
from calc.Estadistica import Estadistica
from calc.Pronostico import Pronostico
from calc.Simulacion import Simulacion

est = Estadistica()
aleatorio = Aleatorio()
pronostico = Pronostico()
simulacion = Simulacion()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mediana')
def mediana():
    return render_template('mediamm.html')
@app.route('/sistemaInv')
def inventario2():
    return render_template('sistemaInventario.html')

@app.route('/FrecuenciaFecha')
def grafica1():
    return render_template('grafica1.html',
        imagen1 = est.graficoFechaDolares())
    
@app.route('/Preciomercado')
def grafica2():
    return render_template('grafica2.html',
        imagen2 = est.graficoFrecuenciaPrecio())
    
@app.route('/Pagomonedas')
def grafica3():
    return render_template('grafica3.html',
        imagen3 = est.graficocriptomonedas())

@app.route('/Datos')
def proyectoDatos():
    return render_template('proyectoDatos.html',
        data=est.datosExcel())

@app.route('/Numerosaleatorios')
def aleatorios():
    return render_template('numerosaleatorios.html')

@app.route('/Pronosticos')
def pronosticos():
    return render_template('pronosticos.html')


@app.route('/inventario', methods=['GET'])
def inventario():
    data = simulacion.modeloInventario()
    return render_template('inventario.html',
        datos=data['datos'],
        df = data['df'],
        imagen = data['img_url'])
    

@app.route('/lineaespera', methods=['GET'])
def banco():
    data = simulacion.banco()
    return render_template('linea.html',
        df = data['df'],
        imagen = data['img_url'])
        
@app.route('/calcularSistemaInventario', methods=['GET', 'POST'])
def calcularSistemaInventario():
    D = request.form.get("demanda", type=float)
    Co = request.form.get("costoOrdenar", type=float)
    Ch = request.form.get("costoMantenimiento", type=float)
    P = request.form.get("costoProducto", type=float)
    Tespera = request.form.get("tiempoEspera", type=float)
    DiasAno = request.form.get("diasAno", type=int)
    num = request.form.get("numeroIteraciones", type=int)

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from pandas import ExcelWriter
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import io
    from io import BytesIO
    import base64
    import math
    from math import sqrt
    from pandas import DataFrame

    Q = round(sqrt(((2*Co*D)/Ch)), 2)
    N = round(D / Q, 2)
    R = round((D / DiasAno) * Tespera, 2)
    T = round(DiasAno / N, 2)
    CoT = N * Co
    ChT = round(Q / 2 * Ch, 2)
    MOQ = round(CoT + ChT, 2)
    CTT = round(P * D + MOQ, 2)

    df = pd.DataFrame(columns=('Q', 'N', 'R', 'T', 'CoT', 'ChT', 'MOQ', 'CTT'))
    df.loc[len(df)] = [Q, N, R, T, CoT, ChT, MOQ, CTT]
    df

    data = df.to_html(classes="table table-striped",
                      justify="justify-all", border=0)

    # Programa para generar el gráfico de costo mínimo
    indice = ['Q', 'Costo_ordenar', 'Costo_Mantenimiento',
        'Costo_total', 'Diferencia_Costo_Total']
    # Generamos una lista ordenada de valores de Q

    periodo = np.arange(0, num)

    def genera_lista(Q):
        n = num
        Q_Lista = []
        i = 1
        Qi = Q
        Q_Lista.append(Qi)
        for i in range(1, 9):
            Qi = Qi - 60
            Q_Lista.append(Qi)

        Qi = Q
        for i in range(9, n):
            Qi = Qi + 60
            Q_Lista.append(Qi)
        return Q_Lista

    Lista = genera_lista(Q)
    Lista.sort()

    dfQ = DataFrame(index=periodo, columns=indice).fillna(0)

    dfQ['Q'] = Lista
    #dfQ

    for period in periodo:
        dfQ['Costo_ordenar'][period] = D * Co / dfQ['Q'][period]
        dfQ['Costo_Mantenimiento'][period] = dfQ['Q'][period] * Ch / 2
        dfQ['Costo_total'][period] = dfQ['Costo_ordenar'][period] + \
            dfQ['Costo_Mantenimiento'][period]
        dfQ['Diferencia_Costo_Total'][period] = dfQ['Costo_total'][period] - MOQ
    dfQ

    # Graficamos los numeros generados
    buf = io.BytesIO()
    plt.plot(dfQ['Costo_ordenar'], label='Costo_ordenar')
    plt.plot(dfQ['Costo_Mantenimiento'], label='Costo_Mantenimiento')
    plt.plot(dfQ['Costo_total'], label='Costo_total')
    plt.legend()

    fig = plt.gcf()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    fig.clear()
    plot_url = base64.b64encode(buf.getvalue()).decode('UTF-8')

    data2 = dfQ.to_html(classes="table table-hover table-striped",
                        justify="justify-all", border=0)

    def make_data(product, policy, periods):
        periods += 1
        # Create zero-filled Dataframe
        period_lst = np.arange(periods)  # index
        header = ['INV_INICIAL', 'INV_NETO_INICIAL', 'DEMANDA', 'INV_FINAL', 'INV_FINAL_NETO',
            'VENTAS_PERDIDAS', 'INV_PROMEDIO', 'CANT_ORDENAR', 'TIEMPO_LLEGADA']
        df = DataFrame(index=period_lst, columns=header).fillna(0)
        # Create a list that will store each period order
        order_l = [Order(quantity=0, lead_time=0)
                   for x in range(periods)]
                       # Fill DataFrame
        for period in period_lst:
            if period == 0:
                df['INV_INICIAL'][period] = product.initial_inventory
                df['INV_NETO_INICIAL'][period] = product.initial_inventory
                df['INV_FINAL'][period] = product.initial_inventory
                df['INV_FINAL_NETO'][period] = product.initial_inventory
            if period >= 1:
                df['INV_INICIAL'][period] = df['INV_FINAL'][period - 1] + \
                    order_l[period - 1].quantity
                df['INV_NETO_INICIAL'][period] = df['INV_FINAL_NETO'][period -
                    1] + pending_order(order_l, period)
                #demand = int(product.demand())
                demand = D
                # We can't have negative demand
                if demand > 0:
                    df['DEMANDA'][period] = demand
                else:
                    df['DEMANDA'][period] = 0
                # We can't have negative INV_INICIAL
                if df['INV_INICIAL'][period] - df['DEMANDA'][period] < 0:
                    df['INV_FINAL'][period] = 0
                else:
                    df['INV_FINAL'][period] = df['INV_INICIAL'][period] - \
                        df['DEMANDA'][period]
                order_l[period].quantity, order_l[period].lead_time = placeorder(
                    product, df['INV_FINAL'][period], policy, period)
                df['INV_FINAL_NETO'][period] = df['INV_NETO_INICIAL'][period] - \
                    df['DEMANDA'][period]
                if df['INV_FINAL_NETO'][period] < 0:
                    df['VENTAS_PERDIDAS'][period] = abs(
                        df['INV_FINAL_NETO'][period])
                    df['INV_FINAL_NETO'][period] = 0
                else:
                    df['VENTAS_PERDIDAS'][period] = 0
                df['INV_PROMEDIO'][period] = (
                    df['INV_NETO_INICIAL'][period] + df['INV_FINAL_NETO'][period]) / 2.0
                df['CANT_ORDENAR'][period] = order_l[period].quantity
                df['TIEMPO_LLEGADA'][period] = order_l[period].lead_time
        return df

    def pending_order(order_l, period):
        """Return the order that arrives in actual period"""
        indices = [i for i, order in enumerate(order_l) if order.quantity]
        sum = 0
        for i in indices:
            if period-(i + order_l[i].lead_time+1) == 0:
                sum += order_l[i].quantity
        return sum

    def demanda(self):
            if self.demand_dist == "Constant":
                return self.demand_p1
            elif self.demand_dist == "Normal":
                return make_distribution(
                    np.random.normal,
                    self.demand_p1,
                    self.demand_p2)()
            elif self.demand_dist == "Triangular":
                return make_distribution(
                    np.random_triangular,
                    self.demand_p1,
                    self.demand_p2,
                    self.demand_p3)()
    def lead_time(self):
            if self.leadtime_dist == "Constant":
                return self.leadtime_p1
            elif self.leadtime_dist == "Normal":
                return make_distribution(
                    np.random.normal,
                    self.leadtime_p1,
                    self.leadtime_p2)()
            elif self.leadtime_dist == "Triangular":
                return make_distribution(
                    np.random_triangular,
                    self.leadtime_p1,
                    self.leadtime_p2,
                    self.leadtime_p3)()

    def __repr__(self):
           return '<Product %r>' % self.name

    def placeorder(product, final_inv_pos, policy, period):
        #lead_time = int(product.lead_time())
        lead_time = Tespera
        # Qs = if we hit the reorder point s, order Q units
        if policy['method'] == 'Qs' and \
                final_inv_pos <= policy['param2']:
            return policy['param1'], lead_time
        # RS = if we hit the review period R and the reorder point S, order: (S -
        # final inventory pos)
        elif policy['method'] == 'RS' and \
            period % policy['param1'] == 0 and \
                final_inv_pos <= policy['param2']:
            return policy['param2'] - final_inv_pos, lead_time
        else:
            return 0, 0

    politica = {'method': "Qs", 'param1': 50,'param2': 20}

    class Order(object):
        """Object that stores basic data of an order"""

        def __init__(self, quantity, lead_time):
            self.quantity = quantity
            self.lead_time = lead_time

    class product(object):
        def __init__ (self, name,price,order_cost,initial_inventory,demand_dist,demand_p1,demand_p2,demand_p3,leadtime_dist,leadtime_p1,leadtime_p2,leadtime_p3):
            self.name = name
            self.price = price
            self.order_cost = order_cost
            self.initial_inventory = initial_inventory
            self.demand_dist = demand_dist
            self.demand_p1 = demand_p1
            self.demand_p2 = demand_p2
            self.demand_p3 = demand_p3
            self.leadtime_dist = leadtime_dist
            self.leadtime_p1 = leadtime_p1
            self.leadtime_p2 = leadtime_p2
            self.leadtime_p3 = leadtime_p3
    producto = product("Mesa", 18.0, 20.0,100,"Constant",80.0,0.0,0.0,"Constant",1.0,0.0,0.0)

    num = num - 1
    df = make_data(producto, politica, num)
    df

    data3 = df.to_html(classes="table table-hover table-striped",
                       justify="justify-all", border=0)

    """ writer = ExcelWriter("static/file/data.xlsx")
    df.to_excel(writer, index=False)
    writer.save()

    df.to_csv("static/file/data.csv", index=False) """

    return render_template('printSistemaInventario.html', data=data, data2=data2, data3=data3, image=plot_url)


@app.route('/Analisis', methods=['GET', 'POST'])
def calcularMediaModaMediana():

    file = request.files['file'].read()
    tipoArch= request.form.get("tipoarchivo")
    columna = request.form.get("nombreColumna")

    # importamos la libreria Pandas, matplotlib y numpy que van a ser de mucha utilidad para poder hacer gráficos
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import io
    from io import BytesIO
    import base64
    from pandas import DataFrame

    # leemos los datos de la tabla del directorio Data de trabajo
    if tipoArch=='1':
        
        datos = pd.read_excel(file)
        
        
    elif tipoArch=='2':
        datos = pd.read_csv(io.StringIO(file.decode('utf-8')))
        
    elif tipoArch=='3':
        datos = pd.read_json(file)

    elif tipoArch=='4':
        datos = pd.read_html(file)
    elif tipoArch=='5':
        datos = pd.read_clipboard(file)

    elif tipoArch=='6':
        datos = pd.read_feather(file)

    elif tipoArch=='7':
        datos = pd.read_fwf(file)

    elif tipoArch=='8':
        datos = pd.read_gbq(file)

    elif tipoArch=='9':
        datos = pd.read_parquet(file)

    elif tipoArch=='10':
        datos = pd.read_pickle(file)

    elif tipoArch=='11':
        datos = pd.read_msgpack(file)

    elif tipoArch=='12':
        datos = pd.read_sas(file)

    elif tipoArch=='13':
        datos = pd.read_sql(file)

    elif tipoArch=='14':
        datos = pd.read_sql_query(file)
    elif tipoArch=='15':
        datos = pd.read_sql_table(file)
    
    # Presentamos los datos en un DataFrame de Pandas
    datos

    # Preparando para el grafico para la columna TOTAL PACIENTES
    buf = io.BytesIO()
    x = datos[columna]
    plt.figure(figsize=(10, 5))
    plt.hist(x, bins=8, color='blue')
    plt.axvline(x.mean(), color='red', label='Media')
    plt.axvline(x.median(), color='yellow', label='Mediana')
    plt.axvline(x.mode()[0], color='green', label='Moda')
    plt.xlabel('Total de datos')
    plt.ylabel('Frecuencia')
    plt.legend()

    fig = plt.gcf()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    fig.clear()
    plot_url = base64.b64encode(buf.getvalue()).decode('UTF-8')

    media = datos[columna].mean()
    moda = datos[columna].mode()
    mediana = datos[columna].median()

    df = pd.DataFrame(columns=('Media', 'Moda', 'Mediana'))
    df.loc[len(df)] = [media, moda, mediana]
    df
    data = df.to_html(classes="table table-striped",
                      justify="justify-all", border=0)

    # Tomamos los datos de las columnas
    df2 = datos[[columna]].describe()
    # describe(), nos presenta directamente la media, desviación standar, el valor mínimo, valor máximo, el 1er cuartil, 2do Cuartil, 3er Cuartil
    data2 = df2.to_html(classes="table table-hover table-striped",
                        justify="justify-all", border=0)

    return render_template('printMediaMedianaModa.html', data=data, data2=data2, image=plot_url)

@app.route('/cuadradosMedios', methods=['POST', 'GET'])
def cuadradosMedio():
    if request.method == 'POST':
        try:
            data = aleatorio.cuadradosMedios(
                int(request.form['n']),
                int(request.form['r']))

            return render_template('cuadradosMedios.html',
                datos = data[0],
                imagen1 = data[1])
        except Exception as error:
            return render_template('cuadradosMedios.html',
                error=error
            )
    elif request.method == 'GET':
        return render_template('cuadradosMedios.html')

@app.route('/congruenciaLineal', methods=['POST', 'GET'])
def congruenciaLineal():
    if request.method == 'POST':
        try:
            data = aleatorio.congruencialLineal(
                int(request.form['n']),
                int(request.form['x']),
                int(request.form['a']),
                int(request.form['c']),
                int(request.form['m']))

            return render_template('congruenciaLineal.html',
                datos = data[0],
                imagen = data[1])
        except Exception as error:
            return render_template('congruenciaLineal.html',
                error = error)

    elif request.method == 'GET':
        return render_template('congruenciaLineal.html')

@app.route('/congruencialMultiplicativo', methods=['POST', 'GET'])
def congruencialMultiplicativo():
    if request.method == 'POST':
        try:
            data = aleatorio.congruencialMultiplicativo(
                int(request.form['n']),
                int(request.form['x']),
                int(request.form['a']),
                int(request.form['m']))

            return render_template('congruencialMultiplicativo.html',
                datos = data[0],
                imagen = data[1])
        except Exception as error:
            return render_template('congruencialMultiplicativo.html',
                error = error)

    elif request.method == 'GET':
        return render_template('congruencialMultiplicativo.html')

@app.route('/distribucionPoisson', methods=['POST', 'GET'])
def distribucionPoisson():
    if request.method == 'POST':
        try:
            data = aleatorio.distribucionPoisson(
                int(request.form['landa']))

            return render_template('distribucionPoisson.html',
                imagen = data)
        except Exception as error:
            return render_template('distribucionPoisson.html',
                error = error)

    elif request.method == 'GET':
        return render_template('distribucionPoisson.html')

@app.route('/promedioMovil', methods=['POST', 'GET'])
def promedioMovil():
    if request.method == 'POST':
        try:
            data = pronostico.promedioMovil(
                request.form['x'],
                request.form['y'],
                request.form['xlbl'],
                request.form['ylbl'])

            return render_template('promedioMovil.html',
                datos = data[0],
                imagen = data[1],
                mediaMovil3 = data[2],
                mediaMovil4 = data[3])
        except Exception as error:
            return render_template('promedioMovil.html',
                error = error)

    elif request.method == 'GET':
        return render_template('promedioMovil.html')


@app.route('/suavizacionExponencial', methods=['POST', 'GET'])
def suavizacionExponencial():
    if request.method == 'POST':
        try:
            data = pronostico.suavizacionExponencial(
                request.form['x'],
                request.form['y'],
                request.form['xlbl'],
                request.form['ylbl'])

            return render_template('suavizacionExponencial.html',
                datos = data,
                cargar = True)
        except Exception as error:
            return render_template('suavizacionExponencial.html',
                error = error)

    elif request.method == 'GET':
        return render_template('suavizacionExponencial.html')

@app.route('/regresionLineal', methods=['POST', 'GET'])
def regresionLineal():
    if request.method == 'POST':
        try:
            data = pronostico.regresionLineal(
                request.form['x'],
                request.form['y'],
                request.form['xlbl'],
                request.form['ylbl'])

            return render_template('regresionLineal.html',
                imagen = data)
        except Exception as error:
            return render_template('regresionLineal.html',
                error = error)

    elif request.method == 'GET':
        return render_template('regresionLineal.html')

@app.route('/regresionCuadratica', methods=['POST', 'GET'])
def regresionCuadratica():
    if request.method == 'POST':
        try:
            data = pronostico.regresionLinealCuadratica(
                request.form['x'],
                request.form['y'],
                request.form['xlbl'],
                request.form['ylbl'])

            return render_template('regresionCuadratica.html',
                imagen = data)
        except Exception as error:
            return render_template('regresionCuadratica.html',
                error = error)

    elif request.method == 'GET':
        return render_template('regresionCuadratica.html')
    
    
    # jjdjd
        
@app.route('/sistemaMontecarlo')
def sistemaMontecarlo():
    return render_template('sistemaMontecarlo.html')

@app.route('/printSistemaMontecarlo')
def printSistemaMontecarlo():
    return render_template('printSistemaMontecarlo.html')

@app.route('/calcularMontecarlo', methods=['GET', 'POST'])
def calcularMontecarlo():
    tipoArch= request.form.get("tipoarchivo")
    n1 = request.form.get("numeroIteraciones", type=int)
    x01 = request.form.get("semilla", type=int)
    a1 = request.form.get("multiplicador", type=int)
    c1 = request.form.get("incremento", type=int)
    m1 = request.form.get("modulo", type=int)

    pago = request.form.get("x")
    probabilidad = request.form.get("y")

    file = request.files['file'].read()

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from pandas import ExcelWriter
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    import io
    from io import BytesIO
    import base64
    import itertools
    import pandas as pd


    if tipoArch=='1':
        
        file = pd.read_excel(file)
        
        
    elif tipoArch=='2':
        file = pd.read_csv(io.StringIO(file.decode('utf-8')))
        
    elif tipoArch=='3':
        file = pd.read_json(file)

    # file = pd.read_excel(file)
    # tot = pd.DataFrame(file)
    #x = a["X"]
    #tot = a["Y"]

    # datos = {
    # 'Pago' : [0,500,1000,2000,5000,8000,10000],
    # 'Probabilidad': [0.83,0.06,0.05,0.02,0.02,0.01,0.01]
    # }
    df = pd.DataFrame(file)
    # Array para guardar los resultados
    dataArray = []
    # Suma de probabilidad
    sumProbabilidad = np.cumsum(df[probabilidad])
    df['FDP'] = sumProbabilidad
    # Obtenemos los datos mínimos
    datosMin = df['FDP']+0.001
    # Obtenemos los datos máximos
    datosMax = df['FDP']
    # Asignamos al DataFrame
    df['Min'] = datosMin
    df['Max'] = datosMax
    # Se establecen correctamente los datos mínimos
    df['Min'] = df['Min'].shift(periods=1, fill_value=0)
    df
        # n = Cantidad de tenedores de pólizas
    n = n1
    m = m1 # 2**32
    a = a1
    x0 = x01
    c = c1
    # Obtenemos los resultados
    x = [1] * n
    r = [0.1] * n
    for i in range(0, n):
        x[i] = ((a*x0)+c) % m
        x0 = x[i]
        r[i] = x0 / m
    # llenamos el DataFrame
    d = {'ri': r }
    dfMCL = pd.DataFrame(data=d)
    dfMCL

    # Valores máximos
    max = df['Max'].values
    # Valores mínimos
    min = df['Min'].values
    # Definimos el número de pagos
    n = 32
    
    # df = pd.DataFrame(df)

    # data1 = dffx.to_html(classes="table table-hover table-striped", justify="justify-all", border=0)
    
    # Función de búsqueda
    def busqueda(arrmin, arrmax, valor):
        
        for i in range (len(arrmin)):
            if valor >= arrmin[i] and valor <= arrmax[i]:
                return i
    #print(i)
        return -1
    xpos = dfMCL['ri']
    posi = [0] * n
    #print (n)
    for j in range(n):
        val = xpos[j]
        pos = busqueda(min,max,val)
        posi[j] = pos
    # Definiendo un índice para simular datos
    ind = [
        1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,93,94,95,96,97,98,99,100,
        101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,
        201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,339,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,
        301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,
        401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,
        501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,
        601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,
        701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,
        801,802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,819,820,821,822,823,824,825,826,827,828,829,830,831,832,833,834,835,836,837,838,839,840,841,842,843,844,845,846,847,848,849,850,851,852,853,854,855,856,857,858,859,860,861,862,863,864,865,866,867,868,869,870,871,872,873,874,875,876,877,878,879,880,881,882,883,884,885,886,887,888,889,890,891,892,893,894,895,896,897,898,899,900,
        901,902,903,904,905,906,907,908,909,910,911,912,913,914,915,916,917,918,919,920,921,922,923,924,925,926,927,928,929,930,931,932,933,934,935,936,937,938,939,940,941,942,943,944,945,946,947,948,949,950,951,952,953,954,955,956,957,958,959,960,961,962,963,964,965,966,967,968,969,970,971,972,973,974,975,976,977,978,979,980,981,982,983,984,985,986,987,988,989,990,991,992,993,994,995,996,997,998,999,1000,
        1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,1012,1013
        ]
    df["Indice"] = ind
    # Ordenamos el DataFrame
    df = df[['Indice',pago,probabilidad,'FDP','Min','Max']]
    # Array para guardar los datos
    simula = []
    for j in range(n):
        for i in range(n):
            sim = df.loc[df["Indice"]== posi[i]+1 ]
            simu = sim.filter([pago]).values
            iterator = itertools.chain(*simu)
                    
            for item in iterator:
                a=item
            simula.append(round(a,2))
    # Insertamos en el DataFrame los datos de simulación
    dfMCL["Simulación"] = pd.DataFrame(simula)
    # Sumamos 39 ya que el precio de la acción actual es de 39
    dfMCL["Pagos a tenedor"] = dfMCL["Simulación"]
# Suma de Pagos a tenedor
    data = dfMCL['Pagos a tenedor'].sum()
    dataArray.append(data)

# Imprimir resultado
    print('Suma de los pagos al tenedor:', data)
    # dat = pd.DataFrame(data)
    # prin_='Suma de los pagos al tenedor: ',data
    # data01=data
    # data01=str(data01)
    # data3=dat.to_html(
    #     classes="col-md-6 mb-3", justify="justify-all")
    dfMCL

    

    buf = io.BytesIO()
    plt.plot(dfMCL['Simulación'], label='Simulación', color='purple')
    plt.plot(dfMCL['Pagos a tenedor'], label='Costo', color='green')
    plt.legend()

    fig = plt.gcf()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    fig.clear()
    plot_url = base64.b64encode(buf.getvalue()).decode('UTF-8')

    data1 = df.to_html(
        classes="dataTable table table-bordered table-hover", justify="justify-all", border=0)

    """ writer = ExcelWriter("static/file/data.xlsx")
    dfMCL.to_excel(writer, index=False)
    writer.save()

    dfMCL.to_csv("static/file/data.csv", index=False)
    """
    data2 = dfMCL.to_html(
        classes="dataTable table table-bordered table-hover", justify="justify-all", border=0)

    """ writer = ExcelWriter("static/file/data.xlsx")
    dfMCL.to_excel(writer, index=False)
    writer.save()

    dfMCL.to_csv("static/file/data.csv", index=False)
    """
    # data3 = data.to_html(
    #     classes="table table-hover table-striped", justify="justify-all", border=0)

    # """ writer = ExcelWriter("static/file/data.xlsx")
    # dfMCL.to_excel(writer, index=False)
    # writer.save()

    # dfMCL.to_csv("static/file/data.csv", index=False)
    # """
    return render_template('printSistemaMontecarlo.html', data=data1, data2=data2,data3=data, image=plot_url)
    # def busqueda(arrmin, arrmax, valor):


if __name__ == '__main__':
    app.run( host="0.0.0.0", port=5000,debug=True)
