document.addEventListener('DOMContentLoaded', function() {
    initSqlJs({ locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.6.2/${file}` })
        .then(SQL => {
            fetch('../src/sensusmundi.db')
                .then(response => response.arrayBuffer())
                .then(buffer => {
                    const db = new SQL.Database(new Uint8Array(buffer));
                    const result = db.exec(`
                        SELECT watchlist, country, date_added, urls_used
                        FROM watchlist
                        WHERE country = 'NATO'
                        ORDER BY date_added DESC
                        LIMIT 1
                    `);
                    if (result[0] && result[0].values.length > 0) {
                        displayWatchlist(result[0].values[0]);
                    } else {
                        displayNoData();
                    }
                })
                .catch(error => {
                    console.error('Error fetching database:', error);
                    displayError();
                });
        })
        .catch(error => {
            console.error('Error initializing SQL.js:', error);
            displayError();
        });
});

function displayWatchlist(watchlistData) {
    const [watchlist, country, date_added, urls_used] = watchlistData;
    const container = document.getElementById('watchlist-container');
    container.innerHTML = '';

    const date = new Date(date_added).toLocaleDateString('en-GB', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    
    const formattedWatchlist = formatWatchlist(watchlist);

    container.innerHTML = `
        <h2>NATO Watchlist for ${date}</h2>
        <div class="watchlist-content">${formattedWatchlist}</div>
        <h3>Sources</h3>
        <ul class="sources-list">
            ${urls_used.split(',').map(url => `<li><a href="${url.trim()}" target="_blank">${url.trim()}</a></li>`).join('')}
        </ul>
    `;
}

function formatWatchlist(watchlist) {
    const sentences = watchlist.split(/(?<=[.!?])\s+/);
    let formattedText = '';
    let paragraphSentences = [];

    sentences.forEach((sentence, index) => {
        paragraphSentences.push(sentence);

        if ((index + 1) % 3 === 0 || index === sentences.length - 1) {
            formattedText += `<p>${paragraphSentences.join(' ')}</p>`;
            paragraphSentences = [];
        }
    });

    return formattedText;
}

function displayNoData() {
    const container = document.getElementById('watchlist-container');
    container.innerHTML = '<p>No watchlist data available for the UK.</p>';
}

function displayError() {
    const container = document.getElementById('watchlist-container');
    container.innerHTML = '<p>An error occurred while fetching the watchlist data. Please try again later.</p>';
}