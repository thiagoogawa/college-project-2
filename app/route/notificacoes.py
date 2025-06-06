
#funções para notificação


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


def notificar_variacao_isp(user_id, id_consumo_normalizado):
    # Busca os dois últimos ISP do usuário
    comando = f"""
        SELECT cn.ISP 
        FROM consumos_normalizados cn
        JOIN relatorios r ON cn.fk_relatorio = r.ID
        WHERE r.fk_id_usuario = {user_id} AND cn.ISP IS NOT NULL
        ORDER BY cn.data_insercao DESC
        LIMIT 2
    """
    resultados = executar_comando("GET", comando)

    if len(resultados) < 2:
        return  # Não tem dados suficientes

    isp_hoje = resultados[0][0]
    isp_ontem = resultados[1][0]

    if isp_ontem == 0:
        return  # Evita divisão por zero

    diferenca = ((isp_hoje - isp_ontem) / isp_ontem) * 100

    if diferenca > 0:
        titulo = "Cuidado"
        conteudo = f"Hoje você está com um ISP {diferenca:.1f}% superior ao de ontem."
    else:
        titulo = "Parabéns"
        conteudo = f"Hoje você está com um ISP {abs(diferenca):.1f}% inferior ao de ontem."

    # Insere a notificação
    comando_insert = f"""
        INSERT INTO notificacoes (Titulo, Conteudo, fk_consumos_normalizados_id)
        VALUES ('{titulo}', '{conteudo}', {id_consumo_normalizado})
    """
    executar_comando("POST", comando_insert)




def notificar_consumo_bruto(user_id, id_consumo_bruto_atual):
    comando_consumos = f"""
        SELECT cb.ID, cb.Agua, cb.Energia, 
               cb.residuos_reciclaveis + cb.residuos_nao_reciclaveis AS Residuos,
               cb.data_insercao
        FROM consumos_brutos cb
        JOIN relatorios r ON cb.fk_relatorio = r.ID
        WHERE r.fk_id_usuario = {user_id}
        ORDER BY cb.data_insercao DESC
        LIMIT 2
    """
    consumos = executar_comando("GET", comando_consumos)

    if len(consumos) < 2:
        return
    
    consumo_hoje = consumos[0]
    consumo_ontem = consumos[1]

    def soma_transporte(fk_consumo_bruto_id):
        comando_transporte = f"""
            SELECT COALESCE(SUM(Distancia), 0) FROM transporte
            WHERE fk_consumos_brutos_id = {fk_consumo_bruto_id}
        """
        resultado = executar_comando("GET", comando_transporte)
        return resultado[0][0] if resultado else 0

    transporte_hoje = soma_transporte(consumo_hoje['ID'])
    transporte_ontem = soma_transporte(consumo_ontem['ID'])

    tipos = ["água", "energia", "resíduos", "transporte"]
    valores_hoje = [consumo_hoje['Agua'], consumo_hoje['Energia'], consumo_hoje['Residuos'], transporte_hoje]
    valores_ontem = [consumo_ontem['Agua'], consumo_ontem['Energia'], consumo_ontem['Residuos'], transporte_ontem]

    diferencas = []

    for i in range(4):
        if valores_ontem[i] == 0 or valores_ontem[i] is None:
            continue

        diff = ((valores_hoje[i] - valores_ontem[i]) / valores_ontem[i]) * 100
        if diff > 0:
            diferencas.append(f"{diff:.1f}% a mais de {tipos[i]}")
        else:
            diferencas.append(f"{abs(diff):.1f}% a menos de {tipos[i]}")

    if not diferencas:
        return

    titulo = "Resumo do consumo diário"
    conteudo = "Você consumiu " + ", ".join(diferencas) + "."

    comando_insert = f"""
        INSERT INTO notificacoes (Titulo, Conteudo, fk_consumos_brutos_id)
        VALUES ('{titulo}', '{conteudo}', {id_consumo_bruto_atual})
    """
    executar_comando("POST", comando_insert)

def apagar_notificacoes_por_usuario_e_data(user_id, data_consumo):
    # Consulta o ID do relatório do usuário na data informada
    comando_rel = f"""
        SELECT ID FROM relatorios
        WHERE fk_id_usuario = {user_id} AND '{data_consumo}' BETWEEN Data_inicio AND Data_fim
        LIMIT 1
    """
    resultado = executar_comando("GET", comando_rel)
    if not resultado:
        return

    rel_id = resultado[0][0]

    # Apaga notificações ligadas a consumos normalizados
    comando_del_norm = f"""
        DELETE n FROM notificacoes n
        JOIN consumos_normalizados cn ON n.fk_consumos_normalizados_id = cn.ID
        WHERE cn.fk_relatorio = {rel_id}
    """

    # Apaga notificações ligadas a consumos brutos
    comando_del_bruto = f"""
        DELETE n FROM notificacoes n
        JOIN consumos_brutos cb ON n.fk_consumos_brutos_id = cb.ID
        WHERE cb.fk_relatorio = {rel_id}
    """

    executar_comando("POST", comando_del_norm)
    executar_comando("POST", comando_del_bruto)

