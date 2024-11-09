import os
import resend
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Fetch the API key from environment variables
resend_api_key = os.getenv("RESEND_API_KEY")
if resend_api_key:
    resend.api_key = resend_api_key
else:
    logging.error("RESEND_API_KEY not found in environment variables")
    raise EnvironmentError("RESEND_API_KEY not found in environment variables")

def send_email(email, reset_url):
    """Send a reset password email."""
    
    # Ensure the reset URL is safe and properly formatted
    if not reset_url.startswith('http'):
        logging.error("Invalid reset URL format: %s", str(reset_url))
        raise ValueError("The reset URL is invalid.")

    # Define the email parameters
    params = {
        "from": "Finance <onboarding@resend.dev>",
        "to": str(email),
        "subject": "Password Reset Request",
        "html": f"<p>Click the link to reset your password: <a href='{str(reset_url)}'>Reset Password</a></p>",
    }

    # Attempt to send the email
    try:
        response = resend.Emails.send(params)
        logging.info(f"Email sent successfully to {email}: {response}")
        return {"message": "Password reset email sent successfully"}
    
    except resend.errors.ResendError as resend_error:
        logging.error("Failed to send email to %s: %s", email, resend_error)
        raise ValueError("Failed to send email due to an issue with Resend service.") from resend_error
    
    except Exception as e:
        logging.error("Unexpected error occurred while sending email: %s", e)
        raise Exception("Unexpected error occurred while sending the password reset email.") from e


