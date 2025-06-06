from flask import Blueprint, request, jsonify, render_template, make_response
from ..db.database import executar_comando
from ..db.report import save_report, get_week_report, get_global_data, update_report, get_day_report, delete_single_report
from ..algorithms.normalizacao import Statistics
from ..algorithms.cryptography import Crypt
from ..algorithms.report_builder import DailyReportBuilder
from ..algorithms.graph_generator import radar_graph, bar_graph, polyline_graph, sector_graph
from datetime import date, datetime,timedelta
import json
import smtplib
from email.message import EmailMessage
import secrets
import string
from .notificacoes import notificar_consumo_bruto, notificar_variacao_isp, apagar_notificacoes_por_usuario_e_data,atualizar_notificacoes_por_relatorio

user_routes = Blueprint('users', __name__)

#função que verifica se o usuário existe no banco pelo ID (e se existe, está autenticado)
def is_authenticated(user_id):
    
    comando = f'SELECT EXISTS(SELECT 1 FROM usuarios WHERE ID = {user_id})'

    #Retorna se existe usuário no banco com as características enviadas
    retorno = executar_comando("GET", comando)

    if retorno == [(1,)]:
        return True
    else:
        return False

#---------------------------------------------------------------------------------------------------------------

#Enviar email com gmail:
def enviar_email(email, token):
    corpo_email = f'''
    <h1>[PROJETO INTEGRADOR 1]:</h1><br>
    <hr>
    <b>Acesso o link abaixo e utilize este token para resetar sua senha!<b/><br>
    <a href="http://localhost:5000/users/novaSenha">Link para recuperar sua senha</a>
    <h3>Token: {token}<h3/> 
    <hr>
    <i>Projeto Integrador 1 - PUC Campinas<i/>
    '''

    msg = EmailMessage()
    msg['Subject'] = "Token para resetar senha - PI 1"
    msg['From'] = 'estudos.flask@gmail.com'
    msg['To'] = email
    msg['X-Priority'] = '1'
    
    password = 'oxixdpspqzdfiuip'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    #Login com as credenciais:
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print(f'Email enviado para: {email}')

    return 'sucesso'

#------------------------------------------------------------------------------------------------------------------------

# Serviço para exibir o formulário de LOGIN na plataforma
@user_routes.route('/logar_user', methods=['GET'])
def exibe_form_login():
    return render_template('login.html')

# Serviço para exibir o formulário de CADASTRO na plataforma
@user_routes.route('/registerForm', methods=['GET'])
def exibe_form_cadastro():
    return render_template('cadastro.html')

@user_routes.route('/endRegister', methods=['GET'])
def exibe_form_cadastro_concluido():
    return render_template('cadastro_concluido.html')

#Serviço para exibir o formulário de DASHBORD
@user_routes.route('/dashboardForm', methods=['GET'])
def exibe_form_dashboard():
    return render_template('dashboard.html')

@user_routes.route('/sobre_nos', methods=['GET'])
def exibe_sobre_nos():
    return render_template('sobrenos.html')

@user_routes.route('/recuperarSenha', methods=['GET'])
def exibe_recuperar_senha():
    return render_template('recuperar_senha.html')


@user_routes.route('/novaSenha', methods=['GET'])
def exibe_form_nova_senha():
    return render_template('nova_senha.html')

#-----------------------------------------------------------------------------------------------------------------------------------------
# "/editarConsumos?date=2025-04-22" exemplo de link com argumentos
@user_routes.route('/editarConsumos', methods=['GET'])
def exibe_form_editarConsumo():
    rep = {}
    r_date = request.args.get('date')
    user_id = request.cookies.get('user_id')

    if(r_date):
        try:
            date.fromisoformat(r_date)
        except ValueError:
            r_date = date.today()
    
        try:
            rep = get_day_report(r_date, user_id)
        except Exception as e:
            return jsonify({"erro": f"Erro ao obter os dados: {str(e)}"}), 500

    return render_template('editardados.html', rep=rep, date=r_date)

#---------------------------------------------------------------------------------------------------------------

