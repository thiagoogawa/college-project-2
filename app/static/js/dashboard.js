document.addEventListener('DOMContentLoaded', async () => {



  // Funcao para impedir valores negativos

  function validar_inputs(){
    const todos_inputs = document.querySelectorAll("input[type='number']");
    todos_inputs.forEach(input => {
      input.addEventListener("input", function (){

        const valor = this.value;
        const valido = /^[0-9]*[.,]?[0-9]*$/;
        
        if (!valido.test(valor) || parseFloat(this.value) < 0) {
          alert("Digite apenas numeros positivos. Use (.) ou (,) para decimais.");
          this.value = 0;
        }
      });
    });
  }

  validar_inputs();






    // /*
    //   Permite a remoção dos itens de transporte da lista ao clicar no botão X
    // */
    // function load_remove_buttons() {
    //   remove_buttons = document.querySelectorAll(".remove-transport-btn");
  
    //   if(remove_buttons){
    //     remove_buttons.forEach((btn) => {
    //       btn.addEventListener('click', (evt) => {
    //         let e = btn.closest('.transport-entry');
    //         if(e) e.remove();
    //       });
    //     });
    //   }
    // }
    // load_remove_buttons();
    // ///----///
  
    /*
      Permite a adição de mais caixas coleta de transporte. Não permite a adição de mais que a quantidade de meios disponíveis.
    */
    const add_transport_button = document.querySelector("#add-transport-button");
    const transport_container = document.querySelector("#transport-inputs-container")
  
    const transportOptions = ['bicicleta', 'onibus', 'carro', 'moto', 'metro'];
  
    if(add_transport_button){
      add_transport_button.addEventListener('click', (evt) => {
        if(transport_container.childElementCount > transportOptions.length-1) return;
        const entry = document.createElement('div');
        entry.classList.add('transport-input-row');
  
        const selectHTML = `
          <select id="transport-input" class="input-field half-width transport-select">
            ${transportOptions.map(opt => `<option value="${opt}">${opt.charAt(0).toUpperCase() + opt.slice(1)}</option>`).join('')}
          </select>
        `;
  
        const inputHTML = `
         <input type="number"
                id="transport-distance"
                class="input-field half-width transport-input"
                placeholder="Distância (km)"
                min="0"
                step="0.1"
                value="0" 
                /></div>`;
  
        entry.innerHTML = `${selectHTML}${inputHTML}`;
        transport_container.appendChild(entry);


        const newinput = entry.querySelector('.transport-input');
        newinput.addEventListener("input", function (){
          const valor = this.value;
          const valido = /^[0-9]*[.,]?[0-9]*$/;


          if (!valido.test(valor) || parseFloat(this.value) < 0) {
            alert("Digite apenas numeros positivos. Use (.) ou (,) para decimais.");
            this.value = 0;
          }
        });


        // load_remove_buttons();
      });
    }
    ///----///
  
    /*
      Envia os dados para o servidor e atualiza a página
    */
    async function upload_data (data) {
      const url = location.protocol + '//' + location.host + '/users/cadastrarConsumo';
      
      try{
        const res = await fetch(url, {
          method: "POST",
          body: JSON.stringify(data),
          headers: {"Content-Type": "application/json"}
        });
  
        if(!res.ok) {
          const error = await res.json();
          alert(error.erro)
        }
        else window.location.reload(true);
      }
      catch(e){
        console.log(e);
      }
    }
  
    const register_btn = document.querySelector(".update-button");
  
    if(register_btn){
      register_btn.addEventListener('click', async (e) => {
        e.preventDefault();
  
        const water = document.querySelector("#water-input");
        const energy = document.querySelector("#energy-input");
        const r_residue = document.querySelector("#recyclable-waste-input");
        const nr_residue = document.querySelector("#waste-input");
        const transports = {};

        // Validacao antes do envio


        const campos = [water, energy, r_residue, nr_residue];
        let invalido = false;

        campos.forEach(campo => {
          if (parseFloat(campo.value) < 0 || isNaN(parseFloat(campo.value))) {
            invalido = true;
            campo.value = 0;
          }
        });

        document.querySelectorAll(".transport-input").forEach(input => {
          if (parseFloat(input.value) < 0 || isNaN(parseFloat(input.value))){
            invalido = true;
            input.value = 0;
          }
        });

        if (invalido){
          alert("Valores inválidos.");
          return;
        }
  
        document.querySelectorAll(".transport-input-row").forEach((entry) => {
          const select = entry.querySelector('.transport-select');
          const input = entry.querySelector('.transport-input');
    
          const tipo = select.value;
          const distancia = parseFloat(input.value) || 0;
    
          if (tipo && distancia > 0.0) transports[tipo] = distancia;
        });
  
        data = {
          'agua': water.value,
          'energia': energy.value,
          'residuos_nao_reciclaveis': nr_residue.value,
          'residuos_reciclaveis': r_residue.value,
          'data': (new Date(Date.now())).toISOString().slice(0,10),
          'transportes': transports
        };
  
        upload_data(data);
      });
    }
  
  });
