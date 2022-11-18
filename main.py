import os

from flask import Flask, render_template, request, send_file
from flask_dropzone import Dropzone
from flask_wtf.csrf import CSRFProtect, CSRFError

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    SECRET_KEY='very secret key indeed',
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    DROPZONE_MAX_FILE_SIZE=10,
    DROPZONE_MAX_FILES=30,
    DROPZONE_ENABLE_CSRF=True  # enable CSRF protection
)

dropzone = Dropzone(app)
csrf = CSRFProtect(app)  # initialize CSRFProtect


@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')


@app.route("/display")
def display():
    return render_template('display.html', tree=make_tree('uploads'))


@app.route("/download/<path>")
def Download(path=None):
    path = path.replace('{--}', '\\')
    return send_file(path, as_attachment=True)


def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try:
        lst = os.listdir(path)
    except OSError:
        pass  # ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                print(fn)
                tree['children'].append(
                    dict(name=name, path=str(fn).replace('\\', '{--}')))
    return tree


if __name__ == '__main__':
    app.run(debug=True)
