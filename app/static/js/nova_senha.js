
document.getElementById('novaSenhaForm').addEventListener('submit', async function(event) {
  event.preventDefault(); // Evita que o formulário seja enviado normalmente

  const email = document.getElementById('email').value;
  const token = document.getElementById('token').value;
  const novaSenha = document.getElementById('nova_senha').value;

  const dados = {
    email: email,
    token: token,
    novasenha: novaSenha
  };

  try {
    const resposta = await fetch('/users/resetarSenha', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dados)
    });

    if (resposta.ok) {
      // Sucesso
      alert('Senha alterada com sucesso!');
      window.location.href = '/users/logar_user'; // Redireciona pro login
    } else {
      // Erro
      alert('Erro ao alterar a senha!');
    }
  } catch (erro) {
    console.error('Erro:', erro);
    alert('Erro inesperado!');
  }
});

