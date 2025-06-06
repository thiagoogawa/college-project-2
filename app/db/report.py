# Importa a biblioteca mysql.connector para conexão com banco de dados MySQL
import mysql.connector
# Importa a classe Statistics do módulo de normalização para cálculos estatísticos
from ..algorithms.normalizacao import Statistics
# Importa funções para geração de diferentes tipos de gráficos
from ..algorithms.graph_generator import radar_graph, bar_graph, polyline_graph, sector_graph
# Importa a função executar_comando do módulo database para execução de queries SQL
from .database import executar_comando
# Importa classes para manipulação de datas e horários
from datetime import datetime, timedelta, date
# Importa biblioteca para manipulação de dados JSON
import json

def get_global_data(user_id):
    """
    Gera relatório geral (médias) de consumo e transporte de um usuário específico.
    """
    # Executa query para obter médias de consumo e dados do usuário
    r = executar_comando("GET_DICT_ONE", f"""
        SELECT
            AVG(b.Agua) AS Agua,
            AVG(b.Energia) AS Energia,
            AVG(b.residuos_reciclaveis) AS ResiduosR,
            AVG(b.residuos_nao_reciclaveis) AS ResiduosNR,
            AVG(r.ISS) AS Indice,
            u.Sustentabilidade as Sustentabilidade,
            u.nome as Nome,
            u.data_cadastro as DataCadastro
        FROM consumos_brutos b
        JOIN relatorios r ON b.fk_relatorio = r.ID
        RIGHT JOIN usuarios u ON r.fk_id_usuario = u.ID
        WHERE u.ID = {user_id}
    """)

    # Executa query para obter dados de transporte agrupados por tipo de veículo
    t = executar_comando("GET", f"""
        SELECT 
            t.Tipo_veiculo, 
            AVG(t.Distancia) AS DistanciaMedia
        FROM transporte t
        JOIN consumos_brutos b ON t.fk_consumos_brutos_id = b.ID
        JOIN relatorios r ON b.fk_relatorio = r.ID
        WHERE r.fk_id_usuario = {user_id}
        GROUP BY Tipo_veiculo;
    """)

    # Inicializa variável para armazenar total de CO2 emitido
    co2_total = 0
    # Converte resultado de transporte para dicionário
    t = dict(t)
    # Verifica se há dados de transporte
    if len(t) > 0:
        # Itera sobre cada tipo de veículo e sua distância média
        for key, value in t.items():
            # Calcula emissão de CO2 para cada tipo de veículo
            emission = Statistics.calcular_emissao_co2(key, value)
            # Armazena distância e emissão como tupla no dicionário
            t[key] = (value, emission)
            # Soma à emissão total de CO2
            co2_total += emission

    # Constrói o relatório final combinando dados de consumo e transporte
    report = {
        **r,  # Desempacota dados de consumo básico
        'Transporte': t,  # Adiciona dados de transporte processados
        'co2_total': co2_total  # Adiciona total de CO2 emitido
    }

    # Retorna o relatório completo
    return report

def get_day_data(c_date, user_id):
    """
    Consulta os dados diarios de consumo, juntando tabelas de consumo brutos, normalizados e de relatório.
    """
    # Executa query para obter dados de consumo de um dia específico
    return executar_comando("GET_DICT", f"""
        SELECT
            b.ID,
            b.Agua,
            b.Energia,
            b.residuos_reciclaveis AS ResiduosR,
            b.residuos_nao_reciclaveis AS ResiduosNR,
            n.ID AS id_normalizado,
            n.ISP,
            b.data_insercao
        FROM consumos_brutos b
            JOIN relatorios r ON b.fk_relatorio = r.ID
        JOIN consumos_normalizados n ON b.data_insercao = n.data_insercao
            AND b.fk_relatorio = n.fk_relatorio
        WHERE b.data_insercao = '{c_date}' AND
            r.fk_id_usuario = {user_id}
    """)

