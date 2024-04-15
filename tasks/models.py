from django.db import models

# Create your models here.
class User(models.Model):
    cc = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default='null') 
    lastname = models.CharField(max_length=100, default='null')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.cc

class Client(models.Model):
    cc = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default='null')
    address = models.CharField(max_length=100, default='null')
    telephone = models.IntegerField(default=0)
    mail = models.CharField(max_length=100, default='null')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    extra = models.CharField(max_length=300, default='null')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.cc

class Rut(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    nit = models.IntegerField(default=0)
    check_digit = models.IntegerField(default=0) # Numero de verificacion
    date = models.DateField(default='null') # y m d
    rut_type = models.CharField(max_length=100, default='null')

    def __str__(self) -> str:
        return 'Hola'

class Fiscal_Responsibilities(models.Model):
    rut = models.ForeignKey(Rut, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.rut

class Responsibilities(models.Model):
    fiscal_responsabilities = models.ForeignKey(Fiscal_Responsibilities, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, default='null')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.description
    
class Economic_activity(models.Model):
    rut = models.ForeignKey(Rut, on_delete=models.CASCADE)

class Declaration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # declaration_type = models.
    state = models.CharField(max_length=100, default='null')
    date = models.DateField(default='null')
    description = models.CharField(max_length=100, default='null')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

# Patrimonio
class Heritage(models.Model):
    declaration = models.ForeignKey(Declaration, on_delete=models.CASCADE)
    date = models.DateField(default='null')
    # Patrimonio liquido = Patrimonio Bruto - Patrimonio Pasivo
    liquid_equity = models.IntegerField(default=0)
    heritage_type = models.CharField(max_length=100, default='null')

# Pasive
class Pasive_Heritage(models.Model):
    heritage = models.ForeignKey(Heritage, on_delete=models.CASCADE)
    # Deudas financieras
    financial_debts = models.IntegerField(default=0)
    # Deudas comerciales
    business_debts = models.IntegerField(default=0)
    # Deudas por impuestos
    tax_debts = models.IntegerField(default=0)
    # Otras deudas
    other_debts = models.IntegerField(default=0)
    # Pasivos inexistentes
    nonexistent_liabilities = models.IntegerField(default=0)
    # Total
    total = models.IntegerField(default=0)

class Brute_Heritage(models.Model):
    # titulos
    titles = models.CharField(max_length=100, default='null')
    # inversiones
    investments = models.CharField(max_length=100, default='null')
    # Acciones
    stock = models.CharField(max_length=100, default=100)
    # Inventarios
    inventories = models.CharField(max_length=100, default=100)
    # Cuentas por cobrar
    accounts_receivable = models.CharField(max_length=100, default=100)
    # Activos fijos
    fixed_assets = models.IntegerField(default=0)
    # Otros activos
    other_assets = models.IntegerField(default=0)
    # Activos omitidos
    omitted_assets = models.IntegerField(default=0)
    # Total
    total = models.IntegerField(default=0)
