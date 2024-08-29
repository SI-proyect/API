import fitz  # Esta es la librería pymupdf que habéis instalado
import re
from datetime import datetime, timedelta
import json

class CalendarExtractor:
    # Mapeo de nombres de meses en español a números
    meses = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12
    }

    # Convertir ordinal a número
    mapa_ordinal = {
        "Primer": 1,
        "Segundo": 2,
        "Tercer": 3,
        "Cuarto": 4,
        "Quinto": 5,
        "Sexto": 6,
        "Séptimo": 7,
        "Octavo": 8,
        "Noveno": 9,
        "Décimo": 10,
        "Décimo primer": 11,
        "Décimo segundo": 12,
        "Décimo tercer": 13,
        "Décimo cuarto": 14,
        "Décimo quinto": 15,
        "Décimo sexto": 16,
        "Décimo séptimo": 17,
        "Décimo octavo": 18,
        "Décimo noveno": 19,
        "Vigésimo": 20,
        "Vigésimo Primero": 21
    }

    def __init__(self, document):
        self.document = document
        self.dates = []

    def calendar_extractor(self):
        # Open the PDF file from in-memory bytes
        pdf_document = fitz.open(stream=self.document.read(), filetype="pdf")
        pages_to_read = [9, 10]

        # Extract text from the PDF
        text = ""
        for page_num in pages_to_read:
            page = pdf_document.load_page(page_num)  # Carga la página específica
            text += page.get_text()
        text = text.replace('�', '')
        lines = text.split('\n')

        # Extract the month and year
        index_rv = [1 if re.match(r'(\d{2})\s*y\s*(\d{2})', line) else 0 for line in lines]
        index_rv = [i for i, x in enumerate(index_rv) if x == 1]

        if index_rv == []:
            return []

        for i in index_rv:
            self.dates.append([lines[i].split(' y '), lines[i+1].split(' día hábil de ')])

        return self.dates

    def calculate_business_day(self, month, year, business_day_number):
        # Create a start date for the given month
        start_date = datetime(year, month, 1)

        # Business day counter
        business_day_counter = 0

        # Iterate over the days of the month
        while True:
            # If the day is a business day (Monday to Friday)
            if start_date.weekday() < 5:
                business_day_counter += 1

            # If we reach the desired business day
            if business_day_counter == business_day_number:
                return start_date

            # Move to the next day
            start_date += timedelta(days=1)

    def transform_to_dict(self):
        dates_dict = {}

        for a,b in self.dates:
            month = self.meses[b[1].lower()]
            year_date = datetime.now().year
            bussiness_day = self.mapa_ordinal[b[0]]
            day = self.calculate_business_day(month, year_date, bussiness_day)

            for c in a:
                dates_dict[c] = day.strftime('%Y-%m-%d')

        return dates_dict