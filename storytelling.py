import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 

sns.set(
    style='darkgrid',
    context='notebook',
    rc={
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.facecolor' : '#0e1117', 
        'axes.edgecolor' : 'white',
        'axes.labelcolor': 'white',
        'xtick.color' : 'white',
        'ytick.color' : 'white',
        'grid.color': 'white',
    }
)

#Criando a sidebar
st.sidebar.title('Menu')
aba_selecionada = st.sidebar.radio("Escolha uma aba", ['Projeto','Análises'])

#URLs da API 
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

#Gerando DataFrames dos dados da API e os armazenando em um dicionário
dados_api = dataframe()

#Itera sbre o dicionário de dataframe e cria uma variável global para acesso 
for nome, df in dados_api.items():
    if df is not None:
        globals()[f"df_{nome}"] = df
        print(f"Variável df_{nome} criada.")
    else: 
        print(f"Erro ao criar o DatFrame {nome}.")

#Função para gerar um gráfico de barra
def barra(df, title, eixoX, eixoY, legenda): 
    df = df.head(20)
    plt.figure(figsize=(15,15))
    grafico_barra = sns.barplot(y='count',data=df, hue='term', palette='deep')
    grafico_barra.set_xlabel(eixoX, fontsize=12, fontweight='bold')
    grafico_barra.set_ylabel(eixoY, fontsize=12, fontweight='bold')
    plt.legend(title=legenda, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title, fontsize=12, fontweight='bold', color='white')
    st.pyplot(plt)


#Função para gerar gráfico de setores
def gerar_setores(df, title):
    plt.figure(figsize=(15,15)) 
    plt.pie(df['count'], labels=df['term'], textprops={'color': 'white'})
    plt.title(title, fontsize=12, fontweight='bold', color='white')
    st.pyplot(plt)

#Função para gerar um gráfico de dispersão 
def gerar_scatter(df): 
    plt.figure(figsize=(15,10))
    scatter_plot = sns.scatterplot(data=df, x='time', y='count', color='red', alpha=0.2)
    scatter_plot.set_xlabel('Ano')
    scatter_plot.set_ylabel('Contagem')
    plt.title('Contagem de reportes de reações adversas ao longo dos anos', fontsize=12, fontweight='bold', color='white')
    st.pyplot(plt)
    
