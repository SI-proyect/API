from tasks.models import Client, Rut, Calendar, Declaration

class DatabaseComparer:
    def __init__(self, cc):
        self.client = Client.objects.get(cc=cc)
        self.nit = self.client.nit
        self.declarations = None
        self.rut = None
        self.calendars = None
        self.cc = cc
        self.warnings = []

    def compare_calendar(self):
        self.calendars = Calendar.objects.all()
        cc_digits = str(self.cc)[-2:]
        if len(self.calendars) == 0:
            # compared_data["error"] = "There are no calendars to compare."
            self.warnings.append({
                    "message": "No hay calendarios para poder comparar.",
                    "type": "danger"
                    })
            return self.warnings
        for calendar in self.calendars:
            if calendar.digits < 10:
                calendar.digits = f"0{calendar.digits}"
            else:
                calendar.digits = str(calendar.digits)
            if cc_digits in calendar.digits:
                self.warnings.append({
                        "message": f"EL cliente {self.client.name} tiene que presentar su declaracion el dia f{calendar.date}",
                        "type": "warning",
                        "cc": self.cc,
                        "date": calendar.date,
                        "digits": calendar.digits,
                        "name": self.client.name,
                        })

        return self.warnings
    def compare_declaration(self):
        self.rut = Rut.objects.get(nit=self.nit)
        self.warnings.clear()
        self.declarations = Declaration.objects.filter(nit=self.nit).order_by("-date")[:2]

        if len(self.declarations) == 0:
            self.warnings.append( {
                    "message": "No hay declaraciones para comparar",
                    "type": "danger"
                    })

            return self.warnings

        # For the unearned income
        uvt = self.declarations[0].uvt
        actual_declaration = self.declarations[0]
        if actual_declaration.unearned_income >= 3500 * uvt:
            self.warnings.append({
                    "message": "Las rentas no laborales son mayores a 3500 UVT. El usuario tiene responsabilidad de IVA.",
                    "type": "danger"
                    })
            return self.warnings

        # for the net income tax / uvt
        if actual_declaration.net_income_tax >= 71 * uvt:
            self.warnings.append({
                    "message": "El impuesto neto de renta es mayor a 71 UVT. El cliente perderá los beneficios de auditoria de la DIAN.",
                    "type": "danger"
                    })

        # compare the net income tax for the last two declarations
        print(self.declarations)
        if len(self.declarations) == 1:
            self.warnings.append({
                    "message": "Solo hay una declaración para comparar.",
                    "type": "danger"
                    })
            return self.warnings
        else:
            previous_declaration = self.declarations[1]

        net_income_difference = actual_declaration.net_income_tax - previous_declaration.net_income_tax
        self.warnings.append({
                "message": f"La diferencia del impuesto neto de renta de las anteriores 2 (dos) declaraciones es de {net_income_difference}. Utilize esto para tomar decisiones sobre los beneficios de auditoria.",
                "type": "info"
                })

        # for unjustified assets
        actual_liquid_heritage = actual_declaration.liquid_heritage
        previous_liquid_heritage = previous_declaration.liquid_heritage
        liquid_heritage_difference = actual_liquid_heritage - previous_liquid_heritage
        actual_liquid_income = actual_declaration.liquid_income
        if actual_liquid_income < liquid_heritage_difference:
            self.warnings.append({
                    "message": "La renta líquida es menor que la diferencia de los patrimonios líquidos. EL cliente tiene ingresos injustificados.",
                    "type": "danger"
                    })

        # for the primary economic activity
        if actual_declaration.primary_economic_activity != self.rut.primary_economic_activity:
            self.warnings.append({
                    "message": "La actividad económica primaria es diferente a la actividad económica primaria del RUT.",
                    "type": "warning"
                    })

        # for the previous year anticipation
        if actual_declaration.previus_year_anticipation != actual_declaration.next_year_anticipation:
            self.warnings.append({
                    "message": "La anticipación del año anterior es diferente a la anticipación del siguiente año.",
                    "type": "warning"
                    })

        return self.warnings

    def compare_rut(self):
        self.rut = Rut.objects.get(nit=self.nit)
        self.warnings.clear()
        primary_economic_activity = self.rut.primary_economic_activity
        actual_declaration = self.declarations[0]

        if primary_economic_activity != actual_declaration.primary_economic_activity:
            self.warnings.append({
                    "message": "La actividad económica principal es diferente a la actividad económica principal del RUT.",
                    "type": "danger",
                    })
            return self.warnings

