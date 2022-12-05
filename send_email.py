
import ssl
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def email_send(filename,cmd):
    try:
        emr = os.getenv('FOFO_EMR')
        cmd = str(cmd)
        print(f'Email send function triggered with cmd {cmd} to email {emr}')

        if emr != '':
            #ems = 'fofo.python.project@gmail.com'
            #email_password =  'aahmxnikceyhfamz'

            ems = os.getenv('FOFO_GMAIL')
            ems_pwd = os.getenv('FOFO_GMAIL_PWD')

            #email_receiver = 'leetsyplakov@gmail.com'


            if cmd =='DetectUnknownFace':
                subject = 'Unknow Face Detected - FOFO'
                body = '''
                FOFO detected unknown face
                '''
            if cmd =='DetectKnownFace':
                subject = 'Know Face Detected - FOFO'
                body = '''
                FOFO detected known face
                '''
            if cmd =='TakePicture':
                subject = 'New Picture Taken - FOFO'
                body = '''
                FOFO took a new picture
                '''

            em = MIMEMultipart()

            em['From'] = ems
            em['To'] = emr
            em['Subject'] = subject
            em.attach(MIMEText(body, "plain"))

            with open(filename, "rb") as attachment:
                # The content type "application/octet-stream" means that a MIME attachment is a binary file
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode to base64
            encoders.encode_base64(part)

            # Add header
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to your message and convert it to string
            em.attach(part)
            text = em.as_string()


            context = ssl.create_default_context()


            with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                smtp.login(ems,ems_pwd)
                smtp.sendmail(ems, emr, text)


            print(f'Email sent to {emr}')

        else:
            print(f'Envalid email address {emr}')

    except Exception as e:
        print(e)

if __name__ == '__main__':
    os.environ['FOFO_EMR'] = 'leetsyplakov@gmail.com'
    os.environ['FOFO_GMAIL'] = 'fofo.python.project@gmail.com'
    os.environ['FOFO_GMAIL_PWD'] = 'aahmxnikceyhfamz'
    fp = 'known_img/22.jpg'
    cmd = 'TakePicture'
    email_send(fp, cmd)

