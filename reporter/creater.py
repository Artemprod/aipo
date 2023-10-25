from container import gpt_reporter, pdf_generator


if __name__ == '__main__':
    gpt_reporter.model = gpt_reporter.model_3
    report_1_user_301213126 = pdf_generator.create_pdf_from_text(
        text=gpt_reporter.get_report_by_user_id_dinymic(301213126), output_filename='report.pdf', font_size=10)
