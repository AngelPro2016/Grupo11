document.addEventListener('DOMContentLoaded', function () {
    const tipoFacturaField = document.getElementById('id_tipo_factura');
    const clienteField = document.getElementById('id_cliente');

    function toggleFields() {
        if (tipoFacturaField.value === 'CONSUMIDOR_FINAL') {
            clienteField.parentElement.style.display = 'none';  // Ocultar cliente
        } else {
            clienteField.parentElement.style.display = '';  // Mostrar cliente
        }
    }

    toggleFields();
    tipoFacturaField.addEventListener('change', toggleFields);
});