def get_day_report(c_date, user_id):
    """
    Gera relatório do dia, com dados de consumo,
    transporte e notificações vinculadas.
    """
    # Obtém dados básicos do dia
    res = get_day_data(c_date, user_id)

    # Inicializa estrutura do relatório diário
    day_report = {
        'transporte': {},
        'notificacoes': []
    }

    # Verifica se há dados para o dia solicitado
    if res:
        # Pega o primeiro (e único) resultado
        res = res[0]
    else:
        # Retorna relatório vazio se não há dados
        return day_report

    # Busca dados de transporte para o consumo bruto do dia
    transporte = get_transport_data(res['ID'])
    # Busca notificações relacionadas ao consumo normalizado
    notificacoes = get_notifications(res['id_normalizado'])

    # Construção do relatório do dia (utiliza do operador ** para desempacotar o dicionario)
    day_report = {
        **res,  # Inclui todos os dados básicos do dia
        'transporte': transporte,  # Adiciona dados de transporte
        'notificacoes': notificacoes  # Adiciona notificações
    }
    
    # Retorna o relatório completo do dia
    return day_report

def get_week_data(report_id, user_id):
    """
    Consulta os dados semanais de consumo, juntando tabelas de consumo brutos, normalizados e de relatório.
    """
    # Executa query para obter todos os dados de uma semana específica
    return executar_comando("GET_DICT", f"""
        SELECT
            b.ID,
            b.Agua,
            b.Energia,
            b.residuos_reciclaveis AS ResiduosR,
            b.residuos_nao_reciclaveis AS ResiduosNR,
            b.data_insercao,
            n.ID AS id_normalizado,
            n.ISP,
            r.fk_id_usuario,
            r.ISS
        FROM consumos_brutos b
		JOIN relatorios r ON b.fk_relatorio = r.ID
        JOIN consumos_normalizados n ON b.data_insercao = n.data_insercao
			AND b.fk_relatorio = n.fk_relatorio
        WHERE r.ID = {report_id} AND
            r.fk_id_usuario = {user_id}
        ORDER BY b.data_insercao ASC
    """)

def get_transport_data(id_consumo_bruto):
    """
    Busca dados de transporte e retorna um dicionário tipo_veiculo: distancia
    """
    # Executa query para obter dados de transporte de um consumo específico
    res = executar_comando("GET", f"""
        SELECT Tipo_veiculo, Distancia
        FROM transporte
        WHERE fk_consumos_brutos_id = {id_consumo_bruto}
    """)

    # Retorna dicionário ou vazio se não houver transporte
    return dict(res) if res else {}

def get_notifications(id_normalizado):
    """
    Busca notificações associadas a um consumo normalizado.
    """
    # Executa query para obter notificações de um consumo normalizado específico
    return executar_comando("GET_DICT", f"""
        SELECT titulo, conteudo
        FROM notificacoes
        WHERE fk_consumos_normalizados_id = {id_normalizado}
    """)

def get_graphs(report_id): 
    """
    Busca gráficos associadas a um relatório.
    """
    # Executa query para obter todos os gráficos de um relatório específico
    return executar_comando("GET_DICT", f"""
        SELECT *
        FROM graficos
        WHERE fk_relatorios_id = {report_id}
    """)

def get_week_report(report_id, user_id):
    """
    Gera relatório da semana, com dados de consumo por dia, médias gerais,
    transporte e notificações vinculadas.
    """
    # Obtém dados da semana usando o ID do relatório e ID do usuário
    res = get_week_data(report_id, user_id)
    # Calcula o número total de dias com dados
    total_days = len(res)
    
    # Inicializa o dicionário que conterá o relatório completo da semana
    week_report = {'general': {}}
    # Dicionário para armazenar os totais de cada métrica para cálculo posterior de médias
    total_metrics = {'Agua': 0, 'Energia': 0, 'ResiduosR': 0, 'ResiduosNR': 0, 'ISP': 0, 'DistanciaTotal': 0}
    # Variável para armazenar o ID do usuário extraído dos dados
    user_id = None
    # Dicionário para armazenar os totais de transporte por tipo
    transport_totals = {}

    # Processa cada dia de dados encontrado
    for i, entry in enumerate(res):
        # Cria a chave para o dia atual (day_1, day_2, etc.)
        dia = f'day_{i+1}'
        
        # Busca dados adicionais relacionados a este dia
        transporte = get_transport_data(entry['ID'])
        notificacoes = get_notifications(entry['id_normalizado'])
        
        # Constrói o relatório do dia incorporando todos os dados disponíveis
        week_report[dia] = {
            **entry,  # Inclui todos os dados originais do dia
            'transporte': transporte,  # Adiciona informações de transporte
            'notificacoes': notificacoes  # Adiciona notificações
        }
        
        # Armazena o ID do usuário e acumula métricas para cálculos de média
        user_id = entry['fk_id_usuario']
        for metric in total_metrics:
            if metric in entry:
                total_metrics[metric] += entry[metric]
        
        # Calcula e acumula dados de transporte
        transport_day_distance = 0
        for tipo, distancia in transporte.items():
            if tipo == 'bicicleta':  # Não emite CO2 então não entra no calculo
                continue
                
            # Inicializa contadores para este tipo de transporte se necessário
            if tipo not in transport_totals:
                transport_totals[tipo] = {'sum': 0, 'amount': 0}
            # Acumula distância total para este tipo de transporte
            transport_totals[tipo]['sum'] += distancia
            # Soma à distância total de transporte para este dia
            transport_day_distance += distancia
            
        # Adiciona o total de transporte diário ao relatório do dia
        week_report[dia]['transporte_total'] = transport_day_distance
        # Adiciona o total de transporte ao relatório da semana
        total_metrics['DistanciaTotal'] += transport_day_distance

    # Calcula médias de emissões de CO2
    total_co2 = 0
    for tipo, dado in transport_totals.items():
        # Emissão com base na soma total de distâncias
        co2_total = Statistics.calcular_emissao_co2(tipo, dado['sum'])
        total_co2 += co2_total

    # Calcula e armazena médias gerais se houver dias com dados
    if total_days > 0:
        # Inicializa a seção geral do relatório com valores padrão
        week_report['general'] = {
            'ID': -1,
            'fk_id_usuario': user_id,
            'data_insercao': '',
            'ISP': -1,
            'total_co2': total_co2,  # Total de CO2 emitido
            'graficos': get_graphs(report_id)
        }
        
        # Adiciona as médias calculadas para cada métrica
        for metric, total in total_metrics.items():
            if metric != 'ISP':
                week_report['general'][metric] = total / total_days
            else:
                week_report['general']['ISS'] = total / total_days

    # Retorna o relatório semanal completo
    return week_report

