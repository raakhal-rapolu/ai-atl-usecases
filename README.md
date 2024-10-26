```markdown
# ReCallMe Backend Service

This repository hosts the backend for the ReCallMe project, a Flask-based API providing cognitive assistance features. The system is designed to help dementia patients by integrating face identification, task management, and communication functionalities through API endpoints. This backend can be extended with LLM (Language Model) capabilities for enhanced interactions.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [File Structure](#file-structure)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Overview

The ReCallMe Backend Service uses Flask with the Blueprint pattern to provide an extensible API structure. It supports various features, such as face recognition and task management, making it an ideal solution for dementia patient care and cognitive assistance. This service integrates with third-party AI models and is deployable to Google Cloud Platform.

## Features

- **Face Identification**: Recognizes faces to assist with memory reinforcement.
- **LLM-based Interaction**: Powered by language models for context-based conversation.
- **Task Management**: Helps users manage and keep track of daily tasks.
- **Caregiver Notifications**: Notifies caregivers based on specific triggers or requests.
- **Modular and Extensible**: Utilizes Flask Blueprints for easy extensibility.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/morozovdd/ReCallMe-backend-svc.git
   cd ReCallMe-backend-svc
   ```
2. **Set up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**: Use `pyproject.toml` to install all required libraries.
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Environment variables must be set for specific functionalities:

- `GEMINI_URL`: URL for Gemini service integration.
- `ANTHROPIC_API_KEY`: API key for access to Anthropic’s AI models.

These variables can be configured in the `.env` file for local development.

## File Structure

Here's an overview of the repository's structure:

```
├── webserver
│   ├── endpoints.py
│   ├── face_prompt_llm.py
│   ├── face_identification.py
│   ├── api_models.py
│   ├── __init__.py
├── extensions.py
├── app.py
└── Dockerfile
```

## Usage

### Running the Application:

```bash
flask run
```

The application will be available at `http://127.0.0.1:5000`.

### Docker Deployment:

To deploy using Docker, build and run the container:

```bash
docker build -t recallme-backend .
docker run -p 5000:5000 recallme-backend
```

### Deploy to Google Cloud Platform:

Utilize the provided `deploy.yml` GitHub Actions workflow, configuring your GCP credentials and Artifact Registry.

## Endpoints

The following are key endpoints provided by the backend. Each endpoint’s implementation can be found in `webserver/endpoints.py`:

- `/identify_face` - POST: Processes image input to identify and verify known faces.
- `/generate_response` - POST: Uses LLM to generate context-based responses based on prompts.
- `/tasks` - GET/POST/DELETE: Manage user tasks, including creation, retrieval, and deletion.

Swagger documentation is available to explore the endpoints interactively. Access it via `/swagger` when the app is running.

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Commit your changes and push them to the branch.
4. Open a pull request to contribute.

## License

This project is licensed under the MIT License.

For further details, please visit our GitHub repository. 
```
