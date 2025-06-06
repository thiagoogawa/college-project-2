document.querySelectorAll('.direciona-relatoriosDiarios').forEach(button => {
  button.addEventListener('click', (event) => {
    const idRelatorio = event.target.getAttribute('data-id');

    if (idRelatorio) {
      window.location.href = `/users/relatorio/${idRelatorio}`;
    } else {
      alert("Erro ao obter usuário ou relatório!");
    }
  });
});
  