# Serviço para o CADASTRO do usuário na plataforma
@user_routes.route('/cadastrarUsuario', methods=['POST']) # receber em JxSON pq nao eh "visivel"
def register_user():
    data = request.json

    nome = data.get('nome')
    cpf = data.get('cpf')
    data_nascimento = data.get('data_nascimento')
    email = data.get('email')
    senha = data.get('senha')
    enc_pass = Crypt().encrypt(senha)

    comando = f'SELECT EXISTS(SELECT * FROM usuarios WHERE email = "{email}")'
    retorno = executar_comando("GET_BY_ID", comando)

    if retorno > 0:
        return {"Erro": 'Já existe um usuário com este e-mail.'}, 500
    
    else:        
        #INSERINDO usuario no banco
        comando = f'INSERT INTO usuarios (nome, cpf, data_nascimento, email, senha ) VALUES("{nome}", "{cpf}", "{data_nascimento}", "{email}", "{enc_pass}")'
        retorno = executar_comando("POST", comando)

        #Gera token novo
        chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        token_novo = ''.join(secrets.choice(chars) for _ in range(5))

        ###Reseta tempo limite para +infinito dnv
        insere_usuario_reset_pass = f'INSERT INTO reset_password (email_usuario, token_atual, tempo_limite) VALUES ("{email}","{token_novo}","2030-04-20 18:00:00")'
        executar_comando("POST", insere_usuario_reset_pass)
        
        if retorno == 'sucesso':
            return {"Status": 'sucesso'}, 201 # padronizar retornos em JSON - tudo que nao é visivel será via JSON (req e res)
        else:
            return {"Status": 'erro'}, 500
        
#---------------------------------------------------------------------------------------------------------------------------------------------------------

# Serviço para executar o LOGIN na plataforma
@user_routes.route('/login', methods=['POST'])
def login_user():

    data = request.json

    email = data.get('email')
    senha = data.get('senha')
    
    comando = f'SELECT ID, Senha FROM usuarios WHERE Email = "{email}" LIMIT 1'
    
    #retorna o USUÁRIO se encontrou email igual:
    retorno = executar_comando("GET", comando)
    
    if retorno:
        compare = Crypt().decrypt(retorno[0][1])
        if compare != senha:
            return {"Status": 'erro ao executar login'}, 400

        response = make_response()
        response.set_cookie('user_id', f"{retorno[0][0]}")
        return response, 201
    else:
        return {"Status": 'erro ao executar login'}, 400
#------------------------------------------------------------------------------------------------------------------

# Rota para cadastrar o consumo de um usuário:
@user_routes.route('/cadastrarConsumo', methods=['POST'])
def cadastrar():
    dados = request.json  # Obtém os dados enviados pelo cliente

    dados['user_id'] = request.cookies.get('user_id')  # Obtém o ID do usuário a partir dos cookies

    # Campos obrigatórios para o cadastro de consumo
    campos_obrigatorios = ['agua', 'energia', 'residuos_nao_reciclaveis', 'residuos_reciclaveis', 'transportes', 'user_id']
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({"erro": "Campos obrigatórios: agua, energia, residuos (reciclaveis e não-reciclaveis), transporte e user_id"}), 400
    
    # Verifica se o usuário está autenticado
    if not is_authenticated(dados['user_id']):
        return {'Erro': 'Usuário não autenticado!'}, 404
    
    if dados.get('date', None) is None:
        dados['date'] = date.today()

    # Criação do relatório diário com os dados do consumo
    relatorio = DailyReportBuilder().\
        set_user(f"{dados['user_id']}").\
        set_date(f"{dados['date']}").\
        add_consumption(water=dados['agua'], energy=dados['energia'],\
            non_recyclabe_residue=dados['residuos_nao_reciclaveis'], recyclabe_residue=dados['residuos_reciclaveis'])

    # Calcula a emissão de CO2 total com base no transporte
    total_co2 = 0
    for vehicle, distance in dados['transportes'].items():
        relatorio.add_vehicle(vehicle, distance)
        total_co2 += Statistics.calcular_emissao_co2(vehicle, distance)

    # Adiciona o consumo de transporte ao relatório e calcula a sustentabilidade
    relatorio.add_consumption(transport=total_co2)
    relatorio.set_sustainability()
        
    try:
        u_id, b_id, n_id = save_report(relatorio)

        notificar_consumo_bruto(u_id, b_id)
        notificar_variacao_isp(u_id, n_id)

        return json.dumps({'success': True}), 200
    except Exception as e:
        # Em caso de erro, retorna a mensagem de erro
        return jsonify({"erro": f"Erro ao cadastrar os dados: {str(e)}"}), 500

