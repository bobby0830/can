const googleIt = require('google-it');

googleIt({ 'query': 'AI', 'limit': 5 }).then(results => {
    console.log('Results:', JSON.stringify(results, null, 2));
}).catch(err => {
    console.error('Error:', err);
});
