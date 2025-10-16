let tripsData = [];
let filteredData = [];
let map;
let markers = [];
let charts = {
    duration: null,
    distance: null,
    speed: null
};

// Fetch trips data from API
async function fetchTripsData() {
    try {
        const response = await fetch("http://127.0.0.1:3000/api/trips");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();

        // Assign fetched data to tripsData and filteredData
        tripsData = data;
        filteredData = [...tripsData];

        populateFilters();
        updateDashboard();
    } catch (error) {
        console.error("Error fetching trips data:", error);
        alert("Failed to load trip data. Please ensure the API is running.");
    }
}

// // Initialize dashboard
// document.addEventListener('DOMContentLoaded', function() {
//     // tripsData = sampleData;
//     filteredData = [...tripsData];

//     populateFilters();
//     updateDashboard();

//     document.getElementById('applyFilters').addEventListener('click', applyFilters);
//     document.getElementById('resetFilters').addEventListener('click', resetFilters);
// });

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function () {
    fetchTripsData(); // Load data from API

    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
});

// Populate filter dropdowns
function populateFilters() {
    const months = [...new Set(tripsData.map(t => t.pickup_month))];
    const days = [...new Set(tripsData.map(t => t.pickup_day_of_week))];
    const vendors = [...new Set(tripsData.map(t => t.vendor_id))];

    const monthFilter = document.getElementById('monthFilter');
    months.forEach(month => {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = month;
        monthFilter.appendChild(option);
    });

    const dayFilter = document.getElementById('dayFilter');
    days.forEach(day => {
        const option = document.createElement('option');
        option.value = day;
        option.textContent = day;
        dayFilter.appendChild(option);
    });

    const vendorFilter = document.getElementById('vendorFilter');
    vendors.forEach(vendor => {
        const option = document.createElement('option');
        option.value = vendor;
        option.textContent = `Vendor ${vendor}`;
        vendorFilter.appendChild(option);
    });
}

// Apply filters
function applyFilters() {
    const monthFilter = document.getElementById('monthFilter').value;
    const dayFilter = document.getElementById('dayFilter').value;
    const distanceFilter = document.getElementById('distanceFilter').value;
    const vendorFilter = document.getElementById('vendorFilter').value;

    filteredData = tripsData.filter(trip => {
        let match = true;

        if (monthFilter && trip.pickup_month !== monthFilter) match = false;
        if (dayFilter && trip.pickup_day_of_week !== dayFilter) match = false;
        if (distanceFilter && trip.trip_distance_category.trim().toLowerCase() !== distanceFilter) match = false;
        if (vendorFilter && trip.vendor_id !== parseInt(vendorFilter)) match = false;

        return match;
    });

    updateDashboard();
}

// Reset filters
function resetFilters() {
    document.getElementById('monthFilter').value = '';
    document.getElementById('dayFilter').value = '';
    document.getElementById('distanceFilter').value = '';
    document.getElementById('vendorFilter').value = '';

    filteredData = [...tripsData];
    updateDashboard();
}

// Update entire dashboard
function updateDashboard() {
    updateStats();
    updateTable();
    updateCharts();
    updateMap();
}

// Update statistics cards
function updateStats() {
    const totalTrips = filteredData.length;
    const avgDistance = filteredData.reduce((sum, trip) => sum + trip.trip_distance_km, 0) / totalTrips || 0;
    const avgDuration = filteredData.reduce((sum, trip) => sum + trip.trip_duration, 0) / totalTrips || 0;
    const avgSpeed = filteredData.reduce((sum, trip) => sum + trip.trip_speed_kmh, 0) / totalTrips || 0;

    document.getElementById('totalTrips').textContent = totalTrips;
    document.getElementById('avgDistance').textContent = avgDistance.toFixed(2);
    document.getElementById('avgDuration').textContent = (avgDuration / 60).toFixed(1);
    document.getElementById('avgSpeed').textContent = avgSpeed.toFixed(1);
}