#Função principal da aba projeto
def projeto(): 
    st.title('Extraindo e Analisando Dados com a API da FDA') #Título principal
    st.header('Objetivos') #Subtítulo (parte dos objetivos)
    st.markdown('- Escolher uma API para extração de dados') #Tópicos objetivos 
    st.markdown('- Formatar os dados da API de forma tabular utilizando Pandas') #Tópicos objetivos
    st.markdown('- Criar gráficos, análises, tabelas, sobre os dados extraídos, utilizando bibliotecas python') #Tópicos objetivos
    st.header('API escolhida') #Subtítulo
    #Texto sobre API escolhida
    st.write('A consulta é estruturada com a URL base da API e parâmetros específicos, como a busca, número de registros e limite, essa consulta tem a forma:')
    #Trecho em bloco de código sobre API
    requisicao = 'https://api.fda.gov/drug/label.json(endpoint base)?search=campo:termo&limit=5(limite).'
    st.code(requisicao, language='python')
    st.header('Categorias Escolhidas') #Subtítulo sobre categorias da API
    #Tópicos com texto sobre as categorias escolhidas da API
    st.markdown('- What adverse reactions are frequently reported: Essa categoria me permite explorar quais medicamentos apresentam as condições adversas mais frequentemente registradas, o que pode fornecer insights sobre quais medicamentos ou substâncias estão associadas a efeitos colaterais comuns')
    st.markdown('- Who reports adverse events: Com essa informação é possível identificar quais fontes estão mais frequentemente relatando os eventos adversos, permitindo uma possível correlação')
    st.markdown('- Adverse drug event reports by Country: Essa categoria permite a análise geográfica nas condições adversas em medicamentos')
    st.markdown('- Date that the report was first received by FDA: Essa categoria permite avaliar padrões de reporte ao longo do tempo e compreender mudanças e tendências')
    st.markdown('- The drug’s dosage form: Essa informação pode ser útil para correlacionar a forma de administração com o tipo de reação adversa')
    st.header('Dificuldades encontradas') #Subtítulo (parte das dificuldades encontradas)
    #Tópico sobre erros 
    #Texto em tópico do primeiro erro
    st.markdown('- Durante a etapa inicial do código que faz as requisições das urls, inicialmente fiz a leitura individual de cada URL. No entanto, percebi que o código não estava otimizado, então reescrevi com outra abordagem. Após isso, encontrei dificuldades ao tentar acessar cada DataFrame individualmente, o que me levou a pesquisar sobre variáveis globais e como criá-las a partir de um dicionário. Meu pensamento para essa etapa foi de criar um dicionário contendo todas as urls , em seguida, desenvolver uma função responsável pela leitura dos dados com tratamento de erros. Após isso, implementei uma função para iterar pelas URls e transformar os dados em DataFrames. Por fim, após a dificuldade de acessar cada dataframe de forma individual e global criei uma função para iterar no dicionário de dataframes e criar uma variável para cada dataframe. O principal motivo que me levou a adotar essa abordagem foi que, caso novas URLs sejam adicionadas, o processo se torna mais simples e eficiente, o código dessa parte ficou dessa forma: ')
    #Trecho de código do primeiro erro
    codigo_primeiro_erro = """
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
    for nome, url in urls.items():
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

#Gerando DataFrames dos dados da API e os armazenando em um dicionário
dados_api = dataframe()

#Itera sobre o dicionário de dataframe e cria uma variável global para acesso 
for nome, df in dados_api.items():
    if df is not None:
        globals()[f"df_{nome}"] = df
        print(f"Variável df_{nome} criada.")
    else: 
        print(f"Erro ao criar o DatFrame {nome}.")   
    """
    #Trecho em bloco de código sobre o primeiro erro
    st.code(codigo_primeiro_erro)
    #Texto em tópico do segundo erro
    st.markdown('- O segundo erro que encontrei foi durante a criação do gráfico de setores, enfrentei dificuldades para renomear os valores da coluna que vieram codificados, provavelmente utilizando algum tipo de Enconder, com números de 1 a 5. Inicialmente, tentei usar o método rename da biblioteca Pandas, mas não tive sucesso. Em seguida, alterei o tipo dos dados para str mas não resolveu o problema. Após consultar a documentação do Pandas, descobri o metódo map, que finalmente mudou os valores da coluna, o código dessa parte ficou dessa forma:')
    #Trecho de código do segundo erro
    codigo_segundo_erro = """
#Transformaçao da coluna term para string 
df_adverse_event_reporters['term'] = df_adverse_event_reporters['term'].astype(str)

#Conversão do nome das colunas term
df_adverse_event_reporters['term'] = df_adverse_event_reporters['term'].map({
    "5": "Consumer or non-health professional",
    "1": "Physician",
    "3": "Other health professional",
    "2": "Pharmacist",
    "4": "Lawyer"
})
"""
    #Trecho em bloco de código sobre o segundo erro
    st.code(codigo_segundo_erro)
    #Texto em tópico do terceiro erro
    st.markdown('- O terceiro erro que encontrei foi ao gerar o arquivo .py, encontrei dificuldades para definir os títulos de cada gráfico. Para contornar isso, adicionei um parâmetro chamado title em todas funções de criação de gráficos. Dessa forma, cada chamada de função passou a receber seu título específico. Além disso, percebi que havia esquecido de definir as legendas e nomes dos eixos individualmente, o que só notei quando executei o arquivo .py. Para corrigir isso, adicionei parâmetros adicionais, um para a legenda e outros para os rótulos dos eixos, para ilustrar vou pegar o código da função de geração de gráficos de barra, que tem a forma:')
    #Trecho de código do terceiro erro
    codigo_terceiro_erro = """
#Função para gerar um gráfico de barra
def barra(df, title, eixoX, eixoY, legenda): 
    df = df.head(20)
    plt.figure(figsize=(15,10))
    grafico_barra = sns.barplot(y='count',data=df, hue='term', palette='deep')
    grafico_barra.set_xlabel(eixoX, fontsize=12, fontweight='bold')
    grafico_barra.set_ylabel(eixoY, fontsize=12, fontweight='bold')
    plt.legend(title=legenda, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title, fontsize=12, fontweight='bold')
"""
    #Trecho em bloco de código sobre o terceiro erro
    st.code(codigo_terceiro_erro)
    #Texto em tópico do quarto erro
    st.markdown('- O quarto erro que encontrei foi ao criar o dashboard e inserir os gráficos do matplotlib, percebi que o contraste estava atrapalhando a visualização dos dados. Para resolver isso, alterei os parâmetros do rc do Seaborn com o código HEX das cores do streamlit, para isso consultei a documentação do seaborn. Além disso tive uma dificuldade específica ao tentar modificar o texto do gráfico de setores, após pesquisar, encontrei a solução utilizando o textprops. O código dessa parte ficou dessa forma:')
    #Trecho de código da primeira parte do quarto erro
    codigo_quarto_erro1 = """
sns.set(
    style='darkgrid',
    context='notebook',
    rc={
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.facecolor' : '#0e1117', 
        'axes.edgecolor' : 'white',
        'axes.labelcolor': 'white',
        'xtick.color' : 'white',
        'ytick.color' : 'white',
        'grid.color': 'white',
    }
)
"""
    #Trecho em bloco de código sobre a primeira parte do quarto erro
    st.code(codigo_quarto_erro1)
    #Trecho de código da segunda parte do quarto erro
    codigo_quarto_erro2 = """
    plt.pie(df['count'], labels=df['term'], textprops={'color': 'white'})
    """ 
    #Trecho em bloco de código da segunda parte do quarto erro
    st.code(codigo_quarto_erro2)

    st.header('Sobre o projeto e etapas') #Subtítulo (parte do projeto e etapas)
    #Tópicos do projeto e etapas
    st.markdown('- Extração dos dados da API pública da FDA') 
    st.markdown('- Tratamento de erros e boas práticas de programação')
    st.markdown('- Conversão dos dados para formato tabular em Pandas')
    st.markdown('- Tratamento e manipulações com os DataFrames')
    st.markdown('- Criação de diversos gráficos como em barra, dispersão e setores')
    st.markdown('- Análise dos gráficos e dados obtidos')
    st.subheader('Para as análises dos dados e gráficos selecione a aba Análises' )

