# Chatbot Using Python Flask & DialogFlow

## REQUIRED LIBRARIES
```
pip install Flask
```
```
pip install dialogflow
```
### Service Account Setup
1. In Dialogflow's console, go to settings ⚙ and under the general tab, you'll see the project ID section with a Google Cloud link to open the Google Cloud console. Open Google Cloud.
2. In the Cloud console, go to the menu icon **☰ > APIs & Services > Credentials**
3. Under the menu icon **☰ > APIs & Services > Credentials > Create Credentials > Service Account Key**.
4. Under Create service account key, select New Service Account from the dropdown and enter. If you already have a service account key, select that. 
5. Give any name for the name and click Create. Give appropriate role.
6. JSON file will be downloaded to your computer that you will need in the setup sections below.

### Set up Dialogflow DetectIntent endpoint to be called from the App
1. Inside root folder, replace the key.json in the credentials folder with your own credentials json file. 
2. In app.py, Change the GOOGLE_PROJECT_ID = **"<YOUR_PROJECT_ID>"** to your project ID

# Demo


https://github.com/user-attachments/assets/850b3ff0-69fe-4b0b-bbeb-ebe945b31274

