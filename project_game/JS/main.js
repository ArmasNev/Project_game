'use strict';

// Leaflet map
const map = L.map('map', {tap: false});
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
map.setView([20, 0], 1);

const data = 'http://127.0.0.1:5000/';
const apiUrl = 'http://127.0.0.1:5000/'
const airportsInRange = 'http://127.0.0.1:5000/airports_in_range';
const pawYellowIcon = L.icon({
    iconUrl: 'CSS/paw_yellow.png',
    iconSize: [15, 15], // size of the icon
    iconAnchor: [-7, -3], // point of the icon which will correspond to marker's location
    popupAnchor: [15, 15] // point from which the popup should open relative to the iconAnchor
});
const pawGreenIcon = L.icon({
    iconUrl: 'CSS/paw_green.png',
    iconSize: [15, 15], // size of the icon
    iconAnchor: [-7, -3], // point of the icon which will correspond to marker's location
    popupAnchor: [15, 15] // point from which the popup should open relative to the iconAnchor
});
const modal1 = document.getElementById("video");
const modal2 = document.getElementById("video2");
const cat = document.getElementById("cat");
const dog = document.getElementById("dog");
const airportMarkers = L.featureGroup().addTo(map);
const buttons = document.querySelector('.buttons')
const markers = {};
const storedButtons = {};

async function getData(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Invalid server input!');
    const data = await response.json();
    return data;
}

// form for player name
document.querySelector('#player-form').addEventListener('submit', function (evt) {
    evt.preventDefault();
    const playerName = document.querySelector('#player-input').value;
    document.querySelector('#player-modal').classList.add('hide');
    gameSetup(`${apiUrl}newgame?name=${playerName}`);
    document.querySelector('#name').textContent = playerName;
    document.querySelector('#time').textContent = '240 Hours';
    document.querySelector('#money').textContent = '10000 ';
    document.querySelector('#dist').textContent = '40000 ';
});

document.addEventListener('click', function (event) {
    if (event.target.id === 'cat') {
        cat.style.width = '35%';
        modal1.style.display = "block";
        document.getElementById("joey").play();
        setTimeout(function () {
            modal1.style.display = "none";
        }, 7000);
    }
    if (event.target.id === 'dog') {
        dog.style.width = '35%';
        modal2.style.display = "block";
        document.getElementById("dogvid").play();
        setTimeout(function () {
            modal2.style.display = "none";
        }, 6000);
    }

});

let currentAirport = null;


// function to fetch data from API
async function gameSetup(url) {
    try {
        airportMarkers.clearLayers();
        const gameData = await getData(url);
        console.log("Game data:", gameData);

        if (!gameData.game_id) {
            throw new Error('Game data does not contain game_id');
        }

        sessionStorage.setItem('game_id', gameData.game_id);
        gameData.airports.forEach(airport => {
            const marker = L.marker([airport.latitude_deg, airport.longitude_deg], {icon: pawYellowIcon}).addTo(map);
            airportMarkers.addLayer(marker);
            markers[airport.ident] = marker;

            let button = document.createElement('button');
            button.className = 'block';
            button.dataset.ident = airport.ident;
            button.appendChild(document.createTextNode(`${airport.ident}, ${airport.name}`));
            buttons.appendChild(button);
            storedButtons[airport.ident] = button;

            button.addEventListener('click', function () {
                flyToAirport(airport.ident);
                currentAirport = {'latitude' : airport.latitude_deg, 'longitude' : airport.longitude_deg}


            });
            const popupContent = `<h4>${airport.name}</h4><button class="button" data-ident="${airport.ident}">Fly here</button>`;
            marker.bindPopup(popupContent);
            button.addEventListener('mouseover', function (evt) {
                marker.setIcon(pawGreenIcon);
            });
            button.addEventListener('mouseout', function (evt) {
                marker.setIcon(pawYellowIcon);
            });
        });
    } catch (error) {
        console.log(error);
    }
}


