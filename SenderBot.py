import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Dictionary to store user data
user_data = {}

# Telegram bot token
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Define a command handler to set up SMTP details
def set_smtp(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    user_data[user_id]['smtp'] = update.message.text.split('/setsmtp ')[1]
    update.message.reply_text("SMTP server details set. You can now send your email content.")

# Define a function to handle incoming messages
def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in user_data and 'smtp' in user_data[user_id]:
        user_data[user_id]['email_content'] = user_data[user_id].get('email_content', '') + update.message.text + "\n"
        update.message.reply_text("Message added to your email content.")
    else:
        update.message.reply_text("Please set up your SMTP server details first with /setsmtp.")

# Define a command handler to send the email
def send_email(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in user_data and 'smtp' in user_data[user_id] and 'email_content' in user_data[user_id]:
        smtp_details = user_data[user_id]['smtp']
        email_content = user_data[user_id]['email_content']

        smtp_server, smtp_port, smtp_username, smtp_password = smtp_details.split(',')

        with smtplib.SMTP(smtp_server, int(smtp_port)) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)

            subject = "Your subject here"
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = subject
            msg.attach(MIMEText(email_content, 'plain'))

            smtp.sendmail(smtp_username, 'recipient@example.com', msg.as_string())
            del user_data[user_id]  # Clear the user's data
            update.message.reply_text("Email sent successfully!")
    else:
        update.message.reply_text("Please set up your SMTP server details and email content first.")

def main():
    # Initialize the Telegram bot
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set up command handlers
    set_smtp_handler = CommandHandler('setsmtp', set_smtp)
    send_email_handler = CommandHandler('sendemail', send_email)
    dispatcher.add_handler(set_smtp_handler)
    dispatcher.add_handler(send_email_handler)

    # Set up a message handler
    message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
    dispatcher.add_handler(message_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()



