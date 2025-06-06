# Importa a biblioteca mysql.connector para conexão com banco de dados MySQL
import mysql.connector
# Importa a biblioteca os para acessar variáveis de ambiente do sistema
import os
# Importa a função load_dotenv para carregar variáveis de um arquivo .env
from dotenv import load_dotenv

# Define função para estabelecer conexão inicial com o banco de dados
def conecta_banco():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Estabelece conexão com o banco MySQL usando as credenciais das variáveis de ambiente
    conexao = mysql.connector.connect (
        host = os.getenv("HOST_ENV"),        # Obtém o endereço do servidor do banco
        user = os.getenv("USER_ENV"),        # Obtém o nome de usuário para conexão
        port = os.getenv("PORT_ENV"),        # Obtém a porta de conexão
        password = os.getenv("PASSWORD_ENV"), # Obtém a senha de acesso
        database = os.getenv("DATABASE_ENV")  # Obtém o nome do banco de dados
    )

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()
    # Retorna tanto o cursor quanto a conexão para uso posterior
    return cursor, conexao

# Define função para executar comandos SQL e retornar resultados como lista de dicionários
def executa_DICT(command): # conseguiu pegar => elemento do banco
    # Obtém cursor e conexão chamando a função conecta_banco()
    cursor, conexao = conecta_banco()

    # Executa o comando SQL passado como parâmetro
    cursor.execute(command)
    # Extrai os nomes das colunas do resultado da consulta
    columns = [col[0] for col in cursor.description]
    # Converte cada linha do resultado em um dicionário, usando os nomes das colunas como chaves
    resultado = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # Fecha o cursor para liberar recursos
    cursor.close()
    # Fecha a conexão com o banco
    conexao.close()

    # Retorna a lista de dicionários com os resultados
    return resultado

# Define função para executar comandos SQL e retornar apenas o primeiro resultado como dicionário
def executa_DICT_ONE(command): # conseguiu pegar => elemento do banco
    # Obtém cursor e conexão chamando a função conecta_banco()
    cursor, conexao = conecta_banco()

    # Executa o comando SQL passado como parâmetro
    cursor.execute(command)
    # Extrai os nomes das colunas do resultado da consulta
    columns = [col[0] for col in cursor.description]
    # Converte a primeira linha do resultado em um dicionário
    resultado = dict(zip(columns, cursor.fetchone()))
    # Fecha o cursor para liberar recursos
    cursor.close()
    # Fecha a conexão com o banco
    conexao.close()

    # Retorna o dicionário com o primeiro resultado
    return resultado

# Define função para executar comandos SQL e retornar resultados como tuplas
def executa_GET(command): # conseguiu pegar => elemento do banco
    # Obtém cursor e conexão chamando a função conecta_banco()
    cursor, conexao = conecta_banco()

    # Executa o comando SQL passado como parâmetro
    cursor.execute(command)
    # Obtém todos os resultados da consulta como lista de tuplas
    resultado = cursor.fetchall()
    # Fecha o cursor para liberar recursos
    cursor.close()
    # Fecha a conexão com o banco
    conexao.close()

    # Retorna a lista de tuplas com os resultados
    return resultado

# Define função para executar comandos SQL e retornar apenas o primeiro valor da primeira linha
def executa_GET_BY_ID(command): # conseguiu pegar => elemento do banco
    # Obtém cursor e conexão chamando a função conecta_banco()
    cursor, conexao = conecta_banco()

    # Executa o comando SQL passado como parâmetro
    cursor.execute(command)
    # Obtém apenas o primeiro valor da primeira linha do resultado
    resultado = cursor.fetchone()[0]
    # Fecha o cursor para liberar recursos
    cursor.close()
    # Fecha a conexão com o banco
    conexao.close()

    # Retorna o valor único encontrado
    return resultado

# Define função para executar comandos SQL que modificam dados (INSERT, UPDATE, DELETE)
def executa_DEFAULT(command): # conseguiu alterar => 'sucesso'
    # Obtém cursor e conexão chamando a função conecta_banco()
    cursor, conexao = conecta_banco()

    # Executa o comando SQL passado como parâmetro
    cursor.execute(command)
    # Confirma as alterações no banco de dados (commit)
    conexao.commit()
    # Fecha o cursor para liberar recursos
    cursor.close()
    # Fecha a conexão com o banco
    conexao.close()

    # Retorna string indicando sucesso na operação
    return "sucesso"

########## FUNÇÃO PRINCIPAL (CHAMA AS FUNÇÕES ESPECIFICAS) ##########

# Define função principal que direciona para a função apropriada baseada no método
def executar_comando(method, command):        
    # Usa match-case para determinar qual função executar baseada no método
    match method:
        # Para métodos que modificam dados, usa a função padrão
        case "POST" | "PUT" | "DELETE":
            return executa_DEFAULT(command)
        
        # Para consultas simples, retorna tuplas
        case "GET":
            return executa_GET(command)
        
        # Para busca por ID específico, retorna valor único
        case "GET_BY_ID":
            return executa_GET_BY_ID(command)

        # Para consultas que retornam múltiplos registros como dicionários
        case "GET_DICT":
            return executa_DICT(command)

        # Para consultas que retornam um único registro como dicionário
        case "GET_DICT_ONE":
            return executa_DICT_ONE(command)
        
        # Caso padrão para métodos não reconhecidos
        case _:
            return "MÉTODO INVÁLIDO"



# print(f"Host: {host}")
# print(f"User: {user}")
# print(f"Port: {port}")
# print(f"Database: {database}")
