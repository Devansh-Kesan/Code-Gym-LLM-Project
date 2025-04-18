### *Firstly ensure that you have installed ollama on your machine and have pulled(hosted) the qwen2.5:7b model in it.*

---

## How to Run the Project

To run the **Code Gym Project**, follow these steps:

### **1. Setup the Environment**

Clone the repository and install the dependencies:

```bash
git clone https://github.com/Devansh-Kesan/Code-Gym-Project.git
```

### **2. Before running following command Please ensure just is already installed in your system**

```bash
just setup  
```

---

### **3. Creating the required docker images(Ensure you have docker desktop already installed)**
Create the images to run python and javascript codes in docker:
```
bash
just build-docker-images
```

### **4. Running the Application**

You can directly run the application using following command:
```bash
just start-all
```
**This will start the prefect,backend and frontend at once and Now you can open `http://localhost:9000` in your browser to view the running application.**

If you want you can also run the backend,frontend and prefect all seperately using following commands.

#### Run the Backend

Start the backend server using FastAPI:
```bash
just start-backend-server
```
This will start the backend server, which powers the core functionality of the system.

#### Run the Frontend

Start the frontend interface using HTML CSS and Javascript:
```bash
just start-frontend-server
```
This will launch the frontend, allowing you to interact with the system via a web interface.

#### Run the Prefect Server

Start the prefect server:
```bash
just start-prefect-server
```
This will launch the Prefect UI, allowing you to interact with and monitor flows through a web-based interface.

**Now open `http://localhost:9000` in your browser to view the running application.**



### **5. Run MkDocs for Documentation**

To view the project documentation locally, run MkDocs:
```bash
just documentation
```
This will start a local server where you can view the project documentation in your browser.
