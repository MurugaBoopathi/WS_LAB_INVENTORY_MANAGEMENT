import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_notification_email(action, item_name, cupboard_name, nt_id,
                            user_email, admin_email, manager_email,
                            sender_email, smtp_config):
    """
    Send email notification when an item is locked/unlocked.

    Parameters
    ----------
    action      : 'unlocked' (borrowed) or 'locked' (returned)
    item_name   : Name of the hardware item
    cupboard_name : Name of the cupboard
    nt_id       : NT ID of the user who performed the action
    user_email  : Email of the user
    admin_email : Admin email
    manager_email : Manager email
    sender_email : Sender (From) email
    smtp_config : dict with server, port, use_tls, username, password
    """

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if action == 'unlocked':
        subject = f"[Lab Inventory] Item Borrowed: {item_name}"
        action_label = "Item Borrowed (Unlocked)"
        action_color = "#e20015"
        person_label = "Borrowed By (NT ID)"
    else:
        subject = f"[Lab Inventory] Item Returned: {item_name}"
        action_label = "Item Returned (Locked)"
        action_color = "#00884b"
        person_label = "Returned By (NT ID)"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto;">
            <div style="background-color: {action_color}; color: white;
                        padding: 15px 20px; border-radius: 5px 5px 0 0;">
                <h2 style="margin: 0;">Lab Inventory Management</h2>
            </div>
            <div style="border: 1px solid #ddd; border-top: none;
                        padding: 20px; border-radius: 0 0 5px 5px;">
                <h3 style="color: {action_color}; margin-top: 0;">{action_label}</h3>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #ddd; width: 40%;">
                            <strong>Action</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {action_label}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>Item</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {item_name}</td>
                    </tr>
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>Location</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {cupboard_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>{person_label}</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {nt_id}</td>
                    </tr>
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>Date &amp; Time</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            {timestamp}</td>
                    </tr>
                </table>
                <br>
                <p style="color: #888; font-size: 12px;">
                    This is an automated notification from
                    Lab Inventory Management Tool.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    # Build email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    recipients = [admin_email, manager_email, user_email]
    msg['To'] = ', '.join(recipients)
    msg.attach(MIMEText(body, 'html'))

    # Send via SMTP
    try:
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        if smtp_config.get('use_tls'):
            server.starttls()
        if smtp_config.get('username') and smtp_config.get('password'):
            server.login(smtp_config['username'], smtp_config['password'])
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        print(f"[EMAIL] Sent successfully: {subject}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        print(f"[EMAIL] Would have sent: {subject} to {recipients}")
        raise
