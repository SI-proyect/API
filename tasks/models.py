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


class User(AbstractBaseUser, PermissionsMixin): #baic information about the user (only 1 for the moment )
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
    REQUIRED_FIELDS = ['cc', 'name', 'last_name']

    def __str__(self):
        return "(" + str(self.cc) + ") " + self.name + " " + self.last_name + " <" + self.email + ">"


class Client(models.Model):
    cc = models.IntegerField(default=0, unique=True) #user sets
    nit = models.IntegerField(default=0, unique=True) #user sets
    name = models.CharField(max_length=100, default='null') #user sets
    address = models.CharField(max_length=100, default='null') #user sets
    telephone = models.IntegerField(default=0) #user sets
    mail = models.CharField(max_length=100, default='null') #user sets
    user = models.ForeignKey(User, on_delete=models.CASCADE) #user sets
    notes = models.CharField(max_length=300, default='null') #user sets
    fiscal_responsibilities = models.BooleanField(default=False) #false by default but can chage by the rut and the declaration
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "(" + str(self.cc) + ") " + self.name + " " + " <" + self.mail + ">"


class Rut(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE) #for nit credential and update the responsabilities
    nit = models.IntegerField(default=0, unique=True) #document cell and need to be compared with client.nit
    primary_economic_activity = models.IntegerField(default=0) # document cell
    secondary_economic_activity = models.IntegerField(default=0) #document cell
    date = models.DateField(default='null')  # y m d  --> document cell
    def __str__(self):
        return str(self.client) + " " + str(self.nit)

class Declaration(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default='null') #for nit and primary-activity
    nit = models.IntegerField(default=0, unique=True) #document cell and ned to be compared with client.nit
    primary_economic_activity = models.IntegerField(default=0) #alert('need to be the same of the rut.primary') document cell
    previus_year_anticipation = models.IntegerField(default=0) #alert('need be the same than the below'). Document cell
    next_year_anticipation = models.IntegerField(default=0) #document cell
    liquid_heritage = models.IntegerField(default=0) #document cell
    liquid_income = models.IntegerField(default=0) #document cell. #alert('this < liquid_heritage - liuqid_heritage_previus')document cell
    net_income_tax = models.IntegerField(default=0) #make the difference betwenn this and the last year tax and if this > 71uvt make alert
    anual_auditory_benefits = models.IntegerField(default=0)#user sets
    semestrals_auditory_benefits = models.IntegerField(default=0) #user sets
    unearned_income = models.IntegerField(default=0) #alert('alert if this >= 3500uvt')
    uvt = models.IntegerField(default=0) #user set
    date = models.DateField(default=None) #document date. document cell

    #TODO : hacer un __str__ informativo de esto

class Calendar(models.Model):
    digits = models.IntegerField(default=0)
    date = models.DateField(default='null')

## DEBEMOS REVISAR COMO PROPONER EL INTERCAMBIO DE INFORMACION ENTRE LA DECLARACION DEL AÑO ANTERIOR Y ESTA
