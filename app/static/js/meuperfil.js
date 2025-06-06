
document.getElementById("perfil-link").addEventListener("click", function (e) {
  e.preventDefault(); // Evita o comportamento padrão do link
  const userId = localStorage.getItem('userId');  // Pega o id do usuário do localStorage
  
  if (userId) {
      // Se o id do usuário for encontrado, construa o link dinâmico
      const perfilLink = `/users/perfil?id=${userId}`;
      window.location.href = perfilLink;  // Redireciona para a página de perfil
  } else {
      // Se o id não for encontrado, pode redirecionar para a página de login
      alert("Usuário não encontrado. Você precisa estar logado.");
      window.location.href = '/login';  // Redireciona para o login, por exemplo
  }
});

//-----------------------------------------------------------------------------------------

//mostra na tela as infos do usuario
function carregarDadosUsuario() {
  const nomeUsuario = localStorage.getItem('user-name');
  const usuarioId = localStorage.getItem('userId');
  const sustentabilidade = localStorage.getItem('sustentabilidade');
  const dataCadastro = localStorage.getItem('data_cadastro');

  if (!nomeUsuario || !usuarioId || !sustentabilidade || !dataCadastro) {
    alert("Dados do usuário não encontrados no localStorage.");
    return;
  }

  // Exibindo o nome do usuário
  document.querySelector('.user-name').textContent = nomeUsuario;

  // Formatando a data para DD/MM/YYYY
  const data = new Date(dataCadastro);
  const dataFormatada = data.toLocaleDateString('pt-BR');

  // Pegando os elementos com a classe .user-info
  const userInfoElements = document.querySelectorAll('.user-info');
  if (userInfoElements.length >= 2) {
    userInfoElements[0].textContent = `Primeiro acesso em: ${dataFormatada}`;
    userInfoElements[1].textContent = `Classificação Sustentável: ${sustentabilidade}`;
  }
}

