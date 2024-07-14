
#botMenu - Food-Ordering Chatbot Using Python Flask & DialogFlow

#Service Account Setup
Open Dialogflow's console, go to settings ⚙ and find the project ID section with a Google Cloud link. Click the link to open Google Cloud.
In Google Cloud, go to the menu ☰ > APIs & Services > Credentials.
Click ☰ > APIs & Services > Credentials > Create Credentials > Service Account Key.
Under "Create service account key," select "New Service Account" and enter a name. If you have an existing service account, select that instead.
Name the account, assign an appropriate role, and click "Create."
A JSON file will be downloaded to your computer. You'll need this file for the setup.

#Set up Dialogflow DetectIntent Endpoint in the App
Replace the key.json file in the credentials folder with your downloaded JSON file.
In app.py, change GOOGLE_PROJECT_ID = "<YOUR_PROJECT_ID>" to your actual project ID.
 
 
