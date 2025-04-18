### *Firstly ensure that you have installed ollama on your machine and have pulled(hosted) the qwen2.5:7b model in it.*

---

## How to Run the Project

To run the **Customer Service Assistant**, follow these steps:

### **1. Setup the Environment**

Clone the repository and install the dependencies:

```bash
git clone https://github.com/AkshayJadhav96/Travel-_Planning_Assistant.git
```

### **2. Setting Up Your `.env` File**
After cloning the repository, you need to configure the environment by adding your API keys. To run this project successfully, you need to create a `.env` file that securely stores your API keys. These keys are required for accessing external services like flights, hotels, weather, and news data.

## Step 1: Create the `.env` File
After cloning the repository, navigate to the **root directory** of the project and create a file named `.env` (this is the full name, no prefix or extension).

---

## Step 2: Get your api keys
### Flights & Hotels (Amadeus API)

1. **Visit**: [Amadeus Developer Portal](https://developers.amadeus.com/)
2. **Sign up** or log in to your account
3. Navigate to: **"My Self-Service Workspace"**
4. **Create a new application**
5. Copy from your dashboard:
   - `API Key` → Use for `FLIGHTS_API_KEY` and `HOTELS_API_KEY`
   - `API Secret` → Use for `FLIGHTS_API_SECRET` and `HOTELS_API_SECRET`

### Weather (WeatherAPI)

1. **Visit**: [WeatherAPI.com](https://www.weatherapi.com/)
2. **Register** for a free account
3. Find your:
   - `API Key` → Use for `WEATHER_API_KEY`

### News (NewsAPI)

1. **Visit**: [NewsAPI.org](https://newsapi.org/)
2. **Sign up** or log in
3. Locate your:
   - `API Key` → Use for `NEWS_API_KEY`

---

### **2. Before running following command Please ensure just is already installed in your system**

```bash
just setup  
```

---

### **3. Running the Application**

#### Run the Backend

Start the backend server using FastAPI:
```bash
just run-fastapi
```
This will start the backend server, which powers the core functionality of the system.

#### Run the Frontend

Start the frontend interface using Streamlit:
```bash
just run-gui
```
This will launch the Streamlit frontend, allowing you to interact with the system via a web interface.


#### Run MkDocs for Documentation

To view the project documentation locally, run MkDocs:
```bash
just run-mkdocs
```
This will start a local server where you can view the project documentation in your browser.

#### Run Ruff for Linting

To check the code for linting issues using Ruff:
```bash
just run-ruff
```
This will analyze the codebase and report any linting errors or warnings.
```