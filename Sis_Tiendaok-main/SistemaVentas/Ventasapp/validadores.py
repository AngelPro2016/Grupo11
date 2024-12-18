from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator #para hacer validaciones especiales letras y espacio (o expresiones regulares)
def validacion_numeros(value):
    if not value.isdigit():
        raise ValidationError("El valor debe contener solo números") #raise funciona como como un print para devolver un mensajhe en caso de que no se cumpla la condicion
    
def Validacion_letras(value):
    if not value.isalpha():
        raise ValidationError("El valor debe contener solo letras")


validacion_especial = RegexValidator(
    regex= r'^[a-zA-Z\s]+$', #para establecer la expresion regular o cadena permitidos 
    message= 'el campo solo debe contener letras y espacios'

)

#validacion numeros letras y espacios
validacion_especial2 = RegexValidator(
    regex= r'^[a-zA-Z0-9\s]+$', #para establecer la expresion regular o cadena permitidos 
    message= 'el campo solo debe contener letras y espacios'

)

#validacion numeros, letras y espacios y caracteres espcailes
validacion_especial3 = RegexValidator(
    regex= r'^[a-zA-Z0-9,-ó\s]+$', #para establecer la expresion regular o cadena permitidos 
    message= 'el campo solo debe contener letras y espacios'
)

# Validación: Cédula (Ecuador)
def validar_cedula(value):
    if len(value) != 10 or not value.isdigit():
        raise ValidationError("La cédula debe contener exactamente 10 dígitos.")
    
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = sum(
        (int(digito) * coef if int(digito) * coef < 10 else int(digito) * coef - 9)
        for digito, coef in zip(value[:9], coeficientes)
    )
    digito_verificador = (10 - (suma % 10)) % 10
    
    if int(value[9]) != digito_verificador:
        raise ValidationError("La cédula ingresada no es válida.")

# Validación: Teléfono (Ecuador)
def validar_telefono(value):
    if len(value) != 10 or not value.isdigit():
        raise ValidationError("El número de teléfono debe contener exactamente 10 dígitos.")
    
    if not value.startswith(('09', '02', '03', '04', '05', '06', '07')):
        raise ValidationError("El número de teléfono no pertenece a un código válido en Ecuador.")