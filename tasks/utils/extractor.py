from datetime import datetime
import re
from pdf2image import convert_from_bytes, exceptions
from PIL import Image, ImageFilter
import pytesseract
import fitz
import io

class PDFExtractor:
    def __init__(self, pdf_file, selector):
        self.pdf_file = pdf_file
        self.selector = selector
        self.roiRunt = [
            (150.03, 733, 623.97, 60),   # Nit
            (132, 1891, 163, 46),        # Principal actividad Ec
            (690, 1885, 170, 51),        # Segunda ActEco
            (259, 2046, 82, 52),         # Responsabilidad1
            (343, 2046, 82, 52),         # Responsabilidad2
            (424, 2046, 82, 52)          # Responsabilidad3
        ]
        self.roiDeclaration = [
            (276, 749, 203, 45),         # 1 Actividad Ec
            (270, 256, 180, 50),         # 2 Year
            (2066, 2498, 481, 37),       # 3 Anticipo year anterior
            (2006, 2646, 471, 46),       # 4 Anticipo year siguiente
            (2216, 2299, 272, 40),       # 5 Impuesto neto de renta
            (2027, 897, 444, 38),        # 6 Ingresos por rentas no laborales
            (335, 691, 473, 51),         # 7 Nit
            (2222, 796, 258, 50),        # 8 Patrimonio líquido
            (525, 1700, 448, 44),        # 9 Renta liq1
            (2034, 1699, 434, 42),       # 10 Renta liq2
            (1529, 1695, 443, 46),       # 11 Renta liq3
            (1032, 1700, 443, 41),       # 12 Renta liq4
        ]
        self.rois = []
        self.json_data = {}

    def set_rois_and_json(self):
        if self.selector == "1":
            self.rois = self.roiRunt
            self.json_data = {
                "nit": "",
                "primary_economic_activity": "",
                "secondary_economic_activity": "",
                "Responsabilidad1": "",
                "Responsabilidad2": "",
                "Responsabilidad3": ""
            }
        elif self.selector == "2":
            self.rois = self.roiDeclaration
            self.json_data = {
                "primary_economic_activity": "",
                "date": "",
                "previus_year_anticipation": "",
                "next_year_anticipation": "",
                "net_income_tax": "",
                "unearned_income": "",
                "nit": "",
                "liquid_heritage": "",
                "RentaLiq1": "",
                "RentaLiq2": "",
                "RentaLiq3": "",
                "RentaLiq4": ""
            }

    def extract_text_from_pdf(self):
        pdf_bytes = self.pdf_file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(dpi=300)  # Convertir la página en una imagen a 300 dpi

            # Convertir pixmap a formato de imagen específico y luego a bytes
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            grayscale_image = img.convert("L")

            for j, roi in enumerate(self.rois):
                x, y, w, h = roi
                cropped_image = grayscale_image.crop((x, y, x + w, y + h))
                # Mejora el contraste y nitidez
                enhanced_image = cropped_image.filter(ImageFilter.EDGE_ENHANCE_MORE)

                # Convertir a blanco y negro
                bw_image = enhanced_image.point(lambda p: 255 if p > 140 else 0)

                # Configuración personalizada de Tesseract
                custom_config = r'--oem 3 --psm 7 outputbase digits'

                # Extraer el texto con Tesseract
                extracted_text = pytesseract.image_to_string(bw_image, config=custom_config)
                cleaned_text = extracted_text.replace(" ", "").replace("\n", "").strip()
                cleaned_text = re.sub(r'\D', '', cleaned_text)
                key = list(self.json_data.keys())[j]
                self.json_data[key] = cleaned_text

            print(self.json_data)

    def get_data(self):
        self.set_rois_and_json()
        self.extract_text_from_pdf()
        if self.selector == "2":
            self.json_data["date"] = f"{self.json_data['date']}-01-01"
            self.json_data["liquid_income"] = str(int(self.json_data["RentaLiq1"]) + int(self.json_data["RentaLiq2"]) + int(self.json_data["RentaLiq3"]) + int(self.json_data["RentaLiq4"]))
            self.json_data.pop("RentaLiq1")
            self.json_data.pop("RentaLiq2")
            self.json_data.pop("RentaLiq3")
            self.json_data.pop("RentaLiq4")
        else:
            codes = ["48", "49"]
            keys = ["Responsabilidad1", "Responsabilidad2", "Responsabilidad3"]
            self.json_data["date"] = datetime.now().strftime("%Y-%m-%d")
            for value in keys:
                if self.json_data[value] in codes:
                    if self.json_data[value] == "48":
                        self.json_data["fiscal_responsibilities"] = True
                    else:
                        self.json_data["fiscal_responsibilities"] = False
                else:
                    self.json_data["fiscal_responsibilities"] = ""
        return self.json_data