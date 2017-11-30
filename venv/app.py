from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from wtforms import Form, StringField, DecimalField, FloatField, DateTimeField, SelectField, BooleanField, IntegerField
import time
from datetime import datetime
import operator
import simplejson as json
ops = {"<": operator.lt,
       ">": operator.gt,
       "=": operator.eq,
       "<=": operator.le,
       ">=": operator.ge}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)


class App_Runs(db.Model):
    __tablename__ = 'app_runs'
    id = db.Column('id', db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.Float, nullable=False)
    app_version = db.Column('app_version', db.String(15))
    platform = db.Column('platform', db.String(15))
    machine_fingerprint = db.Column('machine_fingerprint', db.String(100))
    machine_name = db.Column('machine_name', db.String(100))

class Event_Logs(db.Model):
    __tablename__ = 'event_logs'
    id = db.Column('id', db.Integer, primary_key=True)
    run_id = db.Column('run_id', db.Integer, nullable=False)
    thread_id = db.Column('thread_id', db.String(100) , nullable=False)
    thread_name = db.Column('thread_name', db.String(100) , nullable=False)
    checksum = db.Column('checksum', db.String(100) , nullable=False)
    timestamp = db.Column('timestamp', db.Float, nullable=False)
    level = db.Column('level', db.Integer, nullable=False)
    culprit = db.Column('culprit', db.String(100))
    pathname = db.Column('pathname', db.String(100))
    lineno = db.Column('lineno', db.Integer)
    user_id = db.Column('user_id', db.String(100))
    email = db.Column('email', db.String(100))
    message = db.Column('message', db.String(500), nullable=False)
    exception = db.Column('exception', db.String(500))
    stacktrace = db.Column('stacktrace', db.String(500))
    extra = db.Column('extra', db.String(500))

class FilterForm1(Form):
    timestamp_filter = DateTimeField('')
    timestamp_operator = SelectField(
        '',
        choices=[('<', '<'), ('>', '>')]
    )
    app_version_filter = StringField('')
    platform_filter = StringField('')
    line_limit = IntegerField('')


class FilterForm2(Form):
    run_id_filter = DecimalField('')
    run_id_latest = BooleanField('')
    thread_name_filter = StringField('')
    timestamp_filter = DateTimeField('')
    timestamp_operator = SelectField(
        '',
        choices=[('<', '<'), ('>', '>')]
    )
    level_filter = DecimalField('')
    level_operator = SelectField(
        '',
        choices=[('=', '='), ('<', '<'), ('>', '>'), ('<=', '<='), ('>=', '>=')]
    )
    culprit_filter = StringField('')
    pathname_filter = StringField('')
    lineno_filter = DecimalField('')
    lineno_operator = SelectField(
        '',
        choices=[('=', '='), ('<', '<'), ('>', '>'), ('<=', '<='), ('>=', '>=')]
    )
    user_id_filter = StringField('')
    email_filter = StringField('')
    message_filter = StringField('')
    exception_filter = StringField('')
    exception_check = BooleanField('')
    stacktrace_filter = StringField('')
    line_limit = IntegerField('')


