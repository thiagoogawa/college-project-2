async function enviarEmail(event) {
  event.preventDefault(); // Impede o envio do formulário

  const email_usuario = document.getElementById('email').value; // Pega o valor do email
  if (!email_usuario) {
    alert("Por favor, preencha o email!");
    return;
  }

  try {
    // Faz a requisição para o backend, método GET (ajuste se necessário)
    const response = await fetch(`/users/enviarToken/${encodeURIComponent(email_usuario)}`);

    if (response.ok) {
      // Sucesso no backend
      alert("Token enviado para o E-mail.");
      // Recarrega a página
      window.location.reload(); 
      
    } else {
      // Caso o backend retorne erro
      alert("Erro ao enviar o token. Tente novamente.");
      window.location.reload(); 
    }
  } catch (error) {
    // Erro de rede ou outro erro
    alert("Erro na conexão. Tente novamente.");
  }
}
