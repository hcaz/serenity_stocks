# Serenity Stocks FastAPI Backend

## Running in Development Mode with Docker

To run this FastAPI project in development mode using Docker, follow these steps:

1. **Install Docker Desktop:** Ensure you have Docker Desktop installed on your system.

2. **Build and run the Docker container:** Navigate to the root directory of the project in your terminal and run the following command:

   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Docker image using the `Dockerfile` in the current directory.
   - Start the Docker container in detached mode based on the `docker-compose.yml` configuration.
   - Mount the project directory to the container, allowing for code changes to be reflected without rebuilding the container (hot reloading).
   - Expose port 8000 on your host machine to port 8000 in the container, where the FastAPI application will be running.

3. **Access the application:** Once the container is running, you can access the FastAPI application in your browser at [http://localhost:8000](http://localhost:8000).

4. **Stop the container:** To stop the Docker container, run the following command in your terminal in the project's root directory:

   ```bash
   docker-compose down
   ```

## Development Notes

- The Docker configuration is set up for development purposes with hot reloading enabled. Any changes you make to the code in your project directory will be automatically reflected in the running container.
- The application runs on port 8000 inside the container and is exposed to port 8000 on your host machine.