@app.route('/app_runs', methods=['GET', 'POST'])
def app_runs():
    form1 = FilterForm1(request.form, line_limit=100)

    if request.method == 'POST':


        timestamp_filter2 = form1.timestamp_filter.data
        app_version_filter = form1.app_version_filter.data
        platform_filter = form1.platform_filter.data
        line_limit = form1.line_limit.data

        timestamp_operator = ops[form1.timestamp_operator.data]

        app_rows = App_Runs.query.all()
        new_app_rows = []
        new_timestamps = []
        #LETS FILTER SHIT BOI

        row_count = 0
        for row in reversed(app_rows):
            print(app_version_filter in row.app_version)
            temp_time = datetime.strptime(time.strftime("%B %d %Y %H:%M:%S", time.localtime(row.timestamp)), "%B %d %Y %H:%M:%S")
            if ((timestamp_filter2==None or (timestamp_operator(temp_time, timestamp_filter2)))
                and (app_version_filter in row.app_version)
                and (platform_filter.upper() in row.platform.upper())):
                if line_limit!=None and (row_count >= line_limit):
                    break
                new_app_rows.append(row)
                new_timestamps.append(temp_time)
                row_count+=1

        if line_limit == None:
            line_limit = 'all'
        return render_template('app_runs.html', rows1 = zip(new_app_rows, new_timestamps), form1=form1, line_limit=str(line_limit))
    else:
        app_rows = App_Runs.query.all()
        new_timestamps = []
        new_app_rows = []
        row_count = 0
        for row in reversed(app_rows):
            if row_count >= 100:
                break
            temp_time = datetime.strptime(time.strftime("%B %d %Y %H:%M:%S", time.localtime(row.timestamp)), "%B %d %Y %H:%M:%S")

            new_timestamps.append(temp_time)
            new_app_rows.append(row)
            row_count+=1

        return render_template('app_runs.html', rows1 = zip(new_app_rows, new_timestamps), form1=form1, line_limit='100')



