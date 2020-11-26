from flask import render_template, request, url_for, redirect, abort, session
from app import app
import json
import os.path
import io
from werkzeug.utils import secure_filename
#import google cloud  client library
from google.cloud import vision
from google.cloud.vision import types

from google.oauth2 import service_account

#Read the credentials for the cloud library.
credentials = service_account.Credentials.from_service_account_file(
    os.path.join(app.root_path, 'static', 'Credential', 'CloudMobileAppAPICredentials.json'))


code = None
error = None
labels = None
image = None
client = None
objects = None
points = []
text = []
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('/index.html', title='Conjugate')


@app.route('/about', methods=['GET'])
def about():
    return render_template('/about.html', title='About Conjugate')


@app.route('/algorithm1', methods=['GET', 'POST'])
def algorithm1():
    return render_template('/algorithm1.html', title='text-Labelling', code=code, labels=labels)


@app.route('/algorithm2', methods=['GET'])
def algorithm2():
    return render_template('/algorithm2.html', title='face-Detection', code=code, points=points)

@app.route('/algorithm3', methods=['GET'])
def algorithm3():
    return render_template('/algorithm3.html', title='Multiple-Object-Detection', code=code, points=points, text=text,objects=objects)

@app.route('/your-file', methods=['GET', 'POST'])
def your_file():
    algo = request.args.get('algo')
    error = ""
    if algo is None:
        global code
        code = request.form['code']
    if request.method == 'POST':
        files = {}
        pic = request.files['file']
        full_name = request.form['code'] + "." + secure_filename(pic.filename).split('.')[1]
        # create the user_image directory if not exists
        if not os.path.exists(os.path.join(app.root_path, 'static', 'user_image')):
            os.makedirs(os.path.join(app.root_path, 'static', 'user_image'))
        # dynamically store to the user_image folder
        if os.path.exists('files.json'):
            with open('files.json') as add_file:
                files = json.load(add_file)
        # Duplicate name redirects to home
        if code in files.keys():
            error = 'Give different image name.'
            return render_template('index.html', error=error, code=code)
        pic.save(os.path.join(app.root_path, 'static', 'user_image', full_name))
        files[request.form['code']] = {'file': full_name}
        with open('files.json', 'w') as add_file:
            json.dump(files, add_file)
            session[code] = True

            # google API
            print('___________________________-')
            # Instantiates a client
            global client
            client = vision.ImageAnnotatorClient(credentials=credentials)

            # The name of the image file to annotate

            print('full_name = ', full_name)
            file_name = os.path.abspath('static/user_image/')
            file_name = file_name+'/'+full_name
            print('file_name',file_name)
            # Loads the image into memory
            with io.open(file_name, 'rb') as image_file:
                content = image_file.read()
            global image
            image = vision.types.Image(content=content)

            # Performs label detection on the image file
            response = client.label_detection(image=image)
            global labels
            labels = response.label_annotations

            print('Labels:')
            for label in labels:
                print(label.description)
            global points
            # end of google API
            print('---------------------------')
        return render_template('your_file.html', code=request.form['code'])
    #?algo=algorithm1||algorithm2
    elif algo == 'algorithm1':
        return redirect(url_for(algo, code=code, labels=labels))
    elif algo == 'algorithm2':
        response = client.face_detection(image=image)
        faces = response.face_annotations
        points = []
        for object_ in faces:
            for vertex in object_.bounding_poly.vertices:
                points.append(vertex.x)
                points.append(vertex.y)
        return redirect(url_for(algo, code=code, points=points))
    elif algo == 'algorithm3':
        global objects
        objects = client.object_localization(image=image).localized_object_annotations
        points = []
        for object_ in objects:
            for vertex in object_.bounding_poly.normalized_vertices:
                points.append(vertex.x)
                points.append(vertex.y)
        return redirect(url_for(algo, code=code, points=points, objects=objects))
    else:
        return render_template('index.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    return render_template('user.html', codes=session.keys(), title='User Images')


@app.route('/<string:code>')
def redirect_to_image(code):
    if os.path.exists('files.json'):
        with open('files.json') as add_file:
            files = json.load(add_file)
            if code in files.keys():
                return redirect(url_for('static', filename='user_image/' + files[code]['file']))
    return abort(404)


@app.route('/webcam', methods=['GET'])
def webcam():
    return render_template('/webcam.html', title='Capture Image')







