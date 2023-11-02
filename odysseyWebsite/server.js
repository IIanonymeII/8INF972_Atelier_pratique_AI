//RUN : "node server.js" dans la console avant de lancer !! 
const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 8081;

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Set up a route to serve your HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'home.html'));
});

// Set up a route to serve your CSS file
app.get('/styles.css', function(req, res) {
  res.setHeader('Content-Type', 'text/css');

  // Read the content of the CSS file and send it in the response
  const cssPath = path.join(__dirname, 'public', 'style.css');
  const cssContent = fs.readFileSync(cssPath, 'utf-8');
  res.send(cssContent);
});

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});