def apagar_notificacoes_por_relatorio(rel_id):
    # Apaga notificações ligadas a consumos normalizados
    comando_del_norm = f"""
        DELETE n FROM notificacoes n
        JOIN consumos_normalizados cn ON n.fk_consumos_normalizados_id = cn.ID
        WHERE cn.fk_relatorio = {rel_id}
    """

    # Apaga notificações ligadas a consumos brutos
    comando_del_bruto = f"""
        DELETE n FROM notificacoes n
        JOIN consumos_brutos cb ON n.fk_consumos_brutos_id = cb.ID
        WHERE cb.fk_relatorio = {rel_id}
    """

    executar_comando("POST", comando_del_norm)
    executar_comando("POST", comando_del_bruto)

def atualizar_notificacoes_por_relatorio(rel_id):
    # Apaga notificações antigas relacionadas ao relatório
    apagar_notificacoes_por_relatorio(rel_id)

    # --- Atualiza notificações de consumo bruto ---
    comando_consumos = f"""
        SELECT 
            ID, Agua, Energia, residuos_reciclaveis + residuos_nao_reciclaveis AS Residuos, data_insercao
        FROM consumos_brutos
        WHERE fk_relatorio = {rel_id}
        ORDER BY data_insercao DESC
        LIMIT 2;
    """
    consumos = executar_comando("GET", comando_consumos)

    if len(consumos) >= 2:
        consumo_hoje = consumos[0]
        consumo_ontem = consumos[1]

        def soma_transporte(fk_consumo_bruto_id):
            comando_transporte = f"""
                SELECT COALESCE(SUM(Distancia), 0) FROM transporte
                WHERE fk_consumos_brutos_id = {fk_consumo_bruto_id}
            """
            resultado = executar_comando("GET", comando_transporte)
            return resultado[0][0] if resultado else 0

        transporte_hoje = soma_transporte(consumo_hoje[0])
        transporte_ontem = soma_transporte(consumo_ontem[0])

        tipos = ["água", "energia", "resíduos", "transporte"]
        valores_hoje = [consumo_hoje[1], consumo_hoje[2], consumo_hoje[3], transporte_hoje]
        valores_ontem = [consumo_ontem[1], consumo_ontem[2], consumo_ontem[3], transporte_ontem]

        diferencas = []

        for i in range(4):
            if valores_ontem[i] == 0 or valores_ontem[i] is None:
                continue
            diff = ((valores_hoje[i] - valores_ontem[i]) / valores_ontem[i]) * 100
            if diff > 0:
                diferencas.append(f"{diff:.1f}% a mais de {tipos[i]}")
            else:
                diferencas.append(f"{abs(diff):.1f}% a menos de {tipos[i]}")

        if diferencas:
            titulo = "Resumo do consumo diário"
            conteudo = "Você consumiu " + ", ".join(diferencas) + "."

            comando_insert = f"""
                INSERT INTO notificacoes (Titulo, Conteudo, fk_consumos_brutos_id)
                VALUES ('{titulo}', '{conteudo}', {consumo_hoje[0]})
            """
            executar_comando("POST", comando_insert)

    # --- Atualiza notificações de consumo normalizado / ISP ---
    comando_norm = f"""
        SELECT ID, ISP 
        FROM consumos_normalizados 
        WHERE fk_relatorio = {rel_id} AND ISP IS NOT NULL
        ORDER BY data_insercao DESC
        LIMIT 2
    """
    resultados = executar_comando("GET", comando_norm)

    if len(resultados) >= 2:
        id_consumo_atual, isp_hoje = resultados[0]
        _, isp_ontem = resultados[1]

        if isp_ontem != 0:
            diferenca = ((isp_hoje - isp_ontem) / isp_ontem) * 100
            if diferenca > 0:
                titulo = "Parabéns"
                conteudo = f"Hoje você está com um ISP {diferenca:.1f}% superior ao de ontem."
            else:
                titulo = "Cuidado"
                conteudo = f"Hoje você está com um ISP {abs(diferenca):.1f}% inferior ao de ontem."

            comando_insert = f"""
                INSERT INTO notificacoes (Titulo, Conteudo, fk_consumos_normalizados_id)
                VALUES ('{titulo}', '{conteudo}', {id_consumo_atual})
            """
            executar_comando("POST", comando_insert)

