const URL = 'http://127.0.0.1:3000/';
const totalTrips = document.getElementById('TotalTrips');
const highSpeed = document.getElementById('HighSpeed');
const longDistance = document.getElementById('Longdistance');
const select = document.getElementById('dataSelect');

fetch(`${URL}api/trips`)
  .then(res => res.json())
  .then(data => {
    totalTrips.innerText = data.length;

    
    const highestSpeed = Math.max(...data.map(trip => trip.trip_speed_kmh || 0));
    highSpeed.innerText = `${highestSpeed} km/h`;

    
    const longestDuration = Math.max(...data.map(trip => trip.trip_duration || 0));
    longDistance.innerText = `${longestDuration} sec`;
  
    if (data.length > 0) {
    //   const keys = Object.keys(data[0]); // get all keys of the first object
    const keys = [        
        "dropoff_datetime",
        "dropoff_latitude",
        "dropoff_longitude",
        "passenger_count" ,
        "pickup_datetime", 
        "pickup_day_of_week",
        "pickup_latitude",
        "pickup_longitude",
        "pickup_month",
        "pickup_time",
        "trip_distance_category",
        "trip_distance_km",
        "trip_duration"
        ]; // specify the keys you want to include

      // Add default option
      const defaultOption = document.createElement('option');
      defaultOption.value = '';
      defaultOption.textContent = 'Select option';
      select.appendChild(defaultOption);

      // Add each key as an option
      keys.forEach(key => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = key;
        select.appendChild(option);
      });
    } else {
      select.innerHTML = '<option>No data found</option>';
    }
  })
  .catch(err => console.error('Error fetching trips:', err));