@app.route('/log_events', methods=['GET', 'POST'])
def log_events():
    form2 = FilterForm2(request.form, line_limit=100)

    if request.method == 'POST':
        run_id_filter = form2.run_id_filter.data
        thread_name_filter = form2.thread_name_filter.data
        timestamp_filter = form2.timestamp_filter.data
        level_filter = form2.level_filter.data
        culprit_filter = form2.culprit_filter.data
        pathname_filter = form2.pathname_filter.data
        lineno_filter = form2.lineno_filter.data
        user_id_filter = form2.user_id_filter.data
        email_filter = form2.email_filter.data
        message_filter = form2.message_filter.data
        exception_filter = form2.exception_filter.data
        stacktrace_filter = form2.stacktrace_filter.data
        run_id_latest = form2.run_id_latest.data

        timestamp_operator = ops[form2.timestamp_operator.data]
        level_operator = ops[form2.level_operator.data]
        lineno_operator = ops[form2.lineno_operator.data]

        exception_check = form2.exception_check.data
        line_limit = form2.line_limit.data


        event_rows = Event_Logs.query.all()
        latest_rid = 0
        if run_id_latest:
            latest_rid = event_rows[-1].run_id
        new_event_rows = []
        new_timestamps = []
        new_messages = []
        new_exceptions = []
        is_row_collapsable = []
        row_count=0
        current_repeated_row = None
        number_of_repeats = 1
        #LETS FILTER SHIT BOI
        for row in reversed(event_rows):
            temp_time = datetime.strptime(time.strftime("%B %d %Y %H:%M:%S", time.localtime(row.timestamp)), "%B %d %Y %H:%M:%S")

            if ((user_id_filter=="" or (row.user_id!=None and (user_id_filter.upper() in row.user_id.upper())))
                and (email_filter=="" or (row.email!=None and (email_filter.upper() in row.email.upper())))
                and (stacktrace_filter=="" or (row.stacktrace!=None and (stacktrace_filter.upper() in row.stacktrace.upper())))
                and (exception_filter=="" or (row.exception!=None and (exception_filter.upper() in row.exception.upper())))
                and (run_id_filter==None or run_id_filter==row.run_id)
                and (level_filter==None or level_operator(row.level, level_filter))
                and (lineno_filter==None or level_operator(row.lineno, lineno_filter))
                and thread_name_filter.upper() in row.thread_name.upper()
                and culprit_filter.upper() in row.culprit.upper()
                and pathname_filter.upper() in row.pathname.upper()
                and message_filter.upper() in row.message.upper()
                and not (row.exception==None and exception_check)
                and (row.run_id >= latest_rid)
                and (timestamp_filter==None or timestamp_operator(temp_time, timestamp_filter))):
                if line_limit!=None and (row_count >= line_limit):
                    break
                message_block = json.loads(row.message)
                message = message_block.get('message')
                params = message_block.get('params')
                new_message = message % tuple(params)

                if row.exception != None:
                    exception_block = json.loads(row.exception)
                    exception_message = exception_block.get('type')
                    new_exceptions.append(exception_message)
                else:
                    new_exceptions.append(row.exception)

                new_event_rows.append(row)
                new_timestamps.append(temp_time)
                new_messages.append(new_message)

                if row_count==0:
                    is_row_collapsable.append(0)
                elif new_messages[row_count]==new_messages[row_count-1] and new_event_rows[row_count].run_id == new_event_rows[row_count-1].run_id:
                    is_row_collapsable.append(1)
                    if current_repeated_row == None:
                        current_repeated_row = row_count-1
                        is_row_collapsable[current_repeated_row] = 2
                    number_of_repeats+=1
                else:
                    if current_repeated_row != None:
                        new_messages[current_repeated_row] = "("+str(number_of_repeats)+" counts) "+new_messages[current_repeated_row]
                        current_repeated_row = None
                        number_of_repeats = 1
                    is_row_collapsable.append(0)

                row_count+=1
        if line_limit==None:
            line_limit='all'
        print("Loaded 2!")
        return render_template('log_events.html', rows2 = zip(new_event_rows, new_timestamps, new_messages, new_exceptions, is_row_collapsable), form2=form2, line_limit=str(line_limit))
    else:
        event_rows = Event_Logs.query.all()
        new_timestamps = []
        new_messages = []
        new_exceptions = []
        new_event_rows = []
        is_row_collapsable = []
        row_count = 0
        current_repeated_row = None
        number_of_repeats = 1
        for row in reversed(event_rows):
            if row_count >= 100:
                break

            temp_time = datetime.strptime(time.strftime("%B %d %Y %H:%M:%S", time.localtime(row.timestamp)), "%B %d %Y %H:%M:%S")
            new_timestamps.append(temp_time)

            message_block = json.loads(row.message)
            message = message_block.get('message')
            params = message_block.get('params')
            new_message = message % tuple(params)

            if row.exception != None:
                exception_block = json.loads(row.exception)
                exception_message = exception_block.get('type')
                new_exceptions.append(exception_message)
            else:
                new_exceptions.append(row.exception)
            new_messages.append(new_message)
            new_event_rows.append(row)
            if row_count==0:
                is_row_collapsable.append(0)
            elif new_messages[row_count]==new_messages[row_count-1] and new_event_rows[row_count].run_id == new_event_rows[row_count-1].run_id:
                is_row_collapsable.append(1)
                if current_repeated_row == None:
                    current_repeated_row = row_count-1
                    is_row_collapsable[current_repeated_row] = 2
                number_of_repeats+=1
            else:
                if current_repeated_row != None:
                    new_messages[current_repeated_row] = "("+str(number_of_repeats)+" counts) "+new_messages[current_repeated_row]
                    current_repeated_row = None
                    number_of_repeats = 1
                is_row_collapsable.append(0)
            row_count+=1

        print("Loaded 1!")
        return render_template('log_events.html', rows2 = zip(new_event_rows, new_timestamps, new_messages, new_exceptions, is_row_collapsable), form2=form2, line_limit='100')

@app.route('/log_events/<row_id>', methods=['GET'])
def log_event(row_id):
    row = Event_Logs.query.filter(Event_Logs.id==row_id).one()
    message_block = json.loads(row.message)
    message = message_block.get('message')
    params = message_block.get('params')
    new_message = message % tuple(params)
    stacktrace=None
    exception=None
    extra=None
    if row.exception != None:
        exception = json.dumps(json.loads(row.exception), indent=4, sort_keys=False)
    if row.stacktrace != None:
        stacktrace = json.dumps(json.loads(row.stacktrace), indent=4, sort_keys=False)
    if row.exception != None:
        extra = json.dumps(json.loads(row.extra), indent=4, sort_keys=False)
    new_time = datetime.strptime(time.strftime("%B %d %Y %H:%M:%S", time.localtime(row.timestamp)), "%B %d %Y %H:%M:%S")

    return render_template('log_event.html', row=row, message=new_message, timestamp=new_time, stacktrace=stacktrace, exception=exception, extra=extra)

if __name__ == '__main__':
    app.run(debug=True)
