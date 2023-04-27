import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def read_secrets(file_path):
    secrets = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            secrets[key] = value
    return secrets

secrets = read_secrets('secrets.txt')

# Replace these with your own Gmail account credentials
sender_email = secrets['SENDER_GMAIL_ACCOUNT']
sender_password = secrets['SENDER_GMAIL_APP_PASSWORD']


def send_email(to_email, subject='', body_html='', body_text=''):
    
    # Replace these with the recipient's email address and the subject of the email
    to_email = to_email
    subject = subject

    # Create the email message with HTML content
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Define the plain text version of the email (optional)
    plain_text = body_text

    # Define the HTML version of the email with formatted text
    html_text = body_html

    # Attach both plain text and HTML versions to the email
    msg.attach(MIMEText(plain_text, 'plain'))
    
    if body_html:
        msg.attach(MIMEText(html_text, 'html'))

    # Send the email using Gmail's SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print('Email sent successfully!')
    except Exception as e:
        print(f'Error sending email: {e}')