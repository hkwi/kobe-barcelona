---
title: 神戸市待機児童
category: app
layout: page
---

<script src="{{ "/assets/marked.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/ansi_up.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/prism.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/notebook.min.js" | prepend: site.baseurl }}"></script>
<script src="{{ "/assets/axios.min.js" | prepend: site.baseurl }}"></script>
<div id="nb"></div>
<script type="text/javascript">
axios.get("https://raw.githubusercontent.com/hkwi/kobe-barcelona/master/notes/2016-10-01-preschool.ipynb").then(function(resp){
document.getElementById("nb").appendChild(nb.parse(resp.data).render());
Prism.highlightAll();
})
</script>
