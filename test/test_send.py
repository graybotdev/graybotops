from app.email_sender_oauth import send_email

if __name__ == "__main__":
    result = send_email(
        "graybot@graybotops.com",  # Replace if needed
        "GrayBot V2 OAuth Test Email",
        "This email was sent using OAuth 2.0!"
    )
    print("✅ Email sent successfully:")
    print(result)