def generate_graph(user_id, id_report, id_bruto):
    # Função para gerar gráficos baseados nos dados de consumo do usuário
    
    # Busca dados de consumo brutos (água, energia, resíduos) do banco de dados
    data = executar_comando(
        "GET_DICT",
        f"""
        SELECT
            b.Agua,
            b.Energia,
            b.residuos_reciclaveis AS ResiduosR,
            b.residuos_nao_reciclaveis AS ResiduosNR,
            b.data_insercao
        FROM consumos_brutos b
        JOIN relatorios r ON b.fk_relatorio = r.ID
        WHERE r.ID = {id_report} AND
            r.fk_id_usuario = {user_id}
        ORDER BY b.data_insercao ASC
        """
    )

    # Busca dados de transporte do banco de dados, agrupados por tipo de veículo
    t = executar_comando(
        "GET_DICT",
        f"""
        SELECT 
            t.Tipo_veiculo AS veiculo, 
            SUM(t.Distancia) AS distancia
        FROM transporte t
        JOIN consumos_brutos b ON t.fk_consumos_brutos_id = b.ID
        JOIN relatorios r ON b.fk_relatorio = r.ID
        WHERE r.ID = {id_report}
        GROUP BY Tipo_veiculo
        """
    )

    # Dicionário para armazenar emissões de CO2 por tipo de veículo
    transport_emissions = {}
    for item in t:
        veiculo = item['veiculo']
        # Converte para float de forma segura e define 0 como padrão se a conversão falhar
        try:
            distancia = float(item['distancia']) if item['distancia'] is not None else 0.0
            # Calcula emissão de CO2 baseado no tipo de veículo e distância
            co2 = Statistics.calcular_emissao_co2(veiculo, distancia)
            transport_emissions[veiculo] = co2
        except (ValueError, TypeError):
            # Em caso de erro na conversão, define a emissão como zero
            transport_emissions[veiculo] = 0.0

    # Função auxiliar para converter valores para float de forma segura
    def safe_float(value):
        # Verifica se o valor é None antes de tentar converter
        if value is None:
            return 0.0
        try:
            # Tenta converter para float
            return float(value)
        except (ValueError, TypeError):
            # Retorna valor padrão se a conversão falhar
            return 0.0

    # Processa dados de água com conversões seguras
    water_data = [safe_float(data[i].get('Agua')) for i in range(len(data))]
    # Processa dados de energia com conversões seguras
    energy_data = [safe_float(data[i].get('Energia')) for i in range(len(data))]
    
    # Calcula as somas de resíduos com tratamento seguro para valores inválidos
    residuos_nr_sum = sum(safe_float(data[i].get('ResiduosNR')) for i in range(len(data)))
    residuos_r_sum = sum(safe_float(data[i].get('ResiduosR')) for i in range(len(data)))

    # Cria diferentes tipos de gráficos com os dados processados
    graphs = {
        # Gráfico de linha para dados de água
        'water': polyline_graph('Água', 'L', [i+1 for i in range(len(data))], water_data),
        # Gráfico de barras para dados de energia
        'energy': bar_graph('Energia', 'kWh', [i+1 for i in range(len(data))], energy_data),
        # Gráfico de setores para dados de resíduos
        'residue': sector_graph('Resíduos', 'kg', ['Resíduos NR', 'Resíduos R'], [residuos_nr_sum, residuos_r_sum]),
        # Gráfico de setores para dados de transporte
        'transport': sector_graph('Transporte', 'kg CO2', list(transport_emissions.keys()),
                                [transport_emissions[i] for i in transport_emissions.keys()])
    }

    # Apaga gráficos anteriores e insere os gráficos gerados no banco de dados
    executar_comando("POST", f"DELETE FROM graficos WHERE fk_relatorios_id = {id_report}")
    executar_comando(
        "POST",
        f"""
            INSERT INTO graficos (Tipo_grafico, Tipo_armazenado, Construcao, fk_relatorios_id) VALUES
            ('polyline', 'water', '{graphs['water']}', {id_report}),
            ('bar', 'energy', '{graphs['energy']}', {id_report}),
            ('sector', 'residue', '{graphs['residue']}', {id_report}),
            ('sector', 'transport', '{graphs['transport']}', {id_report})
        """
    )

