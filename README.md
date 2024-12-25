# 📚 Bluesky Crawler README

Welcome to the **Bluesky Crawler** project! This repository contains tools to interact with the Bluesky API, collecting posts and replies from users, and storing them in a SQLite database.

## 🚀 Summary of Project

The **Bluesky Crawler** is designed to extract and manage data from the Bluesky platform. Using the provided scripts, you can fetch posts from an author’s feed, retrieve replies for specific posts, and store this data in a structured database. This project utilizes Python, SQLAlchemy, and Docker for seamless operation and deployment.

## 🔧 How to Use

1. **Using Docker:**
   You can run the crawler inside a Docker container. First, ensure Docker is installed and running, then use:
    ```bash
    docker-compose run script-runner run_bluesky_crawler.py
    ```

## 💾 Tech Info

-   **Languages & Frameworks**:

    -   Python 3.11
    -   SQLAlchemy for ORM
    -   Requests for HTTP handling

-   **Database**:

    -   SQLite

-   **Containerization**:

    -   Docker, with `Dockerfile` and `docker-compose.yaml` for easy deployment

-   **Project Structure**:

    ```
    scripts/
        bluesky_client.py     # Handles interactions with the Bluesky API
        database_manager.py    # Manages database interactions
        feed_processor.py      # Processes incoming data and stores it
        pyproject.toml         # Dependency management
        run_bluesky_crawler.py # Entry point for the application
    ```

-   **Configuration**:
    -   Use Python's `dotenv` package for environment variables.

Feel free to explore the **Bluesky Crawler** and contribute to the project! If you run into any issues or have suggestions, please open an issue or submit a pull request. Happy coding! 🎉
