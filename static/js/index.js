const tableBody = document.querySelector('#data-table tbody');
const matrixTableHead = document.querySelector('#matrix-table thead');
const matrixTableBody = document.querySelector('#matrix-table tbody');
const scrapeDateSelect = document.querySelector('#scrape-date');
const runScraperBtn = document.querySelector('#run-scraper');
const scraperStatus = document.querySelector('#scraper-status');
const sortByChallengeBtn = document.querySelector('#sort-by-challenge');
const sortByTeamsBtn = document.querySelector('#sort-by-teams');
const progressBarContainer = document.querySelector('#progress-bar-container');
const progressBar = document.querySelector('#progress-bar');
const exportCsvBtn = document.querySelector('#export-history-csv');
const navLinks = document.querySelectorAll('nav a');

let historicalData = [];
let selectedScrape;

function disableUI() {
    runScraperBtn.disabled = true;
    exportCsvBtn.disabled = true;
    sortByChallengeBtn.disabled = true;
    sortByTeamsBtn.disabled = true;
    scrapeDateSelect.disabled = true;
    navLinks.forEach(link => {
        link.style.pointerEvents = 'none'; // Disable clicks
        link.style.opacity = '0.5'; // Visual cue
    });
}

function enableUI() {
    runScraperBtn.disabled = false;
    exportCsvBtn.disabled = false;
    sortByChallengeBtn.disabled = false;
    sortByTeamsBtn.disabled = false;
    scrapeDateSelect.disabled = false;
    navLinks.forEach(link => {
        link.style.pointerEvents = 'auto';
        link.style.opacity = '1';
    });
}

async function fetchData() {
    try {
        const response = await fetch('/api/data');
        historicalData = await response.json();
        populateDateSelector();
        renderData();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function populateDateSelector() {
    scrapeDateSelect.innerHTML = '';
    historicalData.forEach((scrape, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = new Date(scrape.timestamp).toLocaleString();
        scrapeDateSelect.appendChild(option);
    });
    // Select the latest scrape by default
    scrapeDateSelect.value = historicalData.length - 1;
}

function renderData() {
    const selectedIndex = scrapeDateSelect.value;
    if (!historicalData[selectedIndex]) return;

    selectedScrape = historicalData[selectedIndex];
    renderTable(selectedScrape.challenges);
    renderMatrix();
}

function renderTable(data) {
    tableBody.innerHTML = '';
    data.forEach(challenge => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${challenge.challenge}</td>
            <td>${challenge.team_count}</td>
        `;
        tableBody.appendChild(row);
    });
}



runScraperBtn.addEventListener('click', async () => {
    scraperStatus.textContent = 'Running scraper... please wait.';
    disableUI(); // Disable UI elements
    progressBarContainer.style.display = 'block';
    progressBar.value = 0;

    const response = await fetch('/api/run-scraper');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let receivedLength = 0;

    // This is a simplified progress simulation.
    // A more accurate progress bar would require the scraper to provide progress updates.
    const progressInterval = setInterval(() => {
        progressBar.value += 1;
        if (progressBar.value >= 95) {
            clearInterval(progressInterval);
        }
    }, 500);

    let result = '';
    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }
            result += decoder.decode(value, { stream: true });
        }
        
        clearInterval(progressInterval);
        progressBar.value = 100;

        const jsonResult = JSON.parse(result);
        if (response.ok) {
            scraperStatus.textContent = 'Scraper ran successfully!';
            fetchData(); // Refresh data after scraper runs
        } else {
            scraperStatus.textContent = `Scraper failed: ${jsonResult.error}`;
        }
    } catch (error) {
         scraperStatus.textContent = `An error occurred: ${result}`;
    } finally {
        enableUI(); // Re-enable UI elements
        setTimeout(() => {
            progressBarContainer.style.display = 'none';
        }, 2000);
    }
});

scrapeDateSelect.addEventListener('change', renderData);

sortByChallengeBtn.addEventListener('click', () => {
    const sortedData = [...selectedScrape.challenges].sort((a, b) => a.challenge.localeCompare(b.challenge));
    renderTable(sortedData);
});

sortByTeamsBtn.addEventListener('click', () => {
    const sortedData = [...selectedScrape.challenges].sort((a, b) => b.team_count - a.team_count);
    renderTable(sortedData);
});

// Initial data fetch
fetchData();

exportCsvBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/history-to-csv');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'history.csv';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Error exporting to CSV: ' + response.statusText);
        }
    } catch (error) {
        console.error('Error exporting to CSV:', error);
        alert('Error exporting to CSV.');
    }
});