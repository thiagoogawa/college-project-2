//Retorma sustentabilidade
// Função para carregar os dados do usuário
function carregarDadosUsuario() {
  const nomeUsuario = localStorage.getItem('userName');
  const usuarioId = localStorage.getItem('userId');
  const sustentabilidade = localStorage.getItem('sustentabilidade');

  if (!nomeUsuario || !usuarioId || !sustentabilidade) {
    alert("Dados do usuário não encontrados no localStorage.");
    return;
  }

  // Exibindo o nome do usuário
  document.querySelector('.nome-usuario').textContent = nomeUsuario;

  // Exibindo diretamente a sustentabilidade do localStorage
  document.querySelector('.classificacao-usuario').textContent = sustentabilidade;
}

// Carregar os dados quando a página for carregada
window.onload = carregarDadosUsuario;


//------------------------------------------------------------------------------------------------------
//carregar consumos de acordo com data:

// Função para pegar o ID do usuário e a data do input
function obterDadosParaEnvio() {
  let userId = localStorage.getItem('userId');  // Pegando o ID do usuário armazenado no localStorage
  let dataReferencia = document.getElementById("date-selector").value;  // Pegando a data do input

  if (!userId || !dataReferencia) {
    alert("Por favor, forneça o ID do usuário e a data.");
    return;
  }

  return { userId, dataReferencia };
}

// Função para enviar a requisição POST com ID do usuário e data
function enviarDadosParaAPI() {
  console.log("Botão clicado!");
  const dados = obterDadosParaEnvio();
  if (!dados) return;

  // Exemplo de como fazer a requisição POST usando Fetch
  fetch('/users/retornaDadosBrutosPorData', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'id': dados.userId,  // Passando o ID do usuário nos headers
    },
    body: JSON.stringify({
      data: dados.dataReferencia  // Passando a data no corpo da requisição
    })
  })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      mostrarDadosNoCard(data);  // Chama a função para mostrar os dados no card
    })
    .catch(error => {
      console.error('Erro ao enviar dados:', error);
    });
}

// Função para exibir os dados no card
function mostrarDadosNoCard(dados) {
  const cardConteudo = document.getElementById("conteudo-card");

  if (dados.error) {
    cardConteudo.innerHTML = `<p>${dados.error}</p>`;
    return;
  }

  // Montando os dados para mostrar no card
  let html = `<ul>`;
  dados.forEach(dado => {
    html += `
    <li><strong>Consumo de Água:</strong> ${dado.agua} litros</li>
    <li><strong>Consumo de Energia:</strong> ${dado.energia} kWh</li>
    <li><strong>Resíduos Não Recicláveis:</strong> ${dado.residuos_nao_reciclaveis} kg</li>
    <li><strong>Resíduos Recicláveis:</strong> ${dado.residuos_reciclaveis} kg</li>
    <li><strong>Veículo:</strong> ${dado.tipo_veiculo}</li>
    <li><strong>Distância:</strong> ${dado.distancia} km</li>
  `;
  });
  html += `</ul>`;

  // Inserindo os dados no card
  cardConteudo.innerHTML = html;
}

// Chamando a função para quando o botão for clicado
document.getElementById("gerar-dados-btn").addEventListener("click", enviarDadosParaAPI);
