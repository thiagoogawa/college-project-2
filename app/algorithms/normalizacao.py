class Statistics:
    # 1. Valores padrão de consumo para normalização (mínimo e máximo) por categoria
    DEFAULTS = {
        "water": (6.0, 135.0), # Litro
        "energy": (1.2, 4.0), # kWh
        "transport": (0.0, 5.0), # kg de CO2
        "non_recyclabe_residue": (0.15, 0.6), # kg
        "recyclabe_residue": (0.1, 0.3) # kg
    }

    # 2. Fatores de emissão de CO2 (em kg/km) para cada tipo de transporte
    TRANSPORTE_CO2 = {
        "bicicleta": 0.0,   # Bicicleta não emite CO2
        "onibus": 0.1,      # Emissão média do ônibus por km
        "carro": 0.25,      # Emissão média de um carro por km
        "moto": 0.15,       # Emissão média de uma moto por km
        "metro": 0.08       # Emissão média do metrô por km
    }

    @staticmethod
    def clamp(n, smallest, largest):
        """
        Garante que o valor `n` esteja entre `smallest` e `largest`.
        Retorna o valor limitado.
        """
        return max(smallest, min(n, largest))

    @classmethod
    def normalize(cls, _type, value):
        """
        Normaliza o valor com base nos limites definidos em `DEFAULTS`.
        O valor é primeiro limitado ao intervalo permitido, depois normalizado entre 0 e 1.
        """
        if _type in cls.DEFAULTS:
            low, high = cls.DEFAULTS[_type]
            value = cls.clamp(value, low, high)
            return (float(value) - low) / (high - low)

    @staticmethod
    def recyclabe_percentual(recyclabe, non_recyclabe):
        """
        Calcula a proporção de resíduos recicláveis sobre o total de resíduos gerados.
        """
        return recyclabe / (recyclabe + non_recyclabe)

    @staticmethod
    def calculate_isp(water, energy, transport, residue):
        """
        Calcula o Índice de Sustentabilidade Parcial (ISP) com base em ponderações específicas:
        - Água: 20%
        - Energia: 30%
        - Transporte: 35%
        - Resíduos: 15%
        Quanto menor o consumo, maior o ISP.
        """
        return 1 - (water * 0.2 + energy * 0.3 + transport * 0.35 + residue * 0.15)

    @staticmethod
    def classificar_sustentabilidade(indice):
        """
        Classifica o nível de sustentabilidade com base no valor do ISP
        """
        if indice > 0.0 and indice <= 0.25:
            return "CRÍTICO"
        elif indice > 0.25 and indice <= 0.50:
            return "ALERTA"
        elif indice > 0.50 and indice <= 0.70:
            return "ACEITÁVEL"
        else:
            return "IDEAL"

    @classmethod
    def calcular_emissao_co2(cls, tipo, distancia):
        """
        Calcula a emissão de CO2 com base no tipo de transporte e na distância percorrida:
        - Valida o tipo de transporte.
        - Converte a distância para número.
        - Retorna a multiplicação do fator pelo valor da distância.
        """
        # Garante que o tipo esteja em letras minúsculas
        tipo = tipo.lower()

        # Busca o fator de emissão de CO2 para o tipo informado
        fator = cls.TRANSPORTE_CO2.get(tipo)

        # Caso o tipo não seja conhecido, lança erro
        if fator is None:
            raise ValueError(f"Tipo de transporte inválido: {tipo}")

        # Tenta converter a distância para float
        try:
            distancia = float(distancia)
        except ValueError:
            raise ValueError("Distância inválida")

        # Retorna o cálculo da emissão
        return fator * distancia
