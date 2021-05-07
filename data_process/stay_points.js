const csv = require('csvtojson')
const d3 = require('d3-array')
const fs = require('fs'),path = require('path');

const converter = csv()
  .fromFile('./gps.csv')
  .then((json) => {
    let data = d3.sort(json, d=>+d.id, d=>new Date(d.Timestamp))
    
    let car_track = d3.groups(data, d => +d.id)
    let sample_tracks = [];
    console.log(car_track)

    car_track.map(car=>{
      let id = car[0];
      
      let tracks = car[1];
      let stay_points = [];
      tracks.map((track,i)=>{
        if(i){
          let prev_date = new Date(tracks[i-1].Timestamp);
          if(new Date(track.Timestamp) - prev_date > 60*1000){
            stay_points.push({
              Timestamp:tracks[i-1].Timestamp,
              lat: tracks[i-1].lat,
              long: tracks[i-1].long
            });
          }
        }
      })
      sample_tracks.push({
        key: id,
        stay_points: stay_points
      })
  })
  fs.writeFile('stay_points.json', JSON.stringify(sample_tracks), 'utf8', (err)=>{
    if(err) throw err;
    console.log('done')
  })
})



