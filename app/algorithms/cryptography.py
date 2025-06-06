# Importa a biblioteca numpy para operações com matrizes e arrays
import numpy as np
# Importa a biblioteca sympy para operações matemáticas simbólicas
import sympy as sp
# Importa o módulo string que contém constantes de caracteres úteis
import string

# Define a classe Crypt para realizar criptografia utilizando matrizes
class Crypt:
    # Define o conjunto de caracteres permitidos: letras, números, pontuação e espaço (usado para "padding")
    charset = list(string.ascii_letters + string.digits + string.punctuation + " ")
    # Define o módulo como o tamanho do conjunto de caracteres
    mod = len(charset)
    # Define a instancia da classe
    _instance = None
    # Define se a instância já foi inicializada
    _initialized = False

    # Método que retorna sempre a mesma instância da classe
    def __new__(cls, enc_matrix=None):
        if cls._instance is None:
            # Só cria uma nova instância se ainda não existir
            if enc_matrix is None:
                # Matriz de criptografia é obrigatória na primeira instanciação
                raise Exception("Matriz de criptografia é obrigatória na primeira instanciação")
            cls._instance = super(Crypt, cls).__new__(cls)
        return cls._instance

    # Método construtor que inicializa a classe com uma matriz de criptografia
    def __init__(self, enc_matrix=None):
        # Pula a inicialização se já foi inicializada
        if Crypt._initialized:
            return
            
        # Garante que a matriz foi fornecida na primeira inicialização
        if enc_matrix is None:
            raise Exception("Matriz de criptografia é obrigatória na primeira instanciação")
            
        # Converte a matriz de entrada para um array numpy
        self.enc_matrix = np.array(enc_matrix)

        # Verifica se a matriz é quadrada
        if self.enc_matrix.shape[0] != self.enc_matrix.shape[1]:
            # Levanta uma exceção se a matriz não for válida
            raise Exception(f"Matriz inválida: não é quadrada")

        # Verifica se a matriz é válida para criptografia (possui inversa no módulo especificado)
        if not self._check_validity(self.enc_matrix):
            # Levanta uma exceção se a matriz não for válida
            raise Exception(f"Matriz inválida: não possui inversa no módulo {self.mod}")
        
        # Armazena o tamanho da matriz
        self.matrix_size = self.enc_matrix.shape[0]
        
        # Marca a instância como inicializada
        Crypt._initialized = True

    # Método para determinar se uma matriz é válida
    def _check_validity(self, enc_matrix):
        # Cria um objeto Matrix do SymPy
        m = sp.Matrix(enc_matrix)

        # Calcula e armazena o determinante
        self.det = m.det()

        # Retorna se o determinante e o módulo são coprimos (não possuem fator comum)
        return np.gcd(self.det % self.mod, self.mod) == 1

    # Método para calcular a matriz inversa em aritmética modular
    def _invert_matrix(self, enc_matrix):
        # Calcula o inverso modular do determinante
        det_inv = pow(self.det, -1, self.mod)

        # Converte a matriz numpy para uma matriz SymPy
        m = sp.Matrix(enc_matrix)

        # Calcula a matriz adjunta (transposta da matriz de cofatores) em módulo
        adj = m.adjugate() % self.mod

        # Calcula a inversa como o produto do inverso do determinante pela adjunta
        inv = (det_inv * adj) % self.mod

        # Converte de volta para um array numpy
        return np.array(inv.tolist())

    # Método para preencher a mensagem para que seu tamanho seja múltiplo da dimensão da matriz
    def _pad_message(self, message, dimension):
        # Calcula o tamanho necessário para que o comprimento seja múltiplo da dimensão
        remainder = len(message) % dimension
        pad_qty = (dimension - remainder) if remainder != 0 else 0

        # Adiciona espaços ao final da mensagem para completar
        return message + (" " * pad_qty)

    # Método para remover o preenchimento adicionado à mensagem
    def _unpad_message(self, message):
        # Remove espaços em branco do final da mensagem
        return message.strip()

    # Método para converter caracteres em seus índices numéricos no charset
    def _to_num(self, message):
        # Para cada caractere na mensagem, retorna seu índice no charset
        return [self.charset.index(n) for n in list(message)]

    # Método para converter índices numéricos de volta para caracteres
    def _to_string(self, nums):
        # Para cada número, retorna o caractere correspondente no charset e junta em uma string
        return "".join([self.charset[n] for n in nums])

    # Método para criptografar uma mensagem
    def encrypt(self, msg):
        # Verifica se todos os caracteres da mensagem estão no charset
        if not all(c in self.charset for c in msg):
            # Levanta uma exceção se houver caracteres não reconhecidos
            raise Exception("Mensagem inválida: caracteres desconhecidos")

        # Converte a mensagem para números e adiciona o preenchimento necessário
        msg = self._to_num(self._pad_message(msg, self.matrix_size))

        # Reorganiza a mensagem em forma de matriz (transposta para organizar por colunas)
        msg_matrix = np.array(msg).reshape(-1, self.matrix_size).T

        # Multiplica a matriz de criptografia pela matriz da mensagem e aplica o módulo
        enc_msg_matrix = np.matmul(self.enc_matrix, msg_matrix) % self.mod

        # Converte a matriz resultante de volta para uma string, reorganizando-a primeiro
        return self._to_string(enc_msg_matrix.T.reshape(-1))

    # Método para descriptografar uma mensagem
    def decrypt(self, enc_msg):
        # Converte a mensagem criptografada em números e reorganiza em matriz
        enc_msg_matrix = np.array(self._to_num(enc_msg)).reshape(-1, self.matrix_size).T

        # Calcula a matriz inversa da matriz de criptografia
        inv_matrix = self._invert_matrix(self.enc_matrix)

        # Multiplica a matriz inversa pela matriz da mensagem criptografada e aplica o módulo
        decrypted = np.matmul(inv_matrix, enc_msg_matrix) % self.mod

        # Converte a matriz resultante de volta para uma string e remove o preenchimento
        return self._unpad_message(self._to_string(decrypted.T.reshape(-1)))

matrix = [[2, 3],
          [1, 2]]

a = Crypt(matrix)

msg = "123ab  x"

print(x:=a.encrypt(msg))
print(a.decrypt(x))
