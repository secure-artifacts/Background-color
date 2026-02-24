# Background Color Viewer (彩色背景提取工具)

This is a Python-based desktop application built with `customtkinter`. It allows users to view, categorize, and extract Facebook background colors.

## Features

- **Background Synchronization**: Automatically fetching and synchronizing the latest background data.
- **Categorization**: View backgrounds neatly organized into different categories.
- **Favorites System**: You can favorite specific backgrounds, and view all locally saved favorites in a dedicated section.
- **Modern UI**: Clean and modern UI with responsive dark/light mode system.

## How to Run Locally

### Requirements

Ensure you have Python 3 installed. Then install the dependencies:

```bash
pip install customtkinter
```

### Starting the Application

Run the main file to start the application:

```bash
python main.py
```

## How to Build the Application

If you want to package the application into a standalone executable:

1. Double-click the `build.bat` script, or run it from your command line:
    ```bash
    build.bat
    ```
2. Wait for the standard build process to complete.
3. Once completed, your application executable will be located in the `dist/` directory.

## Usage

1. Launch the application.
2. Wait for the Initial data fetch to complete.
3. Click on the categories on the left Sidebar to browse backgrounds.
4. Click on a background to copy its detail or interact with it.
5. All your favorites are automatically saved to `favorites.json` and persist across sessions.
