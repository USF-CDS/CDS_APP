from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from youtube_transcript_api import YouTubeTranscriptApi
from tensorflow.keras.models import load_model
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(20))
    uid = db.Column(db.String(50))
    course_code = db.Column(db.String(20))
    professor = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    course_other = db.Column(db.String(50))
    submission_link = db.Column(db.String(200))
    major = db.Column(db.String(50))
    comments = db.Column(db.Text())

def extract_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return "video not on Youtube or Does not exist"

def transcript(video_id):
    try:
        m = YouTubeTranscriptApi.get_transcript(video_id)
        line = []
        new_line = []
        stopwords_line = ""
        for word in m:
            for w in word['text'].split(" "):
                line.append(w)
        stopwords_line = remove_stopwords(line)  # Assuming you have implemented this function
        return stopwords_line
    except:
        return 'No subtitles'

def predict_values(transcript):
    model = load_model('LSTM_try1.h5')
    # Perform preprocessing on the transcript if required
    # Make predictions using the LSTM model
    # Return the predicted values
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ee', methods=['GET', 'POST'])
def ee():
    if request.method == 'POST':
        semester = request.form['semester']
        uid = request.form['uid']
        course_code = request.form['course-code']
        professor = request.form['professor']
        name = request.form['name']
        email = request.form['email']
        course_other = request.form['course-other']
        submission_link = request.form['submission-link']
        major = request.form['major']
        comments = request.form['comments']

        video_id = extract_video_id(submission_link)
        transcript_text = transcript(video_id)
        predicted_values = predict_values(transcript_text)

        submission = Submission(semester=semester, uid=uid, course_code=course_code, professor=professor,
                                name=name, email=email, course_other=course_other,
                                submission_link=submission_link, major=major, comments=comments)
        db.session.add(submission)
        db.session.commit()

        return render_template('ee.html', predicted_values=predicted_values)
    return render_template('ee.html')

if __name__ == '__main__':
    app.run(debug=True)
