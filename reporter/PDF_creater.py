from fpdf import FPDF


class PDFGenerator:

    def __init__(self, font_path = 'DejaVuSans.ttf'):
        self.font_path = font_path

    def create_pdf_from_text(self, text, output_filename, font_size=10):

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', self.font_path, uni=True)

        # Установите размер шрифта
        pdf.set_font('DejaVu', '', font_size)

        # Установите координаты X и Y для начала текста (левый верхний угол)
        pdf.set_xy(10, 10)

        # Разделяйте текст на строки и добавляйте их в PDF с выравниванием по левому краю
        lines = text.split('\n')
        for line in lines:
            pdf.multi_cell(0, 10, txt=line, align='L')

        # Сохраните PDF-документ
        pdf.output(output_filename)



if __name__ == '__main__':

    # Пример использования функции
    text_to_convert = """
        Это пример текста,
        который будет преобразован в PDF файл.
        Вы можете добавить свой текст сюда.
        """
    PDFGenerator().create_pdf_from_text(text_to_convert, 'output.pdf',  font_size=10)
