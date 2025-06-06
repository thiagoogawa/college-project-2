import json
from typing import List
from .normalizacao import Statistics

class DailyReportBuilder:
    def __init__(self, report=None):
        """
        Inicializa o construtor de relatórios.
        Se um relatório em formato JSON for fornecido, ele será carregado.
        Caso contrário, um novo relatório vazio será criado com as chaves padrão.
        """
        if report is None:
            self.report = {
                "actions": [],
                "raw": {},
                "normalized": {},
                "vehicle": {}
            }
        else:
            self.report = {
                "sustainability": report['ISP'],
                "user": report['fk_id_usuario']
            }

    def set_sustainability(self, sustainability: int = None):
        """
        Define o índice de sustentabilidade parcial (ISP) do relatório.
        Se não for fornecido, calcula automaticamente usando os dados normalizados (deve ser chamado por último neste caso).
        """
        if sustainability is None:
            self.report['sustainability'] = round(Statistics.calculate_isp(
                float(self.report["normalized"]["water"]),
                float(self.report["normalized"]["energy"]),
                float(self.report["normalized"]["transport"]),
                float(self.report["normalized"]["non_recyclabe_residue"])
            ), 2)
        else:
            self.report['sustainability'] = sustainability
        return self

    def set_date(self, date: str):
        """
        Define a data do relatório.
        """
        self.report['date'] = date
        return self

    def set_user(self, user: str):
        """
        Define o ID do usuário dono do relatório.
        """
        self.report['user'] = user
        return self

    def add_consumption(self, **kwargs):
        """
        Adiciona os dados brutos e normalizados de consumo.
        Os dados normalizados são calculados com base nos valores brutos usando a classe Statistics.
        """
        for key, value in kwargs.items():
            self.report["raw"][f"{key}"] = f"{value}"
            
            if f"{key}" != "recyclabe_residue":
                self.report["normalized"][f"{key}"] = round(
                    Statistics.normalize(f"{key}", float(value)), 2)
        return self

    def add_vehicle(self, v_type, distance):
        """
        Adiciona informações de transporte ao relatório.
        `v_type` define o tipo de veículo, e `distance` a distância percorrida.
        """
        self.report["vehicle"][v_type] = f"{distance:.2f}"
        return self

    def add_actions(self, actions):
        """
        Adiciona ações (notificações, alertas, etc.) ao relatório.
        Recebe uma lista de ações a serem inseridas.
        """
        for action in actions:
            self.report['actions'].append(action)
        return self

    def build(self):
        """
        Constrói e retorna o relatório final em formato JSON.
        """
        json_string = json.dumps(self.report)
        return json_string