def delete_single_report(date, user_id):
    # Função para deletar um relatório específico de uma data
    try:
        # Busca IDs relacionados ao relatório da data especificada
        ids = executar_comando(
            "GET_DICT_ONE",
            f"""SELECT 
                    r.ID as report_id, 
                    b.ID as brute_id, 
                    n.ID as normalized_id, 
                    (
                        SELECT COUNT(*) 
                        FROM consumos_brutos cb
                        WHERE cb.fk_relatorio = r.ID
                    ) AS count FROM relatorios r
                RIGHT OUTER JOIN consumos_brutos b ON b.data_insercao = '{date}'
                RIGHT OUTER JOIN consumos_normalizados n ON n.data_insercao = '{date}'
                WHERE '{date}' BETWEEN r.Data_inicio AND r.Data_fim AND r.fk_id_usuario = {user_id}"""
        )
    except Exception:
        # Em caso de erro na consulta, encerra a função
        return

    # Verifica se os dados necessários foram encontrados
    if (not ids) or (ids and len(ids.items()) < 3):
        return

    # Remove dados de transporte associados ao consumo bruto
    executar_comando("POST", f"DELETE FROM transporte WHERE fk_consumos_brutos_id = {ids['brute_id']}")
    # Remove notificações associadas ao consumo normalizado
    executar_comando("POST", f"DELETE FROM notificacoes WHERE fk_consumos_normalizados_id = {ids['normalized_id']}")
    # Remove o registro de consumo bruto
    executar_comando("POST", f"DELETE FROM consumos_brutos WHERE ID = {ids['brute_id']}")
    # Remove o registro de consumo normalizado
    executar_comando("POST", f"DELETE FROM consumos_normalizados WHERE ID = {ids['normalized_id']}")

    # Se era o último registro do relatório, remove o relatório inteiro
    if ids['count'] <= 1:
        # Remove gráficos associados ao relatório
        executar_comando("POST", f"DELETE FROM graficos WHERE fk_relatorios_id = {ids['report_id']}")
        # Remove o relatório
        executar_comando("POST", f"DELETE FROM relatorios WHERE ID = {ids['report_id']}")
    else:
        # Se ainda há outros registros, regenera os gráficos
        generate_graph(user_id, ids['report_id'], ids['brute_id'])

