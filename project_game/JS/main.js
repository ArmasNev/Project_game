// Leaflet map
const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
map.setView([60, 24], 7);


const data = 'http://127.0.0.1:5000/get_airports';
// form for player name

// function to fetch data from API
async function getData() {
  const response = await fetch(data);
  if (!response.ok) throw new Error('Invalid server input!');
  const responseData = await response.json();
        console.log(responseData);
}
getData();

// function to update game status

// function show weather at selected airport

// function to check if any goals have been reached

// function to update event data and event table in UI

// function to check if game is over

// function to set up game (main function) <---
