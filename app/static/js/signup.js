document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-cadastro");

  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // impede o comportamento padrão de submit

    const nome = document.getElementById("nome").value;
    const cpf = document.getElementById("cpf").value;
    const dataNascimento = document.getElementById("dataNascimento").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("password").value;



    // Validacao (a senha nao pode conter esapcos)

      if (/\s/.test(senha)) {
        alert("A senha não pode conter espaços.");
        return;
    };

        // Validacao (email deve conter um (.) apos o (@) )

    if (!email.includes(".")) {
      alert("O email precisa conter um (.) após o @. Exemplo: usuario@dominio.com ");
      return;
    };




    const dados = {
      nome: nome,
      cpf: cpf,
      data_nascimento: dataNascimento,
      email: email,
      senha: senha,
    };

    try {
      const response = await fetch("/users/cadastrarUsuario", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(dados),
      });

      const resultado = await response.json();

      if (response.ok) {
        alert("Cadastro realizado com sucesso!");
        window.location.href = "/users/logar_user"; // redirecionar para login
      } else {
        alert(`Erro: ${resultado.Erro || resultado.Status}`);
      }
    } catch (error) {
      console.error("Erro ao cadastrar:", error);
      alert("Erro ao tentar se cadastrar. Tente novamente.");
    }
  });
});