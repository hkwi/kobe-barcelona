---
title: Barcelona detail
category: app
layout: page
---

<script src="{{ "/assets/d3.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/d3plus.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/axios.min.js" | prepend: site.baseurl }}"></script>
<script>
var data = "{{ "/data" | prepend: site.baseurl }}";
function qs_value(key){
	if(window.location.search.substring(0,1)=="?"){
		var pairs = window.location.search.substring(1).split("&");
		for(var i=0; i<pairs.length; i++){
			var s = pairs[i].indexOf("=");
			if(s < 0){
				if(key == pairs[i]){
					return null;
				}
			}else if(key == pairs[i].substring(0,s)){
				return decodeURIComponent(pairs[i].substring(s+1));
			}
		}
	}
	return null;
}

var area_id = qs_value("area");
if(area_id == null){
	area_id = 1;
} else {
	area_id = parseInt(area_id);
}

function hex2(i){
	var u = i.toString(16);
	while(u.length < 2){
		u = "0"+u;
	}
	return u;
}
function int2(i){
	var u = i.toString(10);
	while(u.length < 2){
		u = "0"+u;
	}
	return u;
}
</script>

<h2 id="area_name"></h2>

他の場所は [picker]({{"/app/2016/05/10/barcelona.html" | prepend: site.baseurl}}) から選択するのが簡単です。

### 年齢別人口 @<span id="pop_date">2015</span>

<div id="pop" style="height:250px; width:500px"></div>

横軸の原点は0歳です。アニメーションで再生することもできます。
:repeat: <input id="pop_play"
 type="button" value="start" onclick="pop_loop_enter()"/>

<script>
var pop = d3plus.viz().container("#pop").type("bar")
	.id("name")
	.y("人数")
	.x("年齢")
	.color("hex");
axios.get(data+"/barcelona_2015_ages.json").then(function(resp){
	resp.data.forEach(function(row){
		if(row.lkey==area_id){
			var data = [];
			for(var i=0; i<row.ages.length; i++){
				data.push({"name":"人口", "人数":row.ages[i], "年齢":i});
			}
			var hex = ["R","G","B"].map(function(a){
				return hex2(Math.floor(255*row[a]));
			}).join("");
			pop.data(data).attrs([{name:"人口","hex":"#"+hex}]).draw();
			document.getElementById("area_name").innerHTML = row.barris;
		}
	});
});

var fs = [
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
function pop_loop_enter(){
	var pop_play = document.getElementById("pop_play")
	if(pop_play.value == "stop"){
		pop_play.value = "start";
	}else{
		pop_play.value = "stop";
		pop_loop();
	}
	return false;
}
var pop_idx = 0;
function pop_loop(){
	var f = fs[pop_idx%fs.length];
	axios.get(data+"/"+f+"_ages.json").then(function(resp){
		resp.data.forEach(function(row){
			if(row.lkey==area_id){
				var data = [];
				for(var i=0; i<row.ages.length; i++){
					data.push({"name":"人口","人数":row.ages[i],"年齢":i});
				}
				var hex = ["R","G","B"].map(function(a){
					return hex2(Math.floor(255*row[a]));
				}).join("");
				pop.data(data).attrs([{name:"人口","hex":"#"+hex}]).draw();
				document.getElementById("pop_date").innerHTML = f.substring(10);
			}
		});
		if(document.getElementById("pop_play").value == "stop"){
			setTimeout(pop_loop, 1000);
		}
	});
	pop_idx++;
	return false;
}
</script>


### 世代構成の変化

<div style="display:flex">
<div id="vec" style="height:300px; width:300px"></div>
<div id="vec_r" style="height:300px; width:400px"></div>
</div>

<script>
var vec = d3plus.viz().container("#vec").type("scatter")
	.id("date")
	.size(5)
	.color("hex")
	.legend(false)
	.x({value:"R",range:[0,1],label:"R（高齢）"})
	.y({value:"G",range:[0,1],label:"G（若年）"});
var vec_r = d3plus.viz().container("#vec_r").type("line")
	.id("name")
	.color("hex")
	.legend(false)
	.x("date")
	.y({value:"G",range:[0,1],label:"G（若年）"});

var vec_proc = 0;
var vec_data = [];
fs.forEach(function(f){
	var date = parseInt(f.substring(10));
	axios.get(data+"/"+f+"_ages.json").then(function(resp){
		vec_proc++;
		resp.data.forEach(function(row){
			if(row.lkey==area_id){
				var hex = ["R","G","B"].map(function(a){
					return hex2(Math.floor(255*row[a]));
				}).join("");
				vec_data.push({"name":date,"date":date,"R":row.R,"G":row.G,"hex":"#"+hex});
				if(fs.length == vec_proc){
					var attrs = vec_data.map(function(d){
						return {"name":d.name,"hex":d.hex}
					});
					vec.data(vec_data).attrs(attrs).draw();
					vec_r.data(vec_data).attrs(attrs).draw();
				}
			}
		});
	});
});
</script>