#---------------------------------------------------------------------------------------------------

# Rota para editar o consumo de um usuário:
def put_consumption(request):
    # Obtém os dados JSON enviados na requisição pelo cliente
    dados = request.json  
    
    # Extrai o ID do usuário dos cookies da requisição e adiciona aos dados
    dados['user_id'] = request.cookies.get('user_id')  
    
    # Define lista com os campos obrigatórios que devem estar presentes na requisição
    campos_obrigatorios = ['agua', 'energia', 'residuos_nao_reciclaveis', 'residuos_reciclaveis', 'transportes', 'user_id', 'data']
    
    # Verifica se os dados existem e se todos os campos obrigatórios estão presentes
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        # Retorna erro 400 (Bad Request) com mensagem explicativa caso algum campo esteja faltando
        return jsonify({"erro": "Campos obrigatórios: agua, energia, residuos (reciclaveis e não-reciclaveis), transporte, data e user_id"}), 400

    # Extrai o ID do usuário dos dados recebidos
    user_id = dados['user_id']
    
    # Verifica se o usuário está autenticado através de função auxiliar
    if not is_authenticated(user_id):
        # Retorna erro 404 caso o usuário não esteja autenticado
        return {'Erro': 'Usuário não autenticado!'}, 404

    # Obtém a data do consumo dos dados recebidos
    _date = dados.get('data')

    # Cria um objeto de relatório diário usando o padrão Builder
    # Define o usuário convertendo user_id para string
    # Define a data convertendo de formato ISO para objeto date
    # Adiciona dados de consumo (água, energia, resíduos recicláveis e não recicláveis)
    relatorio = DailyReportBuilder().\
        set_user(f"{user_id}").\
        set_date(f"{date.fromisoformat(_date)}").\
        add_consumption(water=dados['agua'], energy=dados['energia'],\
            non_recyclabe_residue=dados['residuos_nao_reciclaveis'], recyclabe_residue=dados['residuos_reciclaveis'])

    # Inicializa variável para acumular o total de emissões de CO2
    total_co2 = 0
    
    # Itera sobre cada veículo e distância nos dados de transporte
    for vehicle, distance in dados['transportes'].items():
        # Adiciona o veículo e distância ao relatório
        relatorio.add_vehicle(vehicle, distance)
        # Calcula e acumula a emissão de CO2 para este veículo/distância
        total_co2 += Statistics.calcular_emissao_co2(vehicle, distance)

    # Adiciona o total de emissões de transporte ao relatório
    relatorio.add_consumption(transport=total_co2)
    # Calcula e define o índice de sustentabilidade do relatório
    relatorio.set_sustainability()

    
        # Tenta atualizar o relatório no banco de dados
    update_report(relatorio)

        # Monta query SQL para buscar o ID do relatório recém-atualizado
        # Busca na tabela relatorios onde o usuário e data coincidem
    comando_rel = f"""
            SELECT ID FROM relatorios
            WHERE fk_id_usuario = {user_id} AND '{_date}' BETWEEN Data_inicio AND Data_fim
            LIMIT 1
        """
        # Executa a query de busca
    resultado = executar_comando("GET", comando_rel)
        
        # Se encontrou um resultado
        
    if resultado:
            # Extrai o ID do relatório do primeiro resultado
            rel_id = resultado[0][0]
            # Atualiza as notificações relacionadas a este relatório
            atualizar_notificacoes_por_relatorio(rel_id)

        # Retorna resposta de sucesso com status 200
     
    return json.dumps({'success': True}), 200
        
    
    return jsonify({"erro": f"Erro ao editar os dados: {str(e)}"}), 500

