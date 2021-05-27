const csv = require('csvtojson')
const d3 = require('d3-array')
const fs = require('fs')
const path = require('path')

const converter = csv()
  .fromFile('./gps.csv')
  .then((json) => {
    let data = d3.sort(json, d => +d.id, d => new Date(d.Timestamp))
    
    let car_track = d3.groups(data, d => +d.id)
    let sample_tracks = []

    car_track.map(car => {
      let id = car[0];
      
      let tracks = car[1];
      let stay_periods = [];

      tracks.map((track,i) => {
        if(i){
          let prev_data = new Date(tracks[i-1].Timestamp)
          if(new Date(track.Timestamp) - prev_data > 60*1000 && new Date(track.Timestamp) - prev_data < 60*1000*60*2 ){
            stay_periods.push({
              "stay_begin":tracks[i-1].Timestamp,
              "stay_end":tracks[i].Timestamp,
              lat:tracks[i-1].lat,
              long:tracks[i-1].long
            })
          }
        }
      })
      sample_tracks.push({
        id,
        stay_periods
      })
    })
    fs.writeFile('stay_periods_1.0.json', JSON.stringify(sample_tracks, null, 4), 'utf8', (err) => {
      if (err) {
        throw err;
      }
      console.log('done');
    })
  })