#Função para os gerar os gráficos no dashboard, a única diferença das funções dos arquivos .py e .ipynb é o ajuste do tamanho da figura e a substituição do plt.show por st.pyplot()
def analises(): 
    st.title('Análises dos dados da API') #Título principal
    st.header('Medicamentos que apresentam efeitos colaterais comuns mais frequentemente') #Subtítulo primeira parte da análise
    #Gerando gráfico de barras para medicamentos que apresentam efeitos coletarais mais frequentemente
    barra(df_frequent_adverse_reactions, 'Medicamentos que apresentam efeitos coleterais mais frequentemente', '', 'Contagem', 'Medicamento') 
    #Texto com análise
    st.markdown(' - É possivel observar que alguns medicamentos, como Adalimumab, Aspirin e Acetiminophen, tem a sua frequência alta, indicando que esses medicamentos estão frequentemente associados a reações adversas reportadas. Essa alta frequência pode indicar que esses medicamentos são mais receitados que outros, ou que, de fato os mesmos realmente tem maior probabilidade de causar reações adversas')
    st.write('-----------------------------------------')#Quebra de liinha
    st.header('Quem reporta as condições adversas a FDA')#Subtítulo com a segunda parte da análise
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
    #Texto com análise
    st.markdown('- O gráfico revela que a maioria dos eventos adversos é reportada por consumidores ou profissionais fora da área da saúde. Médicos ocupam o segundo lugar, como esperado, dado seu contato direto com os pacientes. Já a categoria "Lawyer" chama atenção, pois sugere que questões legais relacionadas a reações adversas são mais frequentes do que se poderia prever, indicando a correlação jurídica com reações adversas de medicamentos')
    st.write('-----------------------------------------')#Quebra de liinha
    st.header('Reporte de condições adversas por países')#Subtítulo com a terceira parte da análise
    #Gerando gráfico de barras para reporte de condições adversas por países
    barra(df_reports_by_country, 'Reporte de condiçoes adversas por países', '', 'Contagem', 'País')
    #Texto com análise
    st.markdown('- É evidente que os Estados Unidos possuem o maior número de relatos de reações adversas de forma esmagadora, o que pode indicar tanto uma coleta de dados mais eficiente quanto uma maior indiência de reações adversas. Além disso, o fato dos Estados Unidos serem uma potência pode levar a maior acesso a medicamentos pela população e consequentemente um aumento nas reações adversas reportadas')
    st.write('-----------------------------------------')#Quebra de linha 
    st.header('Contagem de reportes de reações adversas ao longo dos anos')#Subtítulo com a quarta parte da análise
    #Convertendo a coluna time do DataFrame recieve_date para o formato datetime 
    df_recieve_date['time'] = pd.to_datetime(df_recieve_date['time']) 
    #Gerando gráfico de dispersão para contagem de reportes de reações adversas ao longo dos anos
    gerar_scatter(df_recieve_date) 
    #Texto com análise
    st.markdown('- Observa-se que os relatos aumentaram de forma contínua desde 2004, alcançando seu pico em 2020, e depois começaram a diminuir. Essa comportamente provavelmente está relacionado à pandemia de COVID-19, que gerou um maior monitoramento e atenção aos efeitos adversos de medicamentos e vacinas')
    st.write('-----------------------------------------')#Quebra de linha
    st.header('Formas de dosagem que mais apresentam condições adversas')#Subtítulo com a quinta parte da análise
    #Gerando um gráfico de barra para formas de dosagem que mais apresentam condições adversas
    barra(df_drug_dosage_forms, 'Formas de dosagem que mais apresentam condições adversas', '', 'Contagem', 'Forma de dosagem')
    #Texto com análise
    st.markdown('- O gráfico mostra que medicamentos na forma de tablet dominam o número de reportes de reações adversas, essa predominância pode ser explicada pela maior popularidade dos medicamentos em formato de comprimido que são mais comumente receitados ou também pode indicar que esses medicamentos apresentam mais condições adversas. Vale ressaltar que, embora os tablets sejam mais populares, o número de reações adversas pode indicar uma maior propensão desses medicamentos a reações adversas')

#Se a aba selecionada for a do projeto executa a função projeto
if aba_selecionada == 'Projeto':
    projeto()

#Se a aba selecionada for a de análises executa a função analises()
if aba_selecionada == 'Análises': 
    analises()