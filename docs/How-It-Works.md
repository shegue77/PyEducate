## ❓ How It Works

PyEducate follows a simple **Host-Server-Client** model that makes lesson delivery seamless and interactive.

1. **Lesson Creation (Host)**

    - The **Host** uses the **Lesson Editor** to create lessons.  
    - Lessons are stored in a **structured JSON format**, making them easy to organize, edit, and share.  
    - Each lesson is **sorted by ID** for consistent ordering and quick retrieval.  

2. **Lesson Hosting (Server Program)**

    - The **Host** runs the **Server Program**, which acts as the bridge between educators and learners.  
    - The server includes a **suite of commands** for sending, receiving, and managing lesson data.  
    - Lessons can be updated or replaced in real time without restarting the server.  

3. **Client Connection**

    - A **Client** connects to the **Host’s server** over the local network.  
    - The client communicates with the server to receive lessons and send back responses or activity data.  

4. **Remote Lesson Delivery**

    - Lessons are transmitted **remotely** from the host’s server to the client.  
    - Once received, lessons are **stored locally** on the client’s device, allowing learners to revisit them anytime — even without an active connection.  

---

💡 **In short:**  
You create lessons on the host machine → the server program manages and serves them → clients connect to receive lessons instantly and interactively.

---

