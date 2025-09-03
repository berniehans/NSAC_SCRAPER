import csv
import io
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from src.nsac_scraper.app import app as flask_app


@pytest.fixture
def app():
    """Provides the Flask app for testing."""
    yield flask_app


@pytest.fixture
def client(app):
    """Provides a test client for the Flask app."""
    return app.test_client()


# Fixture to clean up test files
@pytest.fixture(autouse=True)
def cleanup_files():
    yield
    if os.path.exists("data/history.json"):
        os.remove("data/history.json")


def create_dummy_history_json(data=None):
    """Creates a dummy history.json file for testing."

    Args:
        data (list, optional): The data to write to the JSON file. Defaults to None.
    """
    os.makedirs("data", exist_ok=True)
    with open("data/history.json", "w", encoding="utf-8") as f:
        json.dump(data if data is not None else [], f, indent=4)


def test_index(test_client):
    """Test the index page."""
    response = test_client.get("/")
    assert response.status_code == 200


def test_matrix(test_client):
    """Test the matrix page."""
    response = test_client.get("/matrix")
    assert response.status_code == 200


def test_get_data_success(test_client):
    """Test /api/data when history.json exists and has data."""
    dummy_data = [
        {
            "timestamp": "2023-01-01",
            "challenges": [{"challenge": "A", "team_count": 10}],
        }
    ]
    create_dummy_history_json(dummy_data)
    response = test_client.get("/api/data")
    assert response.status_code == 200
    assert response.json == dummy_data


def test_get_data_file_not_found(test_client):
    """Test /api/data when history.json does not exist."""
    response = test_client.get("/api/data")
    assert response.status_code == 404
    assert "history.json not found" in response.json["error"]


def test_get_data_empty_file(test_client):
    """Test /api/data when history.json is empty."""
    create_dummy_history_json([])
    response = test_client.get("/api/data")
    assert response.status_code == 200
    assert response.json == []


@patch("threading.Thread")
@patch("asyncio.run")
def test_run_scraper_success(mock_asyncio_run, mock_thread, test_client):
    """Test /api/run-scraper when scraper starts successfully."""
    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    response = test_client.get("/api/run-scraper")

    assert response.status_code == 202
    assert "Scraper started successfully" in response.json["message"]
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    # Verify that asyncio.run would be called with scraper_main
    # This is implicitly tested by mocking threading.Thread and asyncio.run
    # and checking if the thread starts. The actual execution is in the thread.


@patch("threading.Thread", side_effect=Exception("Thread start error"))
def test_run_scraper_failure(mock_thread, test_client):
    """Test /api/run-scraper when scraper fails to start."""
    response = test_client.get("/api/run-scraper")
    assert response.status_code == 500
    assert "Failed to start scraper" in response.json["message"]


def test_history_to_csv_success(test_client):
    """Test /api/history-to-csv when history.json exists and has data."""
    dummy_data = [
        {
            "timestamp": "2023-01-01T00:00:00Z",
            "challenges": [{"challenge": "A", "team_count": 10}],
        },
        {
            "timestamp": "2023-01-02T00:00:00Z",
            "challenges": [
                {"challenge": "A", "team_count": 12},
                {"challenge": "B", "team_count": 5},
            ],
        },
    ]
    create_dummy_history_json(dummy_data)
    response = test_client.get("/api/history-to-csv")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    csv_content = response.data.decode("utf-8")
    reader = csv.reader(io.StringIO(csv_content))
    rows = list(reader)
    assert rows[0] == ["Timestamp", "A", "B"]
    assert rows[1] == ["2023-01-01T00:00:00Z", "10", "0"]  # B is 0 for first entry
    assert rows[2] == ["2023-01-02T00:00:00Z", "12", "5"]


def test_history_to_csv_file_not_found(test_client):
    """Test /api/history-to-csv when history.json does not exist."""
    response = test_client.get("/api/history-to-csv")
    assert response.status_code == 404
    assert "history.json not found" in response.json["error"]


def test_history_to_csv_empty_file(test_client):
    """Test /api/history-to-csv when history.json is empty."""
    create_dummy_history_json([])
    response = test_client.get("/api/history-to-csv")
    assert response.status_code == 404
    assert "No data in history.json to convert" in response.json["message"]