def delete_consumption(request):
    # Obtém os dados JSON da requisição
    dados = request.json
    # Adiciona o user_id obtido dos cookies aos dados
    dados['user_id'] = request.cookies.get('user_id')
    
    # Define os campos obrigatórios para operação de exclusão
    campos_obrigatorios = ['user_id', 'data']
    
    # Verifica se todos os campos obrigatórios estão presentes
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        # Retorna erro 400 se algum campo obrigatório estiver faltando
        return jsonify({"erro": "Campos obrigatórios: data e user_id"}), 400

    # Obtém a data dos dados recebidos
    _date = dados.get('data')
    # Converte a data de formato ISO para objeto date
    _date = date.fromisoformat(_date)

    try:
        # Apaga todas as notificações relacionadas ao usuário e data específicos
        apagar_notificacoes_por_usuario_e_data(dados['user_id'], _date)
        # Remove o relatório individual correspondente à data e usuário
        delete_single_report(_date, dados['user_id'])
        # Retorna resposta vazia com status 201 (Created) indicando sucesso
        return make_response(), 201
        
    except Exception as e:
        # Captura qualquer exceção durante o processo de exclusão
        # Retorna erro 500 com mensagem explicativa
        return jsonify({"erro": f"Erro ao apagar os dados: {str(e)}"}), 500

# Decorator que define a rota '/editarConsumo' aceitando métodos PUT e DELETE
@user_routes.route('/editarConsumo', methods=['PUT', 'DELETE'])
def edit_consumption():
    # Verifica qual método HTTP foi usado na requisição
    if request.method == "PUT":
        # Se for PUT, chama a função de atualização de consumo
        return put_consumption(request)
    elif request.method == "DELETE":
        # Se for DELETE, chama a função de exclusão de consumo
        return delete_consumption(request)
    
#------------------------------------------------------------------------------------------------------------------

# Sustentabilidade do usuário
@user_routes.route('/retornaSustentabilidade', methods=['GET'])
def retorna_sustentabilidade():
    user_id = request.cookies.get('user_id')

    if not user_id:
        return jsonify({"erro": "ID do usuário não fornecido no header"}), 400
    
    try:
        # Consulta apenas a sustentabilidade do usuário pelo ID
        query = f"SELECT Sustentabilidade FROM usuarios WHERE ID = {int(user_id)}"
        resultado = executar_comando("GET", query)

        if not resultado:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        sustentabilidade = resultado[0][0]  # Obtém o valor da sustentabilidade

        return jsonify({"sustentabilidade": sustentabilidade})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

#------------------------------------------------------------------------------------------------------------------
@user_routes.route('/set_cookie', methods=['GET'])
def set_cookie():
    user_id = request.args.get('user_id') 
    response = make_response()
    response.set_cookie('user_id', user_id)
    return response

@user_routes.route('/get_cookie', methods=['GET'])
def get_cookie():
    user_id = request.cookies.get('user_id')
    return user_id | ''

@user_routes.route('/delete_cookie', methods=['GET'])
def delete_cookie():
    response = make_response()
    response.set_cookie('user_id', '', max_age=0)
    return response

#------------------------------------------------------------------------------------------------------------------

