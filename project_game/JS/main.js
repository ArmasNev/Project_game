'use strict';

// Leaflet map
const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
map.setView([60, 24], 7);

const data = 'http://127.0.0.1:5000/get_airports';
const airportsInRange = 'http://127.0.0.1:5000/airports_in_range';
const blueIcon = L.divIcon({ className: 'blue-icon' });
const greenIcon = L.divIcon({ className: 'green-icon' });
const airportMarkers = L.featureGroup().addTo(map);
const buttons = document.querySelector('.buttons')
// form for player name

// function to fetch data from API
async function getData() {
  const response = await fetch(data);
  if (!response.ok) throw new Error('Invalid server input!');
  const responseData = await response.json();
        console.log(responseData);

    for (let airport of responseData) {
      const marker = L.marker([airport.latitude_deg, airport.longitude_deg]).addTo(map);
      airportMarkers.addLayer(marker);
      marker.setIcon(blueIcon);
      let button = document.createElement('button');
      button.className = 'block';
      button.appendChild(document.createTextNode(airport.name));
      buttons.appendChild(button);
      const popupContent = document.createElement('div');
        const h4 = document.createElement('h4');
        h4.innerHTML = airport.name;
        popupContent.append(h4);
        const goButton = document.createElement('button');
        goButton.classList.add('button');
        goButton.innerHTML = 'Fly here';
        popupContent.append(goButton);
        const p = document.createElement('p');
        p.innerHTML = `Distance ${airport.distance}km`;
        popupContent.append(p);
        marker.bindPopup(popupContent);
        goButton.addEventListener('click', function () {
          gameSetup(`${apiUrl}flyto?game=${data.status.id}&dest=${airport.ident}`);
        });
}}
getData();
setTimeout(function () {
   window.dispatchEvent(new Event("resize"));
}, 500);
setTimeout(map);
async function inRange() {
  const response = await fetch(airportsInRange);
  if (!response.ok) throw new Error('Invalid server input!');
  const responseData = await response.json();}
// function to update game status

// function show weather at selected airport

// function to check if any goals have been reached

// function to update event data and event table in UI

// function to check if game is over

// function to set up game (main function) <---
