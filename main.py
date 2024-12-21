#Bibliotecas 
import requests
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 

sns.set(
    style='darkgrid',
    context='notebook',
    rc={
        'axes.spines.top': False,
        'axes.spines.right': False
    }
)

#URLs escolhidas para análise: Food and Drug Administration (FDA)
urls = {
    "frequent_adverse_reactions": 'https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20241219]&count=patient.drug.activesubstance.activesubstancename.exact',
    "adverse_event_reporters": 'https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20241219]&count=primarysource.qualification',
    "reports_by_country": 'https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20241219]&count=primarysource.reportercountry.exact',
    "recieve_date": 'https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20241220]&count=receivedate',
    "drug_dosage_forms": 'https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20241219]&count=patient.drug.drugdosageform.exact',
}

#Função para extração dos dados da API que realiza uma requisição GET e retorna o JSON, inclui também tratamento de erros
def extracao(url): 
    try: 
        requisicao = requests.get(url, timeout=60)
        requisicao.raise_for_status()
        return requisicao.json()
    except requests.exceptions.RequestException as erro: 
        print(f"Erro ao acessar {url}", {erro})

# Função que itera sobre o dicionário de urls chamando a função extração e retorna a coluna de results da API como um dataframe pandas
def dataframe():
    dados = {}
    print('Realizando requisição')
    for nome, url in urls.items():
        print('...')
        try: 
            arquivo_json = extracao(url)
            if 'results' in arquivo_json and arquivo_json['results']: 
                df = pd.DataFrame(arquivo_json['results'])
                dados[nome] = df
            else: 
                print(f"Erro para a URL: {url}")
        except Exception as erro: 
            print(f"Erro para a url {url} {erro}")
            
    print("Requisições sem erro")
    return dados

#Função para gerar um gráfico de barra
def barra(df, title, eixoX, eixoY, legenda): 
    df = df.head(20)
    plt.figure(figsize=(15,10))
    grafico_barra = sns.barplot(y='count',data=df, hue='term', palette='deep')
    grafico_barra.set_xlabel(eixoX, fontsize=12, fontweight='bold')
    grafico_barra.set_ylabel(eixoY, fontsize=12, fontweight='bold')
    plt.legend(title=legenda, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title, fontsize=12, fontweight='bold')
    plt.show()

#Função para gerar gráfico de setores
def gerar_setores(df, title): 
    plt.pie(df['count'], labels=df['term'])
    plt.title(title, fontsize=12, fontweight='bold')
    plt.show()

#Função para gerar um gráfico de dispersão 
def gerar_scatter(df): 
    plt.figure(figsize=(15,10))
    scatter_plot = sns.scatterplot(data=df, x='time', y='count', color='red', alpha=0.2)
    scatter_plot.set_xlabel('Ano')
    scatter_plot.set_ylabel('Contagem')
    plt.title('Contagem de reportes de reações adversas ao longo dos anos', fontsize=12, fontweight='bold')
    plt.show()

#Função principal 
def main(): 
    #Gerando DataFrames dos dados da API e os armazenando em um dicionário
    dados_api = dataframe()

    #Itera sobre o dicionário de dataframe e cria uma variável global para acesso 
    for nome, df in dados_api.items():
        if df is not None:
            globals()[f"df_{nome}"] = df
            print(f"Variável df_{nome} criada.")
        else: 
            print(f"Erro ao criar o DatFrame {nome}.")

    #Gerando gráfico de barras para medicamentos que apresentam efeitos coletarais mais frequentemente
    barra(df_frequent_adverse_reactions, 'Medicamentos que apresentam efeitos coleterais mais frequentemente', '', 'Contagem', 'Medicamento')

    #Transformaçao da coluna term do DataFrame adverse_event_reporters para string 
    df_adverse_event_reporters['term'] = df_adverse_event_reporters['term'].astype(str)

    #Conversão do nome das colunas term do DataFrame adverse_event_reporters
    df_adverse_event_reporters['term'] = df_adverse_event_reporters['term'].map({
        "5": "Consumer or non-health professional",
        "1": "Physician",
        "3": "Other health professional",
        "2": "Pharmacist",
        "4": "Lawyer"
    })

    #Gerando gráfico de setores de quem reporta condições adversas
    gerar_setores(df_adverse_event_reporters, 'Quem reporta condições adversas')

    #Gerando gráfico de barras para reporte de condições adversas por países
    barra(df_reports_by_country, 'Reporte de condiçoes adversas por países', '', 'Contagem', 'País')

    #Convertendo a coluna time do DataFrame recieve_date para o formato datetime 
    df_recieve_date['time'] = pd.to_datetime(df_recieve_date['time']) 

    #Gerando gráfico de dispersão para contagem de reportes de reações adversas ao longo dos anos
    gerar_scatter(df_recieve_date) 

    #Gerando um gráfico de barra para formas de dosagem que mais apresentam condições adversas
    barra(df_drug_dosage_forms, 'Formas de dosagem que mais apresentam condições adversas', '', 'Contagem', 'Forma de dosagem')

if __name__ == "__main__": 
    main()