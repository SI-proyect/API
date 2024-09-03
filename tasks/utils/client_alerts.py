from tasks.models import Client, Rut, Calendar, Declaration

class DatabaseComparer:
    def __init__(self, cc):
        self.clients = Client.objects.get(cc=cc)
        self.nit = self.clients.nit
        self.declarations = Declaration.objects.filter(nit=self.nit)
        self.ruts = Rut.objects.filter(nit=self.nit)
        self.calendars = Calendar.objects.all()
        self.cc = cc
        self.compared_data = {
            "error": {},
            "calendar_warning": None,
            "rut_warning": None,
            "type": None,
        }

    def compare_calendar(self):
        cc_digits = str(self.cc)[-2:]
        if len(self.calendars) == 0:
            self.compared_data["error"]["calendar"] = "There are no calendars to compare."
            return self.compared_data

        for calendar in self.calendars:
            if calendar.digits < 10:
                calendar.digits = f"0{calendar.digits}"
            else:
                calendar.digits = str(calendar.digits)
            if cc_digits in calendar.digits:
                self.compared_data["type"] = "info"
                self.compared_data["calendar_warning"] = f"Client has a declaration at {calendar.date}."
                return self.compared_data

    def compare_rut(self):
        if len(self.ruts) == 0:
            self.compared_data["error"]["rut"] = "There are no RUTs to compare."
            return self.compared_data

        for rut in self.ruts:
            if rut.cc == self.cc:
                self.compared_data["rut_warning"] = f"Client has a RUT registered."
                return self.compared_data
