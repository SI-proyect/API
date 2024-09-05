from tasks.models import Client, Rut, Calendar, Declaration

class DatabaseComparer:
    def __init__(self, cc):
        self.client = Client.objects.get(cc=cc)
        self.nit = self.client.nit
        self.declarations = None
        self.rut = None
        self.calendars = None
        self.cc = cc

    def compare_calendar(self):
        self.calendars = Calendar.objects.all()
        compared_data = {}
        cc_digits = str(self.cc)[-2:]
        if len(self.calendars) == 0:
            compared_data["error"] = "There are no calendars to compare."
            return compared_data

        for calendar in self.calendars:
            if calendar.digits < 10:
                calendar.digits = f"0{calendar.digits}"
            else:
                calendar.digits = str(calendar.digits)
            if cc_digits in calendar.digits:
                compared_data["type"] = "info"
                compared_data["calendar_warning"] = f"Client with name: '{self.client.name}' has a declaration at {calendar.date}."
                return compared_data

    def compare_declaration(self):
        self.declarations = Declaration.objects.filter(nit=self.nit).order_by("-date")[:2]
        compared_data = {
            "issue": None,
            "error": {},
            "declaration": {},
        }
        if len(self.declarations) == 0:
            compared_data["error"]["declaration"] = "There are no declarations to compare."
            return compared_data

        # For the unearned income
        uvt = self.declarations[0].uvt
        actual_declaration = self.declarations[0]
        if actual_declaration.unearned_income >= 3500 * uvt:
            compared_data["declaration"]["unearned_income"] = {"message": "Unearned income is higher than 3500 UVT. Now the user has IVA responsibility."}
            compared_data["declaration"]["unearned_income"]["type"] = "danger"

        # for the net income tax / uvt
        if actual_declaration.net_income_tax >= 71 * uvt:
            compared_data["declaration"]["net_income_tax"] = {"message": "Net income tax is higher than 71 UVT. User will lose the DIAN auditory benefits."}
            compared_data["declaration"]["net_income_tax"]["type"] = "danger"

        # compare the net income tax for the last two declarations
        if len(self.declarations) == 1:
            compared_data["issue"] = "There is only one declaration to compare."
            return compared_data
        else:
            previous_declaration = self.declarations[1]

        net_income_difference = actual_declaration.net_income_tax - previous_declaration.net_income_tax
        compared_data["declaration"]["net_income_tax_difference"] = {"message": f"Net income tax difference between the last two declarations is {net_income_difference}. Use this to take decisions for the auditory benefits."}
        compared_data["declaration"]["net_income_tax_difference"]["type"] = "info"

        # for unjustified assets
        actual_liquid_heritage = actual_declaration.liquid_heritage
        previous_liquid_heritage = previous_declaration.liquid_heritage
        liquid_heritage_difference = actual_liquid_heritage - previous_liquid_heritage
        actual_liquid_income = actual_declaration.liquid_income
        if actual_liquid_income < liquid_heritage_difference:
            compared_data["declaration"]["liquid_income"] = {"message": "Liquid income is lower than the liquid heritage difference. User has unjustified assets."}
            compared_data["declaration"]["liquid_income"]["type"] = "danger"

        # for the primary economic activity
        if actual_declaration.primary_economic_activity != self.rut.primary_economic_activity:
            compared_data["declaration"]["primary_economic_activity"] = {"message": "Primary economic activity is different from the RUT's primary economic activity."}
            compared_data["declaration"]["primary_economic_activity"]["type"] = "warning"

        # for the previous year anticipation
        if actual_declaration.previus_year_anticipation != actual_declaration.next_year_anticipation:
            compared_data["declaration"]["previous_year_anticipation"] = {"message": "Previous year anticipation is different from the next year anticipation."}
            compared_data["declaration"]["previous_year_anticipation"]["type"] = "warning"

        return compared_data

    def compare_rut(self):
        self.rut = Rut.objects.get(nit=self.nit)
        compared_data = {}
        primary_economic_activity = self.rut.primary_economic_activity
        actual_declaration = self.declarations[0]

        if primary_economic_activity != actual_declaration.primary_economic_activity:
            compared_data["issue"] = "Primary economic activity is different from the RUT's primary economic activity."
            compared_data["type"] = "warning"
            return compared_data

