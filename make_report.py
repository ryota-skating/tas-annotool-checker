import json
from pathlib import Path
from string import Template

REPORT_JSON = Path("output/report")
REPORT_HTML = Path("output/report-html")

HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Annotation Report - $annotator</title>
<style>
body{font-family:sans-serif;margin:30px}
.controls{margin-bottom:20px}
.video{margin-bottom:25px;border-top:1px solid #ccc;padding-top:10px}
.segment{padding:4px;margin:2px;white-space:pre-wrap}
.confusable{background:#fff3cd}
.overflow{background:#f8d7da}
.multi{background:#d1ecf1}
</style>
</head>
<body>
<h1>Annotator: $annotator</h1>

<div class="controls">
<label><input type="checkbox" id="show_confusable" checked> ラベルミス</label>
<label><input type="checkbox" id="show_overflow" checked> 範囲過剰</label>
<label><input type="checkbox" id="show_multi" checked> 複数に跨ったラベル</label>
<br><br>
<label>余分なフレーム数の閾値:
<input type="number" id="overflow_threshold" value="0" style="width:80px">
</label>
</div>

<div id="report"></div>

<script>
const data=$json_data;

function render(){
 const showConf=document.getElementById("show_confusable").checked;
 const showOverflow=document.getElementById("show_overflow").checked;
 const showMulti=document.getElementById("show_multi").checked;
 const threshold=parseInt(document.getElementById("overflow_threshold").value||0);
 const container=document.getElementById("report");
 container.innerHTML="";

 data.videos.forEach(video=>{
  const section=document.createElement("div");
  section.className="video";

  const title=document.createElement("h2");
  title.textContent="動画 "+video.number+" ("+video.title+")";
  section.appendChild(title);

  if(showConf){
   video.confusable_label.forEach(e=>{
    const div=document.createElement("div");
    div.className="segment confusable";
    div.textContent=
     "frame "+e.target_segment[0]+"-"+e.target_segment[1]+" : \\n"
     +"  - "+e.target_label+" は "+e.correct_label+" の可能性";
    section.appendChild(div);
   });
  }

  if(showOverflow){
   video.long_segment_overflow.forEach(e=>{
    if(e.extra_frames<threshold) return;
    const div=document.createElement("div");
    div.className="segment overflow";
    div.textContent=
     "frame "+e.target_segment[0]+"-"+e.target_segment[1]+" : \\n"
     +"  - "+e.label+" の範囲が長すぎる可能性";
    section.appendChild(div);
   });
  }

  if(showMulti){
   video.long_segment_multi_label.forEach(e=>{
    const div=document.createElement("div");
    div.className="segment multi";
    const ranges=e.contained_correct_segments
      .map(x=>"    - "+x.label+" ("+x.range[0]+"-"+x.range[1]+")")
      .join("\\n");
    div.textContent=
      "frame "+e.target_segment[0]+"-"+e.target_segment[1]+" : \\n"
      +"  - "+e.label+" は複数のラベルに分かれる可能性：\\n"+ranges;
    section.appendChild(div);
   });
  }

  container.appendChild(section);
 });
}

document.querySelectorAll("input").forEach(x=>x.addEventListener("change",render));
render();
</script>
</body>
</html>
""")

def generate():
    REPORT_HTML.mkdir(exist_ok=True)
    for path in REPORT_JSON.glob("*.json"):
        with open(path) as f:
            data=json.load(f)
        html=HTML_TEMPLATE.substitute(
            annotator=data["annotator"],
            json_data=json.dumps(data)
        )
        out=REPORT_HTML/(path.stem+".html")
        with open(out,"w") as f:
            f.write(html)
        print("created",out)

if __name__=="__main__":
    generate()