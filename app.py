from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileStorage
from werkzeug.utils import secure_filename
from wtforms import SubmitField
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import math
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.dirname(__file__)) + "/uploads"



class FileUpload(FlaskForm):
    pdf_file = FileField("Upload your file", validators=[FileRequired()])
    submit = SubmitField("Submit your file")


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FileUpload()
    if form.validate_on_submit():
        filename = secure_filename(form.pdf_file.data.filename)
        session['file'] = os.path.join(app.config['UPLOAD_FOLDER'],filename)
        form.pdf_file.data.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return redirect(url_for('result'))

    return render_template('index.html', form=form)


@app.route("/result")
def result():
    all_text = convert_pdf_to_txt(session['file'])
    all_text = all_text.split("\n")
    allowed = [chr(i) for i in range(65, 65 + 26)]
    allowed.extend([chr(i) + '+' for i in range(65, 65 + 26)])
    allowed.append('Ab')
    allowed.extend([str(i) for i in range(0, 50)])
    one_or_two = []
    for i in all_text:
        if len(i) <= 2 and i in allowed:
            one_or_two.append(i)
    sno = []

    for i in range(len(one_or_two)):
        if one_or_two[i].isnumeric() and int(one_or_two[i]) + 1 == int(one_or_two[i + 1]):
            sno.append(int(one_or_two[i]))
        else:
            break

    credits = []
    grade = []

    for i in range((sno[-1] + 1) * 2, sno[-1] * 3 + 3):
        credits.append(one_or_two[i])

    for i in range((sno[-1] + 1) * 3, sno[-1] * 4 + 4):
        grade.append(one_or_two[i])

    credits = list(map(int, credits))
    print(credits)
    total_credits = sum(credits)
    print(grade)

    grade_to_mark = {
        'O': 10,
        'A+': 9,
        'A': 8,
        'B+': 7,
        'B': 6,
        'C': 5,
        'P': 4,
        'F': 0,
        'Ab': 0,
        'I': 0
    }

    grade = list(map(lambda x: grade_to_mark[x], grade))
    final_pair = zip(credits, grade)
    final_cgpa = 0
    for i, j in final_pair:
        final_cgpa += i * j
    final_cgpa /= total_credits
    final_cgpa = '{0:.2f}'.format(final_cgpa)
    print(final_cgpa)

    return render_template('result.html',cgpa=final_cgpa)


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    os.remove(session['file'])
    return text


if __name__ == '__main__':
    app.run(debug=True)