def update_report(r):
    """
    Atualiza um relatório existente com novos dados brutos, transporte e normalizados.
    """

    # Verifica se a data não está no futuro
    if datetime.fromisoformat(r.report['date']).date() > date.today():
        raise Exception("Data de edição/cadastro não pode ser no futuro!")

    # 1. Recuperar o ID do relatório correspondente à data e usuário informados
    id_report = executar_comando(
        "GET",
        f"""SELECT r.ID FROM relatorios r
        RIGHT OUTER JOIN consumos_brutos b ON b.data_insercao = '{r.report['date']}'
        WHERE '{r.report['date']}' BETWEEN r.Data_inicio AND r.Data_fim AND r.fk_id_usuario = {r.report['user']}"""
    )

    # Se não encontrou relatório existente, cria um novo
    if len(id_report) <= 0:
        save_report(r)
        return
    # Extrai o ID do relatório encontrado
    id_report = id_report[0][0]

    # 2. Atualizar os dados brutos de consumo associados ao relatório
    sql_bruto = f"""
        UPDATE consumos_brutos 
        SET 
            Agua = {r.report['raw']['water']},
            Energia = {r.report['raw']['energy']}, 
            residuos_nao_reciclaveis = {r.report['raw']['non_recyclabe_residue']}, 
            residuos_reciclaveis = {r.report['raw']['recyclabe_residue']}
        WHERE
            fk_relatorio = {id_report} AND data_insercao = '{r.report['date']}'
    """
    executar_comando("POST", sql_bruto)

    # 3. Recuperar o ID do consumo bruto atualizado
    id_bruto = executar_comando(
        "GET",
        f"SELECT ID FROM consumos_brutos WHERE fk_relatorio = {id_report} AND data_insercao = '{r.report['date']}'"
    )[0][0]

    # 4. Excluir os registros antigos de transporte vinculados ao consumo bruto
    executar_comando("POST", f"DELETE FROM transporte WHERE fk_consumos_brutos_id = {id_bruto}")

    # 5. Inserir os novos registros de transporte atualizados
    for key, value in r.report['vehicle'].items():
        sql_transporte = f"""
            INSERT INTO transporte (Tipo_veiculo, Distancia, fk_consumos_brutos_id)
            VALUES ('{key}', {value}, {id_bruto})
        """
        executar_comando("POST", sql_transporte)

    # 6. Atualizar os dados normalizados de consumo associados ao relatório
    sql_norm = f"""
        UPDATE consumos_normalizados
        SET
            Agua = {r.report['normalized']['water']},
            Energia = {r.report['normalized']['energy']},
            Residuos = {r.report['normalized']['non_recyclabe_residue']}, 
            Transporte = {r.report['normalized']['transport']},
            ISP = {r.report['sustainability']}
        WHERE
            fk_relatorio = {id_report} AND data_insercao = '{r.report['date']}'
    """
    executar_comando("POST", sql_norm)

    # Recupera ID do consumo normalizado
    id_norm = executar_comando("GET", f"SELECT ID FROM consumos_normalizados WHERE fk_relatorio = {id_report} AND data_insercao = '{r.report['date']}'")[0][0]

    # 7. Atualizar o ISS (Índice de Sustentabilidade Semanal) no relatório
    sql_upt_r = f"""
        UPDATE relatorios
        SET
            ISS = (SELECT AVG(ISP) FROM consumos_normalizados WHERE fk_relatorio = {id_report})
        WHERE
            ID = {id_report}
    """
    executar_comando("PUT", sql_upt_r)

    # 8. Atualizar o ISI (Índice de Sustentabilidade Individual) do usuário
    sql_upt_u = f"""
        UPDATE usuarios
        SET
            ISI = (SELECT AVG(ISS) FROM relatorios WHERE fk_id_usuario = {r.report['user']})
        WHERE
            ID = {r.report['user']}
    """
    executar_comando("PUT", sql_upt_u)

    # Regenera os gráficos com os dados atualizados
    generate_graph(r.report['user'], id_report, id_bruto)

    # Retorna IDs importantes para uso posterior
    return r.report['user'], id_bruto, id_norm