# Rota para exibir o perfil do usuário, aceitando apenas requisições GET
@user_routes.route('/perfil', methods=['GET'])
def profile():
    # Obtém o ID do usuário a partir dos cookies da requisição
    user_id = request.cookies.get('user_id')
    
    # Verifica se o user_id foi fornecido nos cookies
    if not user_id:
        # Retorna erro 500 se o user_id não estiver presente
        return jsonify({"erro": "Erro ao obter os dados: user_id não fornecido"}), 500

    # Busca dados do usuário (exemplo seu)
    # Executa comando SQL para buscar o valor ISI do usuário específico
    isi = executar_comando('GET_BY_ID', f"SELECT ISI FROM usuarios WHERE ID = {user_id}")
    
    # Verifica se o valor ISI foi encontrado
    if isi is not None:
        # Atualiza a classificação de sustentabilidade do usuário baseada no ISI
        executar_comando('PUT', f"UPDATE usuarios SET Sustentabilidade = '{Statistics.classificar_sustentabilidade(isi)}' WHERE ID = {user_id}")
    else:
        # Define valor padrão 1 se ISI não foi encontrado
        isi = 1

    # Obtém dados globais do usuário (consumos gerais)
    rep = get_global_data(user_id)
    
    # Itera sobre todos os valores do dicionário de dados
    for k, v in rep.items():
        # Substitui valores None por 0 para evitar erros de cálculo
        if v is None:
            rep[k] = 0

    # Normaliza os dados de consumo de água usando a classe Statistics
    w_norm = Statistics.normalize('water', rep.get('Agua', 0))
    # Normaliza os dados de consumo de energia
    e_norm = Statistics.normalize('energy', rep.get('Energia', 0))
    # Normaliza os dados de resíduos não recicláveis
    nr_norm = Statistics.normalize('non_recyclabe_residue', rep.get('ResiduosNR', 0))
    # Normaliza os dados de transporte (emissões de CO2)
    t_norm = Statistics.normalize('transport', rep.get('co2_total', 0))
    
    # Gera um gráfico de radar com os valores normalizados (invertidos para melhor visualização)
    svg = radar_graph([isi, 1 - t_norm, 1 - w_norm, 1 - e_norm, 1 - nr_norm])

    # Calcula o total de resíduos somando recicláveis e não recicláveis
    # Se a soma for 0, define como 1 para evitar divisão por zero
    rep['ResiduosT'] = rep['ResiduosR'] + rep['ResiduosNR'] if rep['ResiduosR'] + rep['ResiduosNR'] > 0 else 1

    # Busca notificações do usuário
    # Query SQL complexa com JOINs para buscar notificações relacionadas ao usuário
    comando = f"""
        SELECT
            n.ID,
            n.Titulo,
            n.Conteudo
        FROM
            notificacoes n
        LEFT JOIN consumos_normalizados cn ON n.fk_consumos_normalizados_id = cn.ID
        LEFT JOIN consumos_brutos cb ON n.fk_consumos_brutos_id = cb.ID
        LEFT JOIN relatorios r1 ON cn.fk_relatorio = r1.ID
        LEFT JOIN relatorios r2 ON cb.fk_relatorio = r2.ID
        WHERE
            (r1.fk_id_usuario = {user_id} OR r2.fk_id_usuario = {user_id})
        ORDER BY n.ID DESC
    """
    # Executa a query para buscar as notificações
    resultados = executar_comando("GET", comando)

    # Inicializa lista vazia para armazenar as notificações formatadas
    lista_notificacoes = []
    
    # Itera sobre cada linha dos resultados da query
    for row in resultados:
        # Adiciona cada notificação formatada como dicionário na lista
        lista_notificacoes.append({
            "ID": row[0],      # ID da notificação
            "Titulo": row[1],  # Título da notificação
            "Conteudo": row[2] # Conteúdo da notificação
        })

    # Renderiza o template HTML passando os dados processados
    return render_template('meuperfil.html', rep=rep, svg=svg, notificacoes=lista_notificacoes)

# Rota para exibir relatórios específicos, aceitando parâmetro _id na URL
@user_routes.route('/relatorio/<_id>', methods=['GET'])
def report(_id):
    # Inicializa dicionário vazio para armazenar dados do relatório
    rep = {}
    # Inicializa lista vazia para armazenar gráficos
    graphs = []
    
    # Obtém o ID do usuário a partir dos cookies da requisição
    _user_id = request.cookies.get('user_id')
    
    # Verifica se o user_id foi fornecido nos cookies
    if(not _user_id):
        # Retorna erro 500 se o user_id não estiver presente
        return jsonify({"erro": "Erro ao obter os dados: user_id não fornecido"}), 500

    # Bloco try-except para capturar e tratar possíveis erros
    try:
        # Obtém dados do relatório semanal específico usando o ID do relatório e usuário
        rep = get_week_report(_id, _user_id)

        # Itera sobre cada item do relatório (exceto 'general')
        for key, dia in rep.items():
            # Verifica se a chave não é 'general' (dados gerais)
            if key != 'general':
                # Adiciona o índice do dia da semana (0=segunda, 6=domingo)
                dia['weekday_index'] = dia['data_insercao'].weekday()

        # Extrai os gráficos dos dados gerais do relatório
        graphs = rep['general']['graficos']

        # Itera novamente sobre todos os dias do relatório
        for key, dia in rep.items():
            # Calcula o total de resíduos para cada dia
            # Se a soma for 0, define como 1 para evitar divisão por zero
            dia['ResiduosT'] = dia['ResiduosR'] + dia['ResiduosNR'] if dia['ResiduosR'] + dia['ResiduosNR'] > 0 else 1

    # Captura qualquer exceção que possa ocorrer durante o processamento
    except Exception as e:
        # Retorna erro 500 com a mensagem de erro específica
        return jsonify({"erro": f"Erro ao obter os dados: {str(e)}"}), 500

    # Renderiza o template HTML passando os dados do relatório, ID e gráficos
    return render_template('relatoriosdiarios.html', rep=rep, _id=_id, graphs=graphs)

