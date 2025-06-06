document.addEventListener('DOMContentLoaded', () => {

  /*
    Redireciona o usuário para a rota com a data escolhida ao clicar no botão Carregar Dados
  */
  const load_data_btn = document.querySelector("#load-date-data");
  const date_selection = document.querySelector("#date-selector");

  if(load_data_btn){
    load_data_btn.addEventListener('click', (_) => {
      if(date_selection) {
        if(!isNaN(new Date(date_selection.value))){
          window.location.href = location.protocol + '//' + location.host + location.pathname + '?date=' + date_selection.value;
        }
      }
    })
  }

  /*
    Permite a remoção dos itens de transporte da lista ao clicar no botão X
  */
  function load_remove_buttons() {
    remove_buttons = document.querySelectorAll(".remove-transport-btn");

    if(remove_buttons){
      remove_buttons.forEach((btn) => {
        btn.addEventListener('click', (_) => {
          let e = btn.closest('.transport-entry');
          if(e) e.remove();
        });
      });
    }
  }
  load_remove_buttons();

  /*
    Permite a adição de mais caixas coleta de transporte. Não permite a adição de mais que a quantidade de meios disponíveis.
  */
  const add_transport_button = document.querySelector(".add-transport-button");
  const transport_container = document.querySelector(".transport-edit-container")

  const transportOptions = ['bicicleta', 'onibus', 'carro', 'moto', 'metro'];

  if(add_transport_button){
    add_transport_button.addEventListener('click', (evt) => {
      if(transport_container.childElementCount > transportOptions.length) return;
      const entry = document.createElement('div');
      entry.classList.add('transport-entry');

      const selectHTML = `
        <select class="input-field transport-select">
          ${transportOptions.map(opt => `<option value="${opt}">${opt.charAt(0).toUpperCase() + opt.slice(1)}</option>`).join('')}
        </select>
      `;

      const inputHTML = `
        <input type="number" step="0.1" min="0" class="input-field transport-input" placeholder="km" value="0" >
        <button class="remove-transport-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      `;

      entry.innerHTML = `<div class="transport-row">${selectHTML}${inputHTML}</div>`;
      transport_container.insertBefore(entry, add_transport_button);
      load_remove_buttons();
    });
  }

  /*
    Envia os dados para o servidor e atualiza a página
  */
  async function upload_data (data, method) {
    const url = location.protocol + '//' + location.host + location.pathname.slice(0, -1);
    
    try{
      const res = await fetch(url, {
        method: method,
        body: JSON.stringify(data),
        headers: {"Content-Type": "application/json"}
      });

      if(!res.ok) {
        const error = await res.json();
        alert(error.erro)
        throw new Error(res.status);
      }else {
        if (method === "PUT") {
          alert("Dados atualizados com sucesso!");
        }
        if (method === "DELETE") {
          alert("Dados excluídos com sucesso!");
        }
        window.location.reload(true);
      }
    }
    catch(e){
      console.log(e);
    }
  }

  /*
    Coleta os dados do formulário, monta o objeto JSON e envia para o servidor
  */
  const update_btn = document.querySelector(".update-button");

  if(update_btn){
    update_btn.addEventListener('click', (evt) => {
      evt.preventDefault();

      const water = document.querySelector("#water-edit");
      const energy = document.querySelector("#energy-edit");
      const r_residue = document.querySelector("#recyclable-waste-edit");
      const nr_residue = document.querySelector("#waste-edit");
      const urlParams = new URLSearchParams(window.location.search);
      const transports = {};










      function validar_digitos_tempo_real() {
        const inputs = document.querySelectorAll("input[type = 'number']");

        inputs.forEach(input => {
          input.addEventListener("input", function () {
            const valor = this.value;
            const valido = /^[0-9]*[.,]?[0-9]*$/;

            if (!valido.test(valor)) {
              alert("Digite apenas numeros positivos. Use (.) ou (,) para decimais.");
              this.value = 0;
            }
          });
        });
      }


      validar_digitos_tempo_real();

      // validação negativos
      const allInputs = [water, energy, r_residue, nr_residue];
      for (const input of allInputs) {
        if (parseFloat(input.value) < 0) {
          alert("Nenhum campo pode conter valores negativos");
          input.focus();
          return;
        }
        if(isNaN(parseFloat(input.value))){
          alert("Valores inválidos.");
          input.focus();
          return;
        }
      }

      // validação transportes
      let invalid_transportes = false;
      document.querySelectorAll(".transport-entry").forEach((entry) => {
        const select = entry.querySelector('.transport-select');
        const input = entry.querySelector('.transport-input');
        const tipo = select.value;
        const distancia = parseFloat(input.value);

        if (distancia < 0) {
          alert("A distância não pode ser negativa");
          input.focus();
          invalid_transportes = true;
          return;
        }
        if(isNaN(parseFloat(input.value))){
          alert("Valores inválidos.");
          input.focus();
          return;
        }

        if (tipo && distancia > 0.0) transports[tipo] = distancia;
      });

      if (invalid_transportes) return;











      const data = {
        'agua': water.value,
        'energia': energy.value,
        'residuos_nao_reciclaveis': nr_residue.value,
        'residuos_reciclaveis': r_residue.value,
        'data': urlParams.get('date'),
        'transportes': transports
      };

      upload_data(data, "PUT");
    });
  }

  /*
    Coleta os dados do formulário, monta o objeto JSON e envia para o servidor
  */
  const delete_btn = document.querySelector("#remove-date-data");

  if(delete_btn){
    delete_btn.addEventListener('click', (evt) => {
      evt.preventDefault();

      const urlParams = new URLSearchParams(window.location.search);

      const data = {
        'data': urlParams.get('date'),
      };

      upload_data(data, "DELETE");
    });
  }  
});
