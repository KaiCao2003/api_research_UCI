from flask import Flask, render_template, request, jsonify, flash, url_for, redirect

import data
from engine import send_request

app = Flask(__name__)
app.secret_key = 'makabaka'

last_content = ""
next_request_time = 0


@app.route('/')
def index():
    return render_template('index.html', next_request_time=next_request_time, last_content=last_content)


@app.route('/send', methods=['POST'])
def send_content():
    global last_content, next_request_time

    course_title = None
    sectionTime = None
    max_capacity = None
    total_enrolled = None
    status = None
    whether_full = None

    courseCode = request.form['content']
    print(courseCode)

    if courseCode is not None:
        # If content is different or it's the first request, send the request immediately
        if courseCode != last_content or next_request_time == 0:
            last_content = courseCode
            # Call the send function
            course_title, sectionTime, max_capacity, total_enrolled, status, whether_full = send_request(courseCode)
            print(course_title)

    return jsonify({
        'course_title': course_title,
        'sectionTime': sectionTime,
        'max_capacity': max_capacity,
        'total_enrolled': total_enrolled,
        'course_status': status,
        'whether_full': whether_full
    })


@app.route('/subscribe', methods=['POST'])
def subscribe():
    code = request.form['content']
    email = request.form['email']

    success = data.add_or_update_record(code, email)

    if success:
        flash('Successfully subscribed!')
    else:
        flash('Email already exists for this code.')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
