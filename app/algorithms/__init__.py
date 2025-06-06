from .normalizacao import Statistics
from .report_builder import DailyReportBuilder
from .graph_generator import radar_graph, bar_graph, sector_graph, polyline_graph
from .cryptography import Crypt
import ast
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
matrix_list = ast.literal_eval(os.getenv("ENCRYPTION_MATRIX"))
matrix = np.array(matrix_list)
Crypt(matrix)