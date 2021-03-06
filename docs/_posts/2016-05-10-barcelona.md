---
title: Barcelona picker
category: app
layout: page
---

<div id="map"></div>
<div style="display:flex">
 <div style="width:40%">
  <div id="hR"></div>
  <div>(weight)=<span id="wR">?</span></div>
  <div id="hG"></div>
  <div>(weight)=<span id="wG">?</span></div>
  <div id="hB"></div>
  <div>(weight)=<span id="wB">?</span></div>
 </div>
 <div style="width:60%">
  <div id="lname">Please select a point in the map.</div>
  <div id="hist"></div>
 </div>
</div>

Data from Barcelona opendata "[Age of the population (year by year). Reading register of inhabitants.](http://opendata.bcn.cat/opendata/en/catalog/POBLACIO)".

<script src="{{ "/assets/d3.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/d3plus.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/axios.min.js" | prepend: site.baseurl }}"></script>
<script type="text/javascript">
var base = "{{ "/data/" | prepend: site.baseurl }}";
var hist = d3plus.viz().container("#hist").type("bar").id("name").text("").x("age").y("value");

axios.get(base+"/barcelona_2015_rgb.json").then(function(resp){
	var proc = function(data, frag, hex){
		var feed = [];
		for(var i=0; i<data.length; i++){
			feed.push({ age:i, value:data[i], name:frag });
		}
		d3plus.viz().container(frag)
			.data(feed).type("bar")
			.id("name").x("age").y("value")
			.attrs([{"name":frag,"hex":hex}])
			.color("hex").draw();
	}
	proc(resp.data["R"], "#hR", "#ff0000");
	proc(resp.data["G"], "#hG", "#00ff00");
	proc(resp.data["B"], "#hB", "#0000ff");
});

function hex2(i){
	var u = i.toString(16);
	while(u.length < 2){
		u = "0"+u;
	}
	return u;
}

function expand(lkey){
	var lkey = new Number(lkey);
	axios.get(base+"/barcelona_2015_ages.json").then(function(resp){
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

var map;
function initMap() {
	var smt = new google.maps.StyledMapType([{
		'stylers': [
			{ 'gamma': 0.8 },
			{ 'saturation': -100 },
			{ 'lightness': 20 }
		]
	}], { name: "monochrome" });
	map = new google.maps.Map(document.getElementById('map'));
	map.mapTypes.set("mono", smt);
	map.setMapTypeId("mono");
	map.fitBounds(new google.maps.LatLngBounds(
		new google.maps.LatLng(41.320004, 2.0695258),
		new google.maps.LatLng(41.4695761, 2.2280099)));
	axios.get(base + "/barcelona_2015_ages.json").then(function(resp){
		var info = new google.maps.InfoWindow();
		resp.data.forEach(function(row){
			var c = "rgb("+Math.floor(255*row.R)+","+Math.floor(255*row.G)+","+Math.floor(255*row.B)+")";
			var name = row.barris;
			var pos = new google.maps.LatLng(row.lat, row.lng);
			var p = new google.maps.Circle({
				center: pos,
				strokeColor: c,
				strokeOpacity: 0,
				fillColor: c,
				fillOpacity: 0.6,
				radius: 400,
				map: map});
			google.maps.event.addDomListener(p, "mouseover", function(){
				this.getMap().getDiv().setAttribute("title", row.name);
			});
			google.maps.event.addDomListener(p, "mouseout", function(){
				this.getMap().getDiv().removeAttribute("title");
			});
			google.maps.event.addDomListener(p, "click", function(o){
				info.close();
				info.setPosition(pos);
				info.setContent('<a href="{{ "/app/2016/05/15/barcelona.html" | prepend: site.baseurl }}?area='+row.lkey+'">'+name+"</a><br>"+row.name);
				info.open(map);
				expand(row.lkey);
			});
		});
	})
}
</script>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBWG7RNe916URO79mZeYBiMFfORHoHQSG4&callback=initMap"></script>

See also
--------
- [はじめに]({{ "/blog/2016/05/13/intro.html" | prepend: site.baseurl }})
