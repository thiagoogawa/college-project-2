document.addEventListener('DOMContentLoaded', async () => {
  const URL_dashboard = '/users/dashboardForm';
  const URL_login = '/users/login';
  const login_form = document.querySelector('#login-form');

  if (login_form) {
    login_form.addEventListener('submit', async function (event) {
      event.preventDefault();  // Impede o comportamento padrão do formulário

      const email = document.getElementById("email").value;
      const senha = document.getElementById("password").value;

      // Validacao (senha nao pode conter espacos)


      
      if (/\s/.test(senha)) {
        alert("A senha não pode conter espaços.");
        return;
      }




      const body = {
        "email": email,
        "senha": senha
      };

      try {
        const response = await fetch(URL_login, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(body)
        });

        if (response.ok) {
          alert('Login realizado com sucesso!');
          window.location.href = URL_dashboard;
        } else {
          alert('Login falhou. Verifique seu e-mail e senha.');
        }
      } catch (error) {
        console.error("Erro ao realizar login:", error);
        alert('Ocorreu um erro ao tentar fazer login. Tente novamente.');
      }
    });
  }
});
