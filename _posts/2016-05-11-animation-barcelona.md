---
title: Barcelona animation
category: app
layout: page
---

<div id="mapH"></div>
<div id="info" style="display:none; background-color:white; padding:15px; margin:5px"><h2 id="age_name"></h2>:repeat:<input id="toggle" type="button" value="pause"/></div>
<script>
var toggle = document.getElementById("toggle")
toggle.onclick = function(e){
	if(toggle.value=="pause"){
		toggle.value = "play";
	}else{
		toggle.value = "pause";
		loop();
	}
}
</script>

Data from Barcelona opendata "[Age of the population (year by year). Reading register of inhabitants.](http://opendata.bcn.cat/opendata/en/catalog/POBLACIO)".

<script src="{{ "/assets/d3.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/d3plus.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/axios.min.js" | prepend: site.baseurl }}"></script>
<script type="text/javascript">
var hist = d3plus.viz().container("#hist").type("bar").id("name").text("").x("age").y("value");
var histBase = ["#hR", "#hG", "#hB"].map(function(name){
	return d3plus.viz()
		.container(name)
		.type("bar")
		.id("name").x("age").y("value")
		.color("hex");
});

function hex2(i){
	var u = i.toString(16);
	while(u.length < 2){
		u = "0"+u;
	}
	return u;
}

function expand(lkey, base){
	var lkey = new Number(lkey);
	axios.get(base+"_ages.json").then(function(resp){
		for(var r=0; r<resp.data.length; r++){
			var row = resp.data[r];
			if(row.lkey == lkey){
				document.getElementById("lname").innerHTML = row.name;
				document.getElementById("wR").innerHTML = row.wR;
				document.getElementById("wG").innerHTML = row.wG;
				document.getElementById("wB").innerHTML = row.wB;
				var data = [];
				for(var i=0; i<row.ages.length; i++){
					data.push({name:"population", age:i, value:row.ages[i]});
				}
				var hex = "#"+hex2(Math.floor(255*row.R))
					+hex2(Math.floor(255*row.G))
					+hex2(Math.floor(255*row.B));
				hist.data(data)
					.attrs([{"name":"population","hex":hex}])
					.color("hex")
					.draw();
				break;
			}
		}
	});
}

var age_name = document.getElementById("age_name");
var circles = {}
function load(base, prefix){
	age_name.innerHTML=prefix.substring(10,14);
/*
	axios.get("data/"+base+"_rgb.json").then(function(resp){
		var proc = function(data, viz, hex){
			var feed = [];
			for(var i=0; i<data.length; i++){
				feed.push({ age:i, value:data[i], name:"C" });
			}
			viz.data(feed)
				.attrs([{"name":"C","hex":hex}])
				.draw();
		}
		proc(resp.data["R"], histBase[0], "#ff0000");
		proc(resp.data["G"], histBase[1], "#00ff00");
		proc(resp.data["B"], histBase[2], "#0000ff");
	});
*/
	axios.get(base+prefix+"_ages.json").then(function(resp){
		var info = new google.maps.InfoWindow();
		for(lkey in circles){
			circles[lkey].setOptions({
				strokeColor: "white",
				fillColor:"white"
			});
		}
		resp.data.forEach(function(row){
			var c = "rgb("+Math.floor(255*row.R)+","+Math.floor(255*row.G)+","+Math.floor(255*row.B)+")";
			var p = circles[row.lkey];
			if(p){
				p.setOptions({
					strokeColor: c,
					fillColor: c
				});
			} else {
				var name = row.ku+" "+row.cho;
				var pos = new google.maps.LatLng(row.lat, row.lng);
				p = new google.maps.Circle({
					center: pos,
					strokeColor: c,
					strokeOpacity: 0,
					fillColor: c,
					fillOpacity: 0.6,
					radius: 400,
					map: map});
				circles[row.lkey] = p;
			}
		});
	})
}

var files = [
	"barcelona_2007",
	"barcelona_2008",
	"barcelona_2009",
	"barcelona_2010",
	"barcelona_2011",
	"barcelona_2012",
	"barcelona_2013",
	"barcelona_2014",
	"barcelona_2015",
];

var loop_ct = 0;
function loop(){
	if(toggle.value=="play"){
		return;
	}
	new Promise(function(resolve,reject){
		load("{{ "/data/" | prepend: site.baseurl }}", files[loop_ct%files.length]);
		resolve();
	}).then(function(){
		loop_ct++;
		setTimeout(loop, 400)
	});
}

var map;
function initMap() {
	var smt = new google.maps.StyledMapType([{
		'stylers': [
			{'gamma': 0.8 },
			{ 'saturation': -100 },
			{ 'lightness': 20 }
		]
	}], { name: "monochrome" });
	map = new google.maps.Map(document.getElementById('mapH'));
	map.mapTypes.set("mono", smt);
	map.setMapTypeId("mono");
	map.fitBounds(new google.maps.LatLngBounds(
		new google.maps.LatLng(41.370004, 2.0695258),
		new google.maps.LatLng(41.4495761, 2.2280099)));
  var info = document.getElementById("info");
  info.parentNode.removeChild(info);
  info.style.display = "block";
	map.controls[google.maps.ControlPosition.TOP_RIGHT].push(info);

	setTimeout(loop, 400);
}

</script>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBWG7RNe916URO79mZeYBiMFfORHoHQSG4&callback=initMap"></script>


See also
--------
- [はじめに]({{ "/blog/2016/05/13/intro.html" | prepend: site.baseurl }})