# Filtro round
@user_routes.route('round')
def round_filter(value, precision=2):
    if value is None or value == 'N/A':
        return value
    return round(float(value), precision)

#----------------------------------------------------------------------
#relatorios
@user_routes.route('/relatoriosUser', methods=["GET"])
def exibe_relatorios_usuario():
    dados = {}

    dados['user_id'] = request.cookies.get('user_id')

    if not is_authenticated(dados['user_id']):
        return {'Erro': 'Usuário não autenticado!'}, 404

    retorna_info_relatorios = f"SELECT * FROM relatorios WHERE fk_id_usuario = '{dados['user_id']}'"
    info_relatorios_usuario = executar_comando("GET", retorna_info_relatorios)

    # Lista para armazenar os dicionários formatados
    info_relatorios = []

    for relatorio in info_relatorios_usuario:
        dados_relatorio = {
            "id_relatorio": relatorio[0],
            "fk_id_usuario": relatorio[1],
            "data_inicio": relatorio[2].strftime("%Y-%m-%d"),
            "data_fim": relatorio[3].strftime("%Y-%m-%d"),
            "resumo": relatorio[4]
        }
        info_relatorios.append(dados_relatorio)

    return render_template('relatorios.html', info_relatorios=info_relatorios)




#---------------------------------------------------------------------------------------
#Redefinição de senha

#Rota para enviar token
@user_routes.route('/enviarToken/<email_usuario>', methods=['GET'])
def send_token(email_usuario):

    print(f"\n\n\n\n\n{email_usuario}\n\n\n")

    #Retorna tempo limite desse usuario
    comando_tempo_limite = f"SELECT tempo_limite FROM reset_password WHERE email_usuario = '{email_usuario}'"
    tempo_limite = executar_comando("GET_BY_ID", comando_tempo_limite)

    #Verifica se e-mail existe
    if tempo_limite is None:
        return {"Status": 'E-mail inexistente'}, 400

    #Calcula tempo atual
    tempo_atual = datetime.now()

    if tempo_atual < tempo_limite:

        #Pegar token atual
        comando_token = f'SELECT token_atual FROM reset_password WHERE email_usuario = "{email_usuario}" LIMIT 1'
        token_atual = executar_comando("GET_BY_ID", comando_token)
        
        #Alterar tempo atual para tempo atual + 30min
        comando_atualiza_tempo_limite = f"UPDATE reset_password SET tempo_limite = NOW() + INTERVAL 30 MINUTE WHERE email_usuario = '{email_usuario}'"
        executar_comando("POST", comando_atualiza_tempo_limite)

        #Envia email para usuario com Token atual
        enviar_email(email_usuario, token_atual)

        return {"Status":f'Token enviado para endereço de email: {email_usuario}'}, 200
    
    else:

        ###Alterar token_atual para novo valor aleatório
        
        #Gera token novo
        chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        token_novo = ''.join(secrets.choice(chars) for _ in range(5))

        #Comando para atualizar token
        comando_atualiza_token = f"UPDATE reset_password SET token_atual = '{token_novo}' WHERE email_usuario = '{email_usuario}'"
        executar_comando("POST", comando_atualiza_token)

        ###Reseta tempo limite para +infinito dnv
        comando_reseta_tempo_limite = f"UPDATE reset_password SET tempo_limite = '2030-04-20 18:00:00' WHERE email_usuario = '{email_usuario}'"
        executar_comando("POST", comando_reseta_tempo_limite)

        return {"Status": 'Erro ao recuperar senha'}, 400
    

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#Rota para resetar senha
@user_routes.route('/resetarSenha', methods=['PUT'])
def reset_password():
    data = request.json

    email_usuario = data.get('email')
    token = data.get('token')
    nova_senha = data.get('novasenha')

    #Verificar no banco se o email do usuario possui este token e o tempo atual é menor do que o tempo limite
    comando_tempo_limite = f"SELECT tempo_limite FROM reset_password WHERE email_usuario = '{email_usuario}'"
    comando_token_atual = f"SELECT token_atual FROM reset_password WHERE email_usuario = '{email_usuario}'"
    
    tempo_limite = executar_comando("GET_BY_ID", comando_tempo_limite)
    token_atual = executar_comando("GET_BY_ID", comando_token_atual)
    tempo_atual = datetime.now()
    
    if token != token_atual or tempo_atual > tempo_limite:
        return {"Status": 'Seu token expirou ou está incorreto'}, 400

    if tempo_limite != None or tempo_limite != []:
        comando_atualizar_senha = f"UPDATE usuarios SET senha = '{nova_senha}' WHERE email = '{email_usuario}'"
        retorno = executar_comando("POST", comando_atualizar_senha) 

    if retorno == 'sucesso':
        return {"Status": 'sucesso'}, 201
    else:
        return {"Status": 'erro'}, 400


