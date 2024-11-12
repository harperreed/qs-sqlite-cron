# 📚 Bluesky Crawler README

Welcome to the **Bluesky Crawler** project! This repository contains tools to interact with the Bluesky API, collecting posts and replies from users, and storing them in a SQLite database. 

## 🚀 Summary of Project

The **Bluesky Crawler** is designed to extract and manage data from the Bluesky platform. Using the provided scripts, you can fetch posts from an author’s feed, retrieve replies for specific posts, and store this data in a structured database. This project utilizes Python, SQLAlchemy, and Docker for seamless operation and deployment.

## 🔧 How to Use

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/harperreed/bluesky-crawler.git
   cd bluesky-crawler/scripts
   ```

2. **Setup Environment:**
   Ensure you have Python 3.11 or later installed. It's recommended to use a virtual environment.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r pyproject.toml
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root of your project and set the following variables:
   ```
   BLUESKY_ACTOR=your_actor_name
   DATABASE_DIRECTORY=path_to_your_database_directory
   POSTS_TO_GRAB=5  # Default is 5
   ```

5. **Run the Crawler:**
   To execute the crawler, run:
   ```bash
   python run_bluesky_crawler.py
   ```
   This will fetch the latest posts from the Bluesky API and store them in the specified SQLite database.

6. **Using Docker:**
   Alternatively, you can run the crawler inside a Docker container. First, ensure Docker is installed and running, then use:
   ```bash
   docker-compose up --build
   ```

## 💾 Tech Info

- **Languages & Frameworks**: 
  - Python 3.11
  - SQLAlchemy for ORM
  - Requests for HTTP handling

- **Database**: 
  - SQLite

- **Containerization**:
  - Docker, with `Dockerfile` and `docker-compose.yaml` for easy deployment

- **Project Structure**:
    ```
    scripts/
        bluesky_client.py     # Handles interactions with the Bluesky API
        database_manager.py    # Manages database interactions
        feed_processor.py      # Processes incoming data and stores it
        pyproject.toml         # Dependency management
        run_bluesky_crawler.py # Entry point for the application
    ```

- **Configuration**: 
    - Use Python's `dotenv` package for environment variables.

Feel free to explore the **Bluesky Crawler** and contribute to the project! If you run into any issues or have suggestions, please open an issue or submit a pull request. Happy coding! 🎉
