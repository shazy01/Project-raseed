document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000/api';

    // Upload Receipt
    const receiptForm = document.getElementById('receipt-form');
    const receiptResponse = document.getElementById('receipt-response');
    receiptForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('image', document.getElementById('receipt-image').files[0]);

        try {
            const response = await fetch(`${API_BASE_URL}/receipts/`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            receiptResponse.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            receiptResponse.textContent = `Error: ${error}`;
        }
    });

    // Natural Language Query
    const queryForm = document.getElementById('query-form');
    const queryResponse = document.getElementById('query-response');
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const queryText = document.getElementById('query-text').value;

        try {
            const response = await fetch(`${API_BASE_URL}/queries/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: queryText }),
            });
            const data = await response.json();
            queryResponse.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            queryResponse.textContent = `Error: ${error}`;
        }
    });

    // Spending Analysis
    const analysisButton = document.getElementById('analysis-button');
    const analysisResponse = document.getElementById('analysis-response');
    analysisButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/spendinganalysis/`);
            const data = await response.json();
            analysisResponse.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            analysisResponse.textContent = `Error: ${error}`;
        }
    });
});
