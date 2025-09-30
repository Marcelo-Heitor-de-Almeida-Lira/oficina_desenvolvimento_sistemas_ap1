# oficina_desenvolvimento_sistemas_ap1
Desenvolvimento de um sistema de recomendação de livros

## Integrantes da equipe
* Luiz Daniel Raposo Nunes de Mello - 1715310049
* Marcelo Heitor de Almeida Lira - 2315310043
* Murillo de Lima Acácio - 1915310018

### Dataset utilizado:
* https://github.com/zygmuntz/goodbooks-10k/tree/master/samples

### 🎯 Objetivo do Sistema
O objetivo principal deste sistema é ajudar os usuários a descobrirem livros que se alinhem com seus gostos literários. Para isso, a plataforma oferece as seguintes funcionalidades:
* __Catálogo Interativo__: Visualização do acervo de livros com opções de busca.
* __Sistema de Avaliação__: Ferramenta para que os usuários possam atribuir notas (de 1 a 5 estrelas) aos livros que já leram, criando um perfil de gosto pessoal.
* __Recomendações Personalizadas__: Geração de uma lista de livros recomendados com base nas avaliações fornecidas pelo usuário e por outros usuários com gostos similares.
* __Análise de Performance__: Exibição de métricas de acurácia que demonstram a eficácia do algoritmo de recomendação.

### 🚀 Como Executar o Projeto
O projeto é dividido em duas partes principais: o __backend__ (a API que serve os dados e a lógica) e o __frontend__ (a interface web com a qual o usuário interage). Ambos precisam estar rodando simultaneamente.
__Pré-requisitos__:
* Python 3.9+
* Gerenciador de pacotes __pip__

1. __Download das imagens__.

Como o GitHub não suporta tamanhos grandes de pastas e arquivos, as imagens das capas dos livros foram compactadas para o arquivo ‘book_covers.zip’, localizado na pasta ‘frontend/’. Para que o sistema funcione corretamente, extraia os arquivos e salve-os em uma pasta de mesmo nome, no mesmo diretório.

2. __Configuração e execução do Backend__.

O backend é responsável por toda a lógica de negócio, acesso aos dados e o cálculo das recomendações.
Bash
```
# 1. Navegue até a pasta do backend
cd backend/

# 2. Crie e ative um ambiente virtual
# No macOS/Linux
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
.\venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor da API (exemplo com Uvicorn/FastAPI)
uvicorn main:app --reload
```

3. __Configuração e execução do Frontend__.

Após executar o último comando, o terminal indicará que o servidor está rodando, geralmente em http://127.0.0.1:8000. Mantenha este terminal aberto.
O frontend é a interface web construída com Streamlit.

Bash
```
# 1. Abra um NOVO terminal e navegue até a pasta do frontend
cd frontend/

# 2. Crie e ative um ambiente virtual (separado do backend)
# No macOS/Linux
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
.\venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie a aplicação Streamlit
streamlit run app.py
```

Seu navegador abrirá automaticamente com a aplicação web. Se não abrir, acesse o endereço http://localhost:8501informado no terminal.


### 🧠 Lógica de Recomendação

O sistema utiliza a técnica de __Filtro Colaborativo User-Based (baseado no usuário)__. A intuição por trás desse método é que, se duas pessoas gostaram dos mesmos livros no passado, elas provavelmente gostarão dos mesmos livros no futuro.
O processo ocorre em 4 etapas:

1. __Criação da Matriz de Utilidade__: Uma grande tabela é montada onde as linhas representam os usuários e as colunas representam os livros. O valor de cada célula é a nota que um usuário deu a um livro.
2. __Cálculo de Similaridade__: O sistema calcula o quão "parecido" é o gosto de cada usuário em relação a todos os outros. Para isso, usamos a métrica de Similaridade de Cossenos.
3. __Previsão de Notas__: Para um livro que o usuário ainda não leu, o sistema prevê qual nota ele provavelmente daria. Essa previsão é uma média das notas que os usuários mais similares deram para aquele livro, ponderada pelo nível de similaridade.
4. __Geração das Recomendações__: Os livros com as maiores notas previstas (e que o usuário ainda não leu) são selecionados e exibidos como recomendação.


### 📏 Justificativa da Métrica de Similaridade (Similaridade de Cossenos)
A __Similaridade de Cossenos__ foi escolhida para medir o quão parecidos são os gostos dos usuários. Nesta abordagem, o histórico de avaliações de cada usuário é tratado como um vetor em um espaço multidimensional. A métrica calcula o cosseno do ângulo entre esses vetores.
Vantagens desta abordagem:
* __Eficaz em Dados Esparsos__: A maioria dos usuários avalia apenas uma pequena fração dos livros disponíveis. A similaridade de cossenos lida bem com essa "esparsidade", pois foca nos livros que os usuários avaliaram em comum.
* __Foco na Direção do Gosto__: A métrica não se preocupa com a magnitude absoluta das notas (se um usuário tende a dar notas mais altas que outro), mas sim com a orientação do gosto (se ambos gostam e desgostam dos mesmos tipos de livros).
* __Padrão de Mercado__: É uma técnica robusta, amplamente utilizada e compreendida em sistemas de recomendação, servindo como um excelente ponto de partida.

### 📊 Cálculo e Análise da Acurácia
Foi desenvolvido um programa específico para medir a acurácia do sistema de recomendação.

O cálculo utilizado segue a fórmula:

Acurácia = número de acertos / número de itens recomendados
Esse programa divide os dados de cada usuário em duas partes (uma para gerar recomendações e outra para verificar se foram corretas), gera as recomendações com base apenas na primeira parte e compara com a segunda parte, aplicando a fórmula acima.
Após executar o programa, obtivemos os seguintes resultados:
* __Total de acertos__: 1.057.110
* __Total de recomendações__: 6.210.007

Aplicando a fórmula:
Acurácia = 1.057.110 / 6.210.007 = 0,1702 (17,02%)
Isso significa que, do total de recomendações feitas pelo sistema, aproximadamente 17% coincidiram com itens que os usuários realmente gostaram (definidos pelo conjunto de teste). Em outras palavras, cerca de 1 a cada 6 recomendações foi um acerto de acordo com a métrica utilizada.
