from typing import Any
from django import forms 
from . import models 
from django.contrib.auth.models import User

class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = 'user',
        

class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(),
        label='Senha',
    )
    password2 = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(),
        label='Confirmação senha',
    )    
    def __init__(self, usuario=None, email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.usuario = usuario
        self.email = email
        
    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'username', 'password','password2', 'email']
        
    def clean(self):
        data = self.data #dados brutos enviados no formulario
        cleaned = self.cleaned_data  #dados limpos enviados no formulários
        validation_error_msgs = {}
        print(self.cleaned_data)
        usuario_data = cleaned.get('username')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')

        email_data = cleaned.get('email')
        
        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()
        error_msg_user_exists = 'Usuario já existe'
        error_msg_email_exists = 'E-mail já existe'
        error_msg_password_match = 'As duas senhas não conferem'
        error_msg_password_short = 'Sua senha precisa de pelo menos 6 caracteres'
        error_msg_required_field = 'Este campo é obrigatório'

        # Usuarios logados: atualização
        if self.usuario:
            if usuario_db:   #se o usuario já existe na database
                if str(self.usuario) != str(usuario_db.username):
                    print('erro')
                    print(self.usuario, usuario_db.username)
                    # e esse usuario for diferente do que está sendo enviado
                    validation_error_msgs['username'] = error_msg_user_exists
            if email_db:
                if str(self.email) != str(email_db.email):
                    validation_error_msgs['email'] = error_msg_email_exists
            if password_data:
                if password_data != password2_data:
                    validation_error_msgs['password'] = error_msg_password_match
                    validation_error_msgs['password2'] = error_msg_password_match
                if len(password_data):
                    validation_error_msgs['password']= error_msg_password_short
            if validation_error_msgs:
                raise(forms.ValidationError(validation_error_msgs))
        
        # Não logados: cadastro
        else:
            if not usuario_data:
                validation_error_msgs['username'] = error_msg_required_field
            if usuario_db:
                validation_error_msgs['username'] = error_msg_user_exists
            if not email_data:
                validation_error_msgs['email'] = error_msg_user_exists
            if email_db:
                validation_error_msgs['email'] = error_msg_email_exists
            if not password_data:
                validation_error_msgs['password'] = error_msg_required_field
                validation_error_msgs['password2'] = error_msg_required_field
            if password_data != password2_data:
                validation_error_msgs['password'] = error_msg_password_match
                validation_error_msgs['password2'] = error_msg_password_match
            if len(password_data) < 6 :
                validation_error_msgs['password']= error_msg_password_short
            if validation_error_msgs:
                raise(forms.ValidationError(validation_error_msgs))
            
            if validation_error_msgs:
                raise(forms.ValidationError(validation_error_msgs))
            