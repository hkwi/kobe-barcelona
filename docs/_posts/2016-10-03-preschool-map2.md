---
title: 神戸市待機児童マップ分析（０～５歳）
category: app
layout: page
---
## 結果

[Google My Maps](https://drive.google.com/open?id=13Hrm6PNuVKjsQWyNpRsFRPwnLqM&usp=sharing)
に置いてありますので、これで地区を眺めるのが簡単です。

登録元の KML は 
[0歳](http://hkwi.github.io/kobe-barcelona/data/2016-10-03-preschool-0.kml),
[1歳](http://hkwi.github.io/kobe-barcelona/data/2016-10-03-preschool-1.kml),
[2歳](http://hkwi.github.io/kobe-barcelona/data/2016-10-03-preschool-2.kml),
[3歳](http://hkwi.github.io/kobe-barcelona/data/2016-10-03-preschool-3.kml),
[4歳](http://hkwi.github.io/kobe-barcelona/data/2016-10-03-preschool-4.kml),
[5歳](http://hkwi.github.io/kobe-barcelona/data/2016-10-03-preschool-5.kml) にあります。

## 手順

<script src="{{ "/assets/marked.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/ansi_up.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/prism.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/notebook.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/axios.min.js" | prepend: site.baseurl }}"></script>
<div id="nb"></div>
<script type="text/javascript">
axios.get("https://raw.githubusercontent.com/hkwi/kobe-barcelona/master/notes/2016-10-03-preschool-map2.ipynb").then(function(resp){
document.getElementById("nb").appendChild(nb.parse(resp.data).render());
Prism.highlightAll();
})
</script>