async function flyToAirport(airportIdent) {
    const game_id = sessionStorage.getItem('game_id');
    if (!game_id) {
        console.error('Game ID not found');
        return;
    }

    try {
        const response = await fetch(`${apiUrl}flyto/${game_id}/${airportIdent}`);
        if (!response.ok) throw new Error('Error during flight operation');
        const responseData = await response.json();
        const weather = await checkWeatherCondition(currentAirport.latitude, currentAirport.longitude);
        console.log(`WEATHER: ${weather.weather[0].id}`);
        removeCurrentLocation(airportIdent);
        if (responseData.status.game_over) {
            alert(responseData.status.game_over_message);
            window.location.href = 'about.html';
        } else if (responseData.status.has_won) {
            const winElement = document.querySelector('.win');
            const winAudio = document.querySelector('.win-audio');
            if (winElement) {
                winElement.style.display = "block";
                winAudio.play();
                setTimeout(function () {
                window.location.href = 'about.html';
            }, 10000);


            } else {
                console.error('Win element not found!');
            }
        } else {
            updateGameStatus(responseData);
            removeCurrentLocation(airport.ident);
        }
    } catch (error) {
        console.error('Error during flight:', error);
    }
}


function updateGameStatus(status) {
    console.log(status)
    document.querySelector('#money').textContent = parseInt(status.status.money);
    document.querySelector('#time').textContent = parseInt(status.status.time) + ' Hours';
    document.querySelector('#dist').textContent = parseInt(status.status.distance);
    document.querySelector('#airport').textContent = ('You are at ' + status.status.location)

    console.log(status.status.event_info)
    if (status.status.event_info) {
        const eventmes = document.querySelector("#event");
        const eventp = document.createElement('p');
        eventp.setAttribute('id', 'eventtext');
        eventmes.appendChild(eventp)
        eventmes.style.display = "block";
        eventp.innerHTML = status.status.event_info
        setTimeout(function () {
            eventmes.style.display = "none";
            eventp.innerHTML = ""
        }, 1500);

    }
}

async function fetchCurrentWeather(lat, lon) {
    try {
        const response = await fetch(`${apiUrl}/get_weather/${lat}/${lon}`);
        return await response.json();
    } catch (error) {
        console.log(`fetchCurrentWeather error: ${error}`);
    }
}
async function updateTime() {
    try {
        const game_id = sessionStorage.getItem('game_id');
        console.log (game_id);
        const response = await fetch(`${apiUrl}/time_update/${game_id}`);

        if (!response.ok) {
            throw new Error(`Error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data);

        return {data};
    } catch (error) {
        console.error('Error:', error);
        return {error};
    }
}

function removeCurrentLocation(currentLocationIdent) {
    // Remove marker
    if (markers[currentLocationIdent]) {
        markers[currentLocationIdent].remove();
        delete markers[currentLocationIdent];
    }

    // Remove button
    if (storedButtons[currentLocationIdent]) {
        storedButtons[currentLocationIdent].parentNode.removeChild(storedButtons[currentLocationIdent]);
        delete storedButtons[currentLocationIdent];
    }
}

async function checkWeatherCondition(lat, lon) {
    const weather = await fetchCurrentWeather(lat, lon);
    const jsonResult = await weather;

    // Display the formatted weather information in the dialog popup
    const dialogElement = document.getElementById('weather-type');
    const pElement = dialogElement.querySelector('p');
    const imgElement = dialogElement.querySelector('img');
    if (weather.weather[0].id >= 500 && weather.weather[0].id <= 622) {
            const updateTimeResult = await updateTime();

            if (updateTimeResult.error) {
                console.error('Error updating time:', updateTimeResult.error);
                pElement.innerHTML = `Weather warning: Storm approaching. Unable to update flight delay information.`;
            } else {
                const delay = updateTimeResult.data.time_reduced_by; 
                pElement.innerHTML = `Weather warning: Storm approaching. Your flight is delayed for ${delay} hours!`;
            }

            imgElement.src = 'https://openweathermap.org/img/wn/10d@2x.png';
            imgElement.alt = 'Icon of a storm';

        setTimeout(function () {
                dialogElement.showModal();
            }, 1500);


    }

    const spanElement = dialogElement.querySelector('span');

    spanElement.addEventListener('click', function (evt) {
        // Close dialog when span is clicked
        dialogElement.close();
    });

    return jsonResult;
}


async function inRange() {
    const response = await fetch(airportsInRange);
    if (!response.ok) throw new Error('Invalid server input!');
    const responseData = await response.json();
}

// function show weather at selected airport

// function to check if game is over
function checkGameOver(money) {
    if (money <= 0) {
        alert(`Game Over: You are out of money! Current balance: ${money} €`);
        return false;
    }
    return true;
}

// function to set up game (main function) <---
