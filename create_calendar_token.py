from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open("calendar_token.json", "w") as token:
        token.write(creds.to_json())

    print("✅ calendar_token.json created successfully")

if __name__ == "__main__":
    main()