#-------------------------------------------------------------------------------------------------------------------

#retorna notificações

# @user_routes.route('/notificacoes', methods=['GET'])
# def notificacoes():
#     user_id = request.cookies.get('user_id')
#     if not user_id:
#         # redirecionar para login ou erro
#         pass
    
#     try:
#         comando = f"""
#             SELECT
#                 n.ID,
#                 n.Titulo,
#                 n.Conteudo
#             FROM
#                 notificacoes n
#             LEFT JOIN consumos_normalizados cn ON n.fk_consumos_normalizados_id = cn.ID
#             LEFT JOIN consumos_brutos cb ON n.fk_consumos_brutos_id = cb.ID
#             LEFT JOIN relatorios r1 ON cn.fk_relatorio = r1.ID
#             LEFT JOIN relatorios r2 ON cb.fk_relatorio = r2.ID
#             WHERE
#                 (r1.fk_id_usuario = {user_id} OR r2.fk_id_usuario = {user_id})
#             ORDER BY n.ID DESC
#         """

#         resultados = executar_comando("GET", comando)

#         lista_notificacoes = []
#         for row in resultados:
#             lista_notificacoes.append({
#                 "ID": row[0],
#                 "Titulo": row[1],
#                 "Conteudo": row[2]
#             })

#         return render_template('meuperfil.html', notificacoes=lista_notificacoes)

#     except Exception as e:
#         return f"Erro ao buscar notificações: {str(e)}", 500





#/////////////////////////////////////////////////////////////////////////

#rotas criadas para teste

# @user_routes.route('/testarNotificacaoISP', methods=['POST'])
# def testar_notificacao_isp():
#     dados = request.json
#     user_id = dados.get('user_id')

#     if not user_id:
#         return {'erro': 'Informe user_id'}, 400

#     try:
#         notificar_variacao_isp(user_id)
#         return {'status': 'Notificação de ISP gerada com sucesso!'}, 200
#     except Exception as e:
#         return {'erro': str(e)}, 500


# @user_routes.route('/testarNotificacaoBruto', methods=['POST'])
# def testar_notificacao_bruto():
#     dados = request.json
#     user_id = dados.get('user_id')

#     if not user_id:
#         return {'erro': 'Informe user_id'}, 400

#     try:
#         notificar_consumo_bruto(user_id)
#         return {'status': 'Notificação de consumo bruto gerada com sucesso!'}, 200
#     except Exception as e:
#         return {'erro': str(e)}, 500
