import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

# 1. Converte um gráfico matplotlib para string SVG
def to_svg(fig):
    svg_buffer = StringIO()
    fig.savefig(svg_buffer, format="svg")
    svg_string = svg_buffer.getvalue()
    svg_buffer.close()

    svg_lines = svg_string.splitlines()
    svg_cleaned = "\n".join(svg_lines[3:])

    return svg_cleaned

# 2. Classe auxiliar para formatar valores percentuais com unidades
class AutoPct:
    def __init__(self, values, unit):
        # Substitui valores NaN por zeros e armazena os valores
        self.values = [0.0 if np.isnan(v) else float(v) for v in values]
        self.unit = unit

    # Método para formatar o valor da porcentagem com a unidade (ex: "25.0% (50kg)")
    def format_pct(self, pct):
        # Calcula o total dos valores com segurança
        total = sum(self.values)
        
        # Se o total for zero, evita divisão por zero
        if total == 0:
            return f'{pct:.1f}% (0{self.unit})'
            
        percent = pct * total / 100.0

        form_val = f'{percent:.1f}' if percent >= 1 else f'{percent:.2f}'
        return f'{pct:.1f}% ({form_val}{self.unit})'

# 3. Gera um gráfico de setores (pizza)
def sector_graph(label, unit, labels, sizes):
    # Verifica se há dados válidos para gerar o gráfico
    if not sizes or all(np.isnan(s) for s in sizes):
        return ""
    
    # Substitui valores NaN por zeros para evitar erros nas conversões
    cleaned_sizes = [0.0 if np.isnan(s) else float(s) for s in sizes]
    
    # Remove pares de rótulos e valores onde o valor é zero (não serão mostrados na pizza)
    filtered_data = [(label, size) for label, size in zip(labels, cleaned_sizes) if size > 0]
    
    # Se não houver dados válidos após a filtragem (todos valores zerados)
    if not filtered_data:
        return ""
    
    # Descompacta os dados filtrados em duas listas separadas (rótulos e valores)
    filtered_labels, filtered_sizes = zip(*filtered_data) if filtered_data else ([], [])
    
    # Cores para os diferentes setores do gráfico
    colors = ['#a84df2', '#4fc3b4', '#93e647', '#ffa54f', '#f779bc', '#8dffcf']

    # Cria o formatador de porcentagem com os valores já filtrados
    f = AutoPct(filtered_sizes, unit)
    fig, ax = plt.subplots(figsize=(5, 5))

    # Agora usamos os dados filtrados para criar o gráfico de pizza
    ax.pie(filtered_sizes, labels=filtered_labels, colors=colors[:len(filtered_labels)],
           autopct=f.format_pct, shadow=False, startangle=0)
    ax.axis('equal')  # Mantém o gráfico circular
    ax.set_title(label)

    # Converte a figura para formato SVG
    svg = to_svg(fig)
    plt.close(fig)
    return svg

# 4. Gera um gráfico de barras verticais
def bar_graph(label, unit, categories, values):
    # Cria uma figura com tamanho específico (largura=5, altura=4)
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Cria barras com largura maior (0.6) para reduzir o espaço entre elas
    bars = ax.bar(categories, values, color='skyblue', width=0.6)

    # Adiciona linhas de grade horizontais tracejadas com transparência
    ax.grid(axis='y', linestyle='dashed', alpha=0.7)
    ax.set_axisbelow(True)  # Mantém a grade atrás das barras

    # Exibe os valores numéricos no topo de cada barra
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{(int(height))}{unit}',
                ha='center', va='bottom', fontsize=10)

    # Define os valores e rótulos do eixo Y com incrementos de 10
    max_value = max(values)
    ticks = np.arange(0, max_value + 10, 10)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{int(tick)}{unit}' for tick in ticks])

    # Define os valores e rótulos do eixo X
    ax.set_xticks(categories)
    ax.set_xticklabels([str(int(cat)) for cat in categories])

    # Define o título do gráfico
    ax.set_title(label)
    
    # Adiciona margem à esquerda para evitar corte dos rótulos do eixo Y
    fig.subplots_adjust(left=0.15)
    
    # Converte o gráfico para formato SVG e retorna
    svg = to_svg(fig)
    plt.close(fig)
    return svg

# 5. Gera um gráfico de linha com marcadores
def polyline_graph(label, unit, xs, ys):
    # Cria uma figura com tamanho específico
    fig, ax = plt.subplots(figsize=(5, 3))

    # Cria um gráfico de linha com marcadores e linhas tracejadas
    ax.plot(xs, ys, 'o--', linewidth=2, markersize=8)

    # Adiciona linhas de grade com transparência
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    y_min = max(0, min(ys) - max(ys))  # Não permitir valores negativos se os dados forem positivos
    y_max = max(ys) + 0.5
    
    # Define o intervalo dos ticks do eixo Y
    tick_interval = max(1, int((y_max - y_min) / 5))  # Pelo menos 5 ticks no gráfico
    ticks = np.arange(y_min, y_max + tick_interval, tick_interval)
    
    # Define os ticks do eixo Y
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{int(y)}{unit}' for y in ticks])
    ax.set_ylim(y_min, y_max)

    # Define os ticks do eixo X
    ax.set_xticks(xs)
    ax.set_xticklabels([str(int(x)) for x in xs])

    # Define o título do gráfico
    ax.set_title(label)
    
    # Converte o gráfico para formato SVG e retorna
    svg = to_svg(fig)
    plt.close(fig)
    return svg

def radar_graph(values):
    """
    Gera um gráfico radar a partir dos valores fornecidos.
    """
    # Define as etiquetas para cada eixo do gráfico
    spoke_labels = ['Índice', 'Transporte', 'Água', 'Energia', 'Resíduos']
    title = 'Geral'
    
    # Calcula os ângulos para cada eixo, começando de cima (norte, -π/2 ou 90° no sentido horário)
    theta = np.linspace(0, 2*np.pi, len(spoke_labels), endpoint=False)
    
    # Adiciona o primeiro valor novamente no final para fechar o polígono
    values = np.concatenate((values, [values[0]]))
    theta = np.concatenate((theta, [theta[0]]))
    
    # Cria uma figura e um eixo com projeção radar (polar)
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(projection='polar'))
    fig.subplots_adjust(top=0.85, bottom=0.05, left=0.1, right=0.9)
    
    # Define o limite máximo do eixo radial como 1.0 
    ax.set_ylim(0, 1.0)
    
    # Define os círculos concêntricos de referência
    r_ticks = [0.2, 0.4, 0.6, 0.8, 1.0]
    ax.set_rgrids(r_ticks, labels=["20", "40", "60", "80", "100"])
    
    # Define o título do gráfico com posicionamento ajustado
    ax.set_title(title, position=(0.5, 1.1), ha='center')
    
    # Define as etiquetas para cada eixo com conversão de radianos para graus
    ax.set_thetagrids(np.degrees(theta[:-1]), labels=spoke_labels)

    # Define a posição zero (0 graus) no topo (norte)
    ax.set_theta_zero_location('N')
    
    # Ajusta o espaçamento das etiquetas
    ax.tick_params(axis='x', which='major', pad=18)
    
    # Desenha o polígono preenchido com cor azul e transparência
    ax.fill(theta, values, color='blue', alpha=0.25)
    
    # Desenha as linhas do polígono
    ax.plot(theta, values, color='blue', alpha=0.4, linewidth=1)
    
    # Ajusta o layout para evitar sobreposições
    fig.tight_layout()
    
    # Converte a figura para SVG e retorna
    svg = to_svg(fig)
    plt.close(fig)
    return svg
