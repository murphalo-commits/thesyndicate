# Sportsbook Odds Tracker (Python Automation Setup)

Because Google Sheets (Apps Script) traffic is blocked by Novig's CloudFront firewall due to Google's server user-agent rules, we use a **local Python script** to fetch the data. 

Running this script locally on your PC bypasses the firewall and allows you to fetch **both standard sportsbook odds and detailed Novig order books (liquidity and alternate lines) anonymously, without needing any Novig developer keys!**

---

## 🛠️ Step 1: Install Python & Libraries
1. Download and install [Python](https://www.python.org/downloads/) (make sure to check "Add Python to PATH" during installation).
2. Open your terminal or PowerShell, navigate to this project folder, and run:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Step 2: Set up Google Sheets API Credentials
To allow the Python script to update your Google Sheet in the background, you need to create a free Google Service Account:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "Sportsbook Tracker").
3. In the search bar at the top, search for **Google Sheets API** and click **Enable**.
4. Search for **Google Drive API** and click **Enable**.
5. Go to **IAM & Admin** -> **Service Accounts** in the left sidebar.
6. Click **+ Create Service Account**, give it any name, and click **Create and Continue**, then click **Done**.
7. Click on your newly created service account in the list, go to the **Keys** tab, click **Add Key** -> **Create new key** (select **JSON**), and click **Create**.
8. A JSON file will download. Copy this file into your `sportsbook-odds-tracker` folder, and rename it to exactly **`credentials.json`**.
9. **Crucial Step:** Open the `credentials.json` file, copy the `"client_email"` address (it looks like `your-name@project-id.iam.gserviceaccount.com`), go to your Google Sheet, click **Share** in the top right, and add that email as an **Editor**.

---

## 📊 Step 3: Initialize your Google Sheet
Before running the Python script, your sheet needs to have the correct structure:
1. Open your [Google Sheet](https://docs.google.com/spreadsheets/d/1V03afDSY0tWIbqQAJhOcuv2A13Z9eJoi0XKs9zoc7Nk/edit?usp=sharing).
2. If you haven't already, go to **Extensions** -> **Apps Script**, delete the default code, paste the contents of [`apps_script.js`](file:///C:/Users/Brian/.gemini/antigravity/scratch/sportsbook-odds-tracker/apps_script.js), and save it.
3. Refresh the Google Sheet. Click the new menu item **Sportsbook Tracker** -> **Setup Sheets (First Time)** and authorize it. 
   *(Note: This creates the "Settings", "Odds Data", and "Novig Market Depth" tabs with the checkboxes).*
4. In the **Settings** sheet, enter your Odds API Key (`ea94f855768fa6bf4fbdc4f60074ed11` is already entered) in cell `B2`, select your active sports, and check the books you want to track.

---

## 🚀 Step 4: Run the Tracker
To update your odds and market depth, open your command prompt/terminal and run:
```bash
python odds_tracker.py
```

The script will:
1. Read your API keys and sports selections directly from your Google Sheet's **Settings** tab.
2. Query The Odds API for DraftKings, FanDuel, BetMGM, Caesars, and Fanatics lines.
3. Query Novig's public GraphQL API for detailed order book depth (Back and Lay odds, available bet limits/liquidity, and alternate lines) for your active sports.
4. Overwrite your **Odds Data** and **Novig Market Depth** tabs with the fresh consolidated data.
5. Post a timestamp and success/error status message back into your **Settings** sheet!

---

## ⏰ Step 5: Automate on a Timer (Windows Task Scheduler)
To have this update completely in the background on your PC:
1. Open the Windows Start Menu and search for **Task Scheduler**.
2. Click **Create Basic Task** in the right sidebar.
3. Name it "Sportsbook Odds Tracker".
4. Set the trigger to **Daily** or **When I log on**, and set it to recur as frequently as you want (e.g., under "Advanced settings", check **Repeat task every:** `1 hour` or `4 hours`).
5. Choose **Start a Program**.
   * **Program/script:** type `python`
   * **Add arguments:** type `odds_tracker.py`
   * **Start in:** paste the absolute path to your folder: `C:\Users\Brian\.gemini\antigravity\scratch\sportsbook-odds-tracker`
6. Click **Finish**.