def save_report(r):
    """
    Função para salvar ou atualizar um relatório semanal de consumo de recursos de um usuário.
    """

    # 0. Preparação de datas (segunda-feira e domingo da semana do relatório)
    report_date = datetime.strptime(r.report['date'], '%Y-%m-%d')
    # Calcula quantos dias se passaram desde a segunda-feira (0=segunda, 6=domingo)
    days_from_monday = report_date.weekday()
    # Calcula a data da segunda-feira da semana do relatório
    monday_date = (report_date - timedelta(days=days_from_monday)).strftime('%Y-%m-%d')
    # Calcula a data do domingo da semana do relatório
    sunday_date = (report_date + timedelta(days=6 - days_from_monday)).strftime('%Y-%m-%d')

    # 1. Verificar se já existe um relatório para a semana atual
    id_report = executar_comando(
        "GET",
        f"SELECT ID FROM relatorios WHERE '{r.report['date']}' BETWEEN Data_inicio AND Data_fim AND fk_id_usuario = {r.report['user']}"
    )

    # 2. Caso não exista, criar um novo relatório
    if len(id_report) <= 0:
        # Monta query para inserir novo relatório com as datas da semana
        query = f"""
            INSERT INTO relatorios (fk_id_usuario, Data_inicio, Data_fim)
            VALUES ({r.report['user']}, '{monday_date}', '{sunday_date}')
        """
        # Executa a inserção do novo relatório
        executar_comando("POST", query)

    # 3. Recuperar o ID do relatório válido para a data atual
    id_report = executar_comando(
        "GET",
        f"SELECT ID FROM relatorios WHERE '{r.report['date']}' BETWEEN Data_inicio AND Data_fim AND fk_id_usuario = {r.report['user']}"
    )[0][0]  # Pega o primeiro resultado da primeira linha

    # 4. Inserir os dados brutos de consumo
    sql_bruto = f"""
        INSERT INTO consumos_brutos (Agua, Energia, residuos_reciclaveis, residuos_nao_reciclaveis, fk_relatorio, data_insercao)
        VALUES ({r.report['raw']['water']}, {r.report['raw']['energy']},
                {r.report['raw']['recyclabe_residue']}, {r.report['raw']['non_recyclabe_residue']},
                {id_report}, '{r.report['date']}')
    """
    try:
        # Tenta executar a inserção dos dados brutos
        executar_comando("POST", sql_bruto)
    except Exception as e:
        # Trata exceções que podem ocorrer durante a inserção
        # Caso o erro não seja de chave duplicada (código 1062), exibir erro
        if f"{e}".find("1062") != 0:
            print(e)  # Imprime outros tipos de erro
        else:
            # Se for erro de chave duplicada, lança exceção customizada
            raise Exception("Dados já cadastrados na data escolhida!")

    # 5. Recuperar o ID do consumo bruto recém-inserido
    id_bruto = executar_comando("GET", f"SELECT ID FROM consumos_brutos WHERE fk_relatorio = {id_report} AND data_insercao = '{r.report['date']}'")[0][0]

    # 6. Inserir os dados normalizados de consumo
    sql_norm = f"""
        INSERT INTO consumos_normalizados (Agua, Energia, Residuos, Transporte, fk_relatorio, data_insercao, ISP)
        VALUES ({r.report['normalized']['water']}, {r.report['normalized']['energy']},
                {r.report['normalized']['non_recyclabe_residue']}, {r.report['normalized']['transport']},
                {id_report}, '{r.report['date']}', {r.report['sustainability']})
    """
    # Executa a inserção dos dados normalizados
    executar_comando("POST", sql_norm)

    # Recupera o ID do consumo normalizado recém-inserido
    id_norm = executar_comando("GET", f"SELECT ID FROM consumos_normalizados WHERE fk_relatorio = {id_report} AND data_insercao = '{r.report['date']}'")[0][0]

    # 7. Inserir os dados de transporte relacionados ao consumo bruto
    for key, value in r.report['vehicle'].items():
        # Monta query para inserir dados de transporte
        sql_transporte = f"""
            INSERT INTO transporte (Tipo_veiculo, Distancia, fk_consumos_brutos_id)
            VALUES ('{key}', {value}, {id_bruto})
        """
        # Executa a inserção dos dados de transporte
        executar_comando("POST", sql_transporte)

    # 8. Atualizar o ISS do relatório (média do ISP dos consumos normalizados da semana)
    sql_upt_r = f"""
        UPDATE relatorios
        SET
            ISS = (SELECT AVG(ISP) FROM consumos_normalizados WHERE fk_relatorio = {id_report})
        WHERE
            ID = {id_report}
    """
    # Executa a atualização do ISS no relatório
    executar_comando("PUT", sql_upt_r)

    # 9. Atualizar o ISI do usuário (média do ISS de todos os relatórios do usuário)
    sql_upt_u = f"""
        UPDATE usuarios
        SET
            ISI = (SELECT AVG(ISS) FROM relatorios WHERE fk_id_usuario = {r.report['user']})
        WHERE
            ID = {r.report['user']}
    """
    # Executa a atualização do ISI no usuário
    executar_comando("PUT", sql_upt_u)

    # Gera gráficos baseados nos dados inseridos
    generate_graph(r.report['user'], id_report, id_bruto)

    # Retorna os IDs do usuário, consumo bruto e consumo normalizado
    return r.report['user'], id_bruto, id_norm
