# Camelia UI

The frontend interface for the Camelia image processing application.

## Getting Started

### Prerequisites

-   Node.js (v16 or newer)
-   npm or yarn
-   Python 3.9+ (for the API server)

### How to Launch the UI

Follow these simple steps to start the Camelia web interface:

1. **Start the API server** first, make sure to use the correct environment:

    ```bash
    # From the root directory of the project
    python api.py
    ```

    Leave this terminal window open.

2. **Start the web UI** (in a new terminal):

    ```bash
    # Navigate to the UI directory
    cd camelia-ui

    # Install dependencies (first time only)
    npm install

    # Launch the development server
    npm run dev
    ```

3. **Access the interface**:
    - Open your web browser
    - Navigate to [http://localhost:3000](http://localhost:3000)

The Camelia UI should now be visible and ready to use.

## Troubleshooting

-   If you encounter any errors, make sure both terminal windows show the servers are running
-   Check that ports 3000 (UI) and 5000 (API) are not being used by other applications
-   If you see a "Failed to fetch" error, ensure the API server is running correctly
