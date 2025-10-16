let map;
let markers = [];

async function fetchData(url) {
  const res = await fetch(url);
  return await res.json();
}

async function loadDashboard() {
  const trips = await fetchData('/api/trips');
  renderCharts(trips);
  initMap(trips);
}

function renderCharts(trips) {
  const ctx1 = document.getElementById('durationChart');
  const ctx2 = document.getElementById('passengerChart');
  const ctx3 = document.getElementById('speedChart');

  // Average duration per day
  const dayDurations = {};
  trips.forEach(t => {
    const day = t.pickup_day_of_week;
    if (!dayDurations[day]) dayDurations[day] = [];
    dayDurations[day].push(t.trip_duration);
  });

  const avgDurations = Object.entries(dayDurations).map(([day, values]) => ({
    day,
    avg: values.reduce((a, b) => a + b, 0) / values.length
  }));

  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: avgDurations.map(d => d.day),
      datasets: [{
        label: 'Avg Trip Duration (sec)',
        data: avgDurations.map(d => d.avg),
        backgroundColor: '#0077cc'
      }]
    }
  });

  // Passenger distribution
  const passengerCount = {};
  trips.forEach(t => {
    passengerCount[t.passenger_count] = (passengerCount[t.passenger_count] || 0) + 1;
  });

  new Chart(ctx2, {
    type: 'pie',
    data: {
      labels: Object.keys(passengerCount),
      datasets: [{
        data: Object.values(passengerCount),
        backgroundColor: ['#0077cc', '#00cc77', '#ff9933', '#cc3366', '#999999']
      }]
    }
  });

  // Average speed by hour
  const hourSpeed = {};
  trips.forEach(t => {
    const hour = new Date(`2000-01-01T${t.pickup_time}`).getHours();
    if (!hourSpeed[hour]) hourSpeed[hour] = [];
    hourSpeed[hour].push(t.trip_speed_kmh);
  });

  const avgSpeed = Object.entries(hourSpeed).map(([hour, values]) => ({
    hour,
    avg: values.reduce((a, b) => a + b, 0) / values.length
  }));

  new Chart(ctx3, {
    type: 'line',
    data: {
      labels: avgSpeed.map(d => d.hour),
      datasets: [{
        label: 'Avg Speed (km/h)',
        data: avgSpeed.map(d => d.avg),
        borderColor: '#ff6600',
        fill: false
      }]
    }
  });
}

function initMap(trips) {
  const center = { lat: 40.75, lng: -73.98 };
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 12,
    center: center
  });

  trips.forEach(t => {
    const pickup = { lat: t.pickup_latitude, lng: t.pickup_longitude };
    const dropoff = { lat: t.dropoff_latitude, lng: t.dropoff_longitude };

    const pickupMarker = new google.maps.Marker({
      position: pickup,
      map: map,
      title: `Pickup: ${t.trip_id}`,
      icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
    });

    const dropoffMarker = new google.maps.Marker({
      position: dropoff,
      map: map,
      title: `Dropoff: ${t.trip_id}`,
      icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    });

    markers.push(pickupMarker, dropoffMarker);
  });
}

document.getElementById('filterBtn').addEventListener('click', async () => {
  const vendor = document.getElementById('vendorSelect').value;
  const passengers = document.getElementById('passengerCount').value;
  const startDate = document.getElementById('startDate').value;
  const endDate = document.getElementById('endDate').value;

  let url = `/api/trips/filter?vendor_id=${vendor}&passenger_count=${passengers}&start_date=${startDate}&end_date=${endDate}`;
  const filtered = await fetchData(url);
  renderCharts(filtered);
  initMap(filtered);
});

loadDashboard();
