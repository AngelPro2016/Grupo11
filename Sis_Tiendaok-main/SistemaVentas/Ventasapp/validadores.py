from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator #para hacer validaciones especiales letras y espacio (o expresiones regulares)
def validacion_numeros(value):
    if not value.isdigit():
        raise ValidationError("El valor debe contener solo números") #raise funciona como como un print para devolver un mensajhe en caso de que no se cumpla la condicion
    
def Validacion_letras(value):
    if not value.isalpha():
        raise ValidationError("El valor debe contener solo letras")

 #expresiones regulares
   
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
