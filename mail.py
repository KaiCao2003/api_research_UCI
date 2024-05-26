import smtplib
from email.mime.text import MIMEText
from email.header import Header


def __send_email(type: str, receivers: [str], code, time=None):

    # Email Settings Here

    if type == "New":
        subject = f'Subscribe to {code}'
        msg = """
        <p>Greetings,</p>
        <p>You have successfully subscribed to class <i><u>""" + code + """.</p>
        <p>
            When the status of this class changes from FULL to OPEN or when a waitlist
            spot becomes available, you will receive a notification email. </i></u>
        </p>
        <p>Thank you.</p>
        """
    elif type == "Update":
        subject = f'Updates for class {code}'
        msg = """
            <p>Greetings,</p>
            <p>
                There are some updates for class <i><u>""" + code + """<i/><u/>. There may be open seats or waitlist
                spots available.
            </p>
            <p>Please check.</p>
            <p>You won't receive any other emails.</p>
            <p>Thank you.</p>
            """
    elif type == "Error":
        mail_user = "BACKUPUSER"
        mail_pass = ""

        receivers = ", ".join(receivers)

        subject = f'UCI_Reg API Not Able to Send Email'
        msg = ("<p>Fail to send email for </p> <p>code:</p>" + code
               + "<p>at: </p>" + time
               + "<p>To: </p>" + receivers)
    else:
        return False

    message = MIMEText(msg, 'html')
    message['From'] = Header("YOU")
    message['To'] = Header("")

    message['Subject'] = Header(subject)

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        return True
    except smtplib.SMTPException:
        return False


def confirmation_email(receivers: [str], code):
    result = __send_email('New', receivers, code)
    return result


def update_email(receivers: [str], code):
    result = __send_email('Update', receivers, code)
    return result


def fail_email(code, receivers, time):
    result = __send_email('Error', receivers, code, time=time)
    return result