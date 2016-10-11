---
title: 待機児童 2016年5～9月
category: app
layout: page
---

<script src="{{ "/assets/marked.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/ansi_up.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/prism.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/notebook.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/axios.min.js" | prepend: site.baseurl }}"></script>

2016年5～9月を動画にしてみました。0 歳が着々と増えていく様子が見えます。

<video controls autoplay loop>
 <source src="{{ "/data/2016-10-05-preschool-waits-by-region.mp4" | prepend: site.baseurl }}" type="video/mp4">
 Your browser does not support the video tag.
</video>

## 手順

<div id="nb"></div>
<script type="text/javascript">
axios.get("https://raw.githubusercontent.com/hkwi/kobe-barcelona/master/notes/2016-10-05-preschool.ipynb").then(function(resp){
document.getElementById("nb").appendChild(nb.parse(resp.data).render());
Prism.highlightAll();
})
</script>
