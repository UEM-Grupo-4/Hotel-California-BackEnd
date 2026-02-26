from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido_1 = models.CharField(max_length=100)
    apellido_2 = models.CharField(max_length=100)
    email = models.EmailField()
    
    def __str__(self):
        return f'Cliente: {self.nombre} {self.apellido_1} {self.apellido_2}'
    
telefono_validator = RegexValidator(
    regex=r'^(?:\+34)?\d{9}$',
    message='Teléfono inválido. Usa 9 dígitos (opcional +34).'
)

class Telefono(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='telefonos')
    telefono = models.CharField(max_length=15, validators=[telefono_validator])    
    
    def __str__(self):
        return f'Cliente: {self.cliente} || Teléfono: {self.telefono}'
