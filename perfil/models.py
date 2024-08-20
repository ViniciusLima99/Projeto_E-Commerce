from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from utils import valida_cpf
import re

# Create your models here.
class Perfil(models.Model):
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    idade = models.PositiveIntegerField()
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11,)
    endereco = models.CharField(max_length=50)
    numero = models.CharField(max_length=5)
    complemento = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(
        max_length=2,
        default='SP',
        choices=(
              ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
        )
    )
    
    def __str__(self) -> str:
        return f'{self.user}'
    
    def clean(self):
        error_messages = {}
        
        cpf_enviado = self.cpf or None
        cpf_salvo = None 
        perfil = Perfil.objects.filter(cpf=cpf_enviado).first() 
        #se o cpf enviando já está na base de dados
        
        if perfil:
            cpf_salvo = perfil.cpf 
            
            if cpf_salvo is not None and self.pk != perfil.pk: 
                #se o perfil já tiver um cpf e a PK daqui for diferente da pk 
              #do perfil que tem esse cpf, levantamos o erro
                error_messages['cpf'] = 'CPF já utilizado'
        
        
        if not valida_cpf(self.cpf):
            error_messages['cpf'] = 'Digite um CPF válido'

        if re.search(r'[^0-9]', self.cep) or len(self.cep) < 8:
            error_messages['cep'] = 'CEP inválido, digite os 8 números do CEP.'

        if error_messages:  
            raise ValidationError(error_messages)
    
    