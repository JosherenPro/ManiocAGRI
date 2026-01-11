from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates/email'
)

async def send_email(subject: str, recipient: str, body: str, template_name: str = None, context: dict = None):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    if template_name:
        await fm.send_message(message, template_name=template_name)
    else:
        await fm.send_message(message)

async def send_welcome_email(email: str, username: str):
    subject = "Bienvenue sur ManiocAgri !"
    body = f"""
    <html>
        <body>
            <h1>Bonjour {username},</h1>
            <p>Votre compte sur <strong>ManiocAgri</strong> a été créé avec succès.</p>
            <p>Il est actuellement en attente d'approbation par un administrateur. Vous recevrez un mail dès que votre accès sera activé.</p>
            <p>Cordialement,<br>L'équipe ManiocAgri</p>
        </body>
    </html>
    """
    await send_email(subject, email, body)

async def send_approval_email(email: str, username: str):
    subject = "Votre compte ManiocAgri a été approuvé !"
    body = f"""
    <html>
        <body>
            <h1>Félicitations {username} !</h1>
            <p>Votre compte sur <strong>ManiocAgri</strong> a été approuvé. Vous pouvez maintenant vous connecter à votre tableau de bord.</p>
            <a href="https://maniocagri.bj/manioc_agri/authentification.html" style="background-color: #198754; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Se connecter</a>
            <p>À bientôt,<br>L'équipe ManiocAgri</p>
        </body>
    </html>
    """
    await send_email(subject, email, body)
