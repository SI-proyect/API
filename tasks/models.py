from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    cc = models.IntegerField(default=0, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, default='null')
    last_name = models.CharField(max_length=100, default='null')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cc','name', 'last_name']

    def __str__(self):
        return "(" + str(self.cc) + ") " + self.name + " " + self.last_name + " <" + self.email + ">"

class Client(models.Model):
    cc = models.IntegerField(default=0, unique=True)
    nit = models.IntegerField(default=0, unique=True)
    name = models.CharField(max_length=100, default='null')
    address = models.CharField(max_length=100, default='null')
    telephone = models.IntegerField(default=0)
    mail = models.CharField(max_length=100, default='null')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fiscal_responsibilities = models.BooleanField(default=False)
    extra = models.CharField(max_length=300, default='null')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.cc

class Rut(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    nit = models.IntegerField(default=0, unique=True)
    check_digit = models.IntegerField(default=0) # Numero de verificacion
    primary_economic_activity = models.IntegerField(default=0)
    secondary_economic_activity = models.IntegerField(default=0)
    date = models.DateField(default='null') # y m d
    rut_type = models.CharField(max_length=100, default='null')

    def __str__(self) -> str:
        return 'Hola'

class Declaration(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default='null')
    ## TODO: Agregar campos para datos que vamos a sacar del pdf de las declaraciones (Jerson)