// Update data table
function updateTable() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    filteredData.forEach(trip => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${trip.trip_id}</td>
            <td>${trip.pickup_datetime}</td>
            <td>${trip.dropoff_datetime}</td>
            <td>${trip.trip_distance_km.toFixed(2)}</td>
            <td>${(trip.trip_duration / 60).toFixed(1)}</td>
            <td>${trip.trip_speed_kmh.toFixed(1)}</td>
            <td>${trip.vendor_id}</td>
        `;
        tbody.appendChild(row);
    });

    document.getElementById('recordCount').textContent = `${filteredData.length} trips found`;
}

// Update charts
function updateCharts() {
    updateDurationChart();
    updateDistanceChart();
    updateSpeedChart();
}

// Duration by weekday chart
function updateDurationChart() {
    const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const durationByDay = {};

    weekdays.forEach(day => {
        const dayTrips = filteredData.filter(t => t.pickup_day_of_week === day);
        if (dayTrips.length > 0) {
            durationByDay[day] = dayTrips.reduce((sum, t) => sum + t.trip_duration, 0) / dayTrips.length / 60;
        } else {
            durationByDay[day] = 0;
        }
    });

    const ctx = document.getElementById('durationChart');

    if (charts.duration) {
        charts.duration.destroy();
    }

    charts.duration = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weekdays,
            datasets: [{
                label: 'Avg Duration (min)',
                data: weekdays.map(day => durationByDay[day]),
                backgroundColor: 'rgba(88, 101, 242, 0.6)',
                borderColor: 'rgba(88, 101, 242, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(88, 101, 242, 0.1)'
                    },
                    ticks: {
                        color: '#8b949e'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(88, 101, 242, 0.1)'
                    },
                    ticks: {
                        color: '#8b949e'
                    }
                }
            }
        }
    });
}

// Distance category pie chart
function updateDistanceChart() {
    const categories = {
        short: 0,
        medium: 0,
        long: 0
    };

    filteredData.forEach(trip => {
        const cat = trip.trip_distance_category.trim().toLowerCase();
        if (categories.hasOwnProperty(cat)) {
            categories[cat]++;
        }
    });

    const ctx = document.getElementById('distanceChart');

    if (charts.distance) {
        charts.distance.destroy();
    }

    charts.distance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Short', 'Medium', 'Long'],
            datasets: [{
                data: [categories.short, categories.medium, categories.long],
                backgroundColor: [
                    'rgba(88, 101, 242, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(236, 72, 153, 0.8)'
                ],
                borderColor: [
                    'rgba(88, 101, 242, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(236, 72, 153, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e6edf3',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Speed by month line chart
function updateSpeedChart() {
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const speedByMonth = {};

    months.forEach(month => {
        const monthTrips = filteredData.filter(t => t.pickup_month === month);
        if (monthTrips.length > 0) {
            speedByMonth[month] = monthTrips.reduce((sum, t) => sum + t.trip_speed_kmh, 0) / monthTrips.length;
        } else {
            speedByMonth[month] = 0;
        }
    });

    const ctx = document.getElementById('speedChart');

    if (charts.speed) {
        charts.speed.destroy();
    }

    charts.speed = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Avg Speed (km/h)',
                data: months.map(month => speedByMonth[month]),
                borderColor: 'rgba(139, 92, 246, 1)',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(139, 92, 246, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(88, 101, 242, 0.1)'
                    },
                    ticks: {
                        color: '#8b949e'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(88, 101, 242, 0.1)'
                    },
                    ticks: {
                        color: '#8b949e'
                    }
                }
            }
        }
    });
}

// Initialize Google Map
function initMap() {
    const mapCenter = { lat: 40.7589, lng: -73.9851 };

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: mapCenter,
        styles: [
            { elementType: 'geometry', stylers: [{ color: '#1d2c4d' }] },
            { elementType: 'labels.text.stroke', stylers: [{ color: '#1a3646' }] },
            { elementType: 'labels.text.fill', stylers: [{ color: '#8ec3b9' }] },
            {
                featureType: 'administrative.locality',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#5865f2' }]
            },
            {
                featureType: 'poi',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#6e9a8f' }]
            },
            {
                featureType: 'poi.park',
                elementType: 'geometry',
                stylers: [{ color: '#263c3f' }]
            },
            {
                featureType: 'poi.park',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#6b9a76' }]
            },
            {
                featureType: 'road',
                elementType: 'geometry',
                stylers: [{ color: '#38414e' }]
            },
            {
                featureType: 'road',
                elementType: 'geometry.stroke',
                stylers: [{ color: '#212a37' }]
            },
            {
                featureType: 'road',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#9ca5b3' }]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry',
                stylers: [{ color: '#746855' }]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry.stroke',
                stylers: [{ color: '#1f2835' }]
            },
            {
                featureType: 'road.highway',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#f3d19c' }]
            },
            {
                featureType: 'transit',
                elementType: 'geometry',
                stylers: [{ color: '#2f3948' }]
            },
            {
                featureType: 'transit.station',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#d59563' }]
            },
            {
                featureType: 'water',
                elementType: 'geometry',
                stylers: [{ color: '#17263c' }]
            },
            {
                featureType: 'water',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#515c6d' }]
            },
            {
                featureType: 'water',
                elementType: 'labels.text.stroke',
                stylers: [{ color: '#17263c' }]
            }
        ]
    });

    updateMap();
}

// Update map markers
function updateMap() {
    if (!map) return;

    markers.forEach(marker => marker.setMap(null));
    markers = [];

    filteredData.forEach(trip => {
        const pickupMarker = new google.maps.Marker({
            position: { lat: trip.pickup_latitude, lng: trip.pickup_longitude },
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 6,
                fillColor: '#5865f2',
                fillOpacity: 0.8,
                strokeColor: '#fff',
                strokeWeight: 2
            },
            title: `Pickup: ${trip.trip_id}`
        });

        const dropoffMarker = new google.maps.Marker({
            position: { lat: trip.dropoff_latitude, lng: trip.dropoff_longitude },
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 6,
                fillColor: '#8b5cf6',
                fillOpacity: 0.8,
                strokeColor: '#fff',
                strokeWeight: 2
            },
            title: `Dropoff: ${trip.trip_id}`
        });

        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="color: #0d1117; padding: 8px;">
                    <strong>${trip.trip_id}</strong><br>
                    Distance: ${trip.trip_distance_km.toFixed(2)} km<br>
                    Duration: ${(trip.trip_duration / 60).toFixed(1)} min<br>
                    Speed: ${trip.trip_speed_kmh.toFixed(1)} km/h
                </div>
            `
        });

        pickupMarker.addListener('click', () => {
            infoWindow.open(map, pickupMarker);
        });

        dropoffMarker.addListener('click', () => {
            infoWindow.open(map, dropoffMarker);
        });

        markers.push(pickupMarker, dropoffMarker);
    });
}

// Make initMap global for Google Maps callback
window.initMap = initMap;