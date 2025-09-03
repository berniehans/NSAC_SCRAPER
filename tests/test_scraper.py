import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.nsac_scraper.scraper import (
    main,
    save_to_history,
    scrape_challenge_data,
    scrape_single_challenge,
)


# Fixture para limpiar archivos de prueba generados
@pytest.fixture(autouse=True)
def cleanup_files():
    """Limpia los archivos generados antes y después de cada test."""
    files_to_clean = ["data/history.json", "data/teams.json", "data/test_history.json"]
    os.makedirs("data", exist_ok=True)  # Asegura que el directorio 'data' exista

    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)

    yield  # Aquí se ejecuta el test

    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)


# Test para la función save_to_history
def test_save_to_history():
    """Verifica que los datos se guardan y se añaden correctamente al historial."""
    test_data = {
        "timestamp": "2025-01-01T00:00:00Z",
        "challenges": [{"challenge": "Test", "team_count": 10}],
    }
    test_filename = "data/test_history.json"

    # 1. Probar la creación de un nuevo archivo de historial
    save_to_history(test_data, test_filename)
    with open(test_filename, "r", encoding="utf-8") as f:
        history = json.load(f)
    assert len(history) == 1
    assert history[0] == test_data

    # 2. Probar que se añade a un historial existente
    test_data_2 = {
        "timestamp": "2025-01-02T00:00:00Z",
        "challenges": [{"challenge": "Test2", "team_count": 20}],
    }
    save_to_history(test_data_2, test_filename)
    with open(test_filename, "r", encoding="utf-8") as f:
        history = json.load(f)
    assert len(history) == 2
    assert history[1] == test_data_2


# Test de alto nivel para scrape_challenge_data
@pytest.mark.asyncio
@patch("src.nsac_scraper.scraper.asyncio.gather", new_callable=AsyncMock)
@patch("src.nsac_scraper.scraper.scrape_single_challenge", new_callable=AsyncMock)
@patch("src.nsac_scraper.scraper.async_playwright")
async def test_scrape_challenge_data_high_level(
    mock_playwright, mock_scrape_single, mock_gather
):
    """Prueba la orquestación de múltiples scrapers."""
    mock_gather.return_value = [{"challenge": "Result", "team_count": 1}]
    test_urls = ["url1", "url2"]
    test_xpath = "//p"

    results = await scrape_challenge_data(test_urls, test_xpath)

    # Verificaciones
    mock_gather.assert_awaited_once()
    assert mock_scrape_single.call_count == 2
    assert results == [{"challenge": "Result", "team_count": 1}]


# Test unitario para un scrape_single_challenge exitoso
@pytest.mark.asyncio
async def test_scrape_single_challenge_success():
    """Prueba un scrape exitoso usando una URL real de config.json y validaciones flexibles."""
    mock_browser = AsyncMock()
    mock_page = AsyncMock()

    # SOLUCIÓN FINAL: Se usa MagicMock para el locator porque page.locator() es síncrona.
    mock_locator = MagicMock()
    # El método inner_text del locator sí es asíncrono.
    mock_locator.inner_text = AsyncMock(return_value="Currently returning 123 teams")

    # Se configura el mock de la página para que su método síncrono 'locator' devuelva nuestro mock_locator.
    mock_page.locator = MagicMock(return_value=mock_locator)
    mock_browser.new_page.return_value = mock_page

    # Cargar una URL y datos de configuración reales
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    url = config["CHALLENGE_URLS"][0]  # Usar la primera URL del config
    xpath = config["XPATH"]

    expected_slug = url.split("/")[-2]
    expected_challenge_name = expected_slug.replace("-", " ").title()

    # Se mockea la función con reintentos para aislar la lógica de este test unitario
    with patch("src.nsac_scraper.scraper.goto_with_retry", new_callable=AsyncMock):
        result = await scrape_single_challenge(url, xpath, mock_browser)

    # Verificaciones
    assert result["challenge"] == expected_challenge_name
    assert isinstance(result["team_count"], int)
    assert result["team_count"] == 123

    mock_page.locator.assert_called_once_with(f"xpath={xpath}")
    mock_locator.inner_text.assert_awaited_once_with(timeout=5000)
    mock_page.close.assert_awaited_once()


# Test unitario para un scrape_single_challenge con error
@pytest.mark.asyncio
async def test_scrape_single_challenge_error():
    """Prueba el manejo de errores en scrape_single_challenge cuando Playwright falla."""
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.new_page.return_value = mock_page

    url = "https://www.spaceappschallenge.org/2025/challenges/failing-challenge/"
    xpath = "//p"

    # Mockea goto_with_retry para simular un fallo en la carga de la página
    with patch(
        "src.nsac_scraper.scraper.goto_with_retry",
        new_callable=AsyncMock,
        side_effect=Exception("Page timeout"),
    ) as mock_goto:
        result = await scrape_single_challenge(url, xpath, mock_browser)

    # Verificaciones
    assert result["team_count"] == 0
    assert "error" in result
    assert "Page timeout" in result["error"]
    mock_page.close.assert_awaited_once()
    mock_goto.assert_awaited_once()


# Test para la función main
@pytest.mark.asyncio
@patch("src.nsac_scraper.scraper.scrape_challenge_data", new_callable=AsyncMock)
@patch("src.nsac_scraper.scraper.save_to_history")
async def test_main_function(mock_save_to_history, mock_scrape_challenge_data):
    """Prueba la función principal de orquestación."""
    mock_scrape_challenge_data.return_value = [
        {"challenge": "Mocked", "team_count": 99}
    ]

    await main()

    # Verifica que las funciones principales fueron llamadas
    mock_scrape_challenge_data.assert_awaited_once()
    mock_save_to_history.assert_called_once()

    # Verifica que teams.json fue escrito correctamente
    with open("data/teams.json", "r", encoding="utf-8") as f:
        teams_data = json.load(f)

    assert "timestamp" in teams_data
    assert teams_data["challenges"][0]["team_count"] == 99
