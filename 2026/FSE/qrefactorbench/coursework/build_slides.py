"""Build an eight-slide editable PPTX, PDF preview and PNGs without new packages.

Uses the existing Pillow installation for previews and stdlib OOXML for PowerPoint.
Content comes from this coursework implementation and saved local execution evidence.
"""

from pathlib import Path
from xml.sax.saxutils import escape
import json
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "coursework/slides"
BG, PANEL, TEXT, MUTED, CYAN, AMBER = "0C1425", "18263C", "F1F6FF", "A8B7CD", "54E0C0", "FFC878"
CN = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
EMU = 7620  # 1600 x 900 pixels -> 13.333 x 7.5 inches


class Slide:
    def __init__(self, title: str, section: str, number: int, brand="QREFACTOR",
                 footer="课程原型 · 历史 AI 分析回放 + 实际本地模拟 · 不宣称量子加速"):
        self.objects = []
        self.number = number
        self.rect(0, 0, 1600, 900, BG)
        self.text(65, 30, 1300, 27, f"{brand}  /  AI PROGRAMMING  /  {section}", 19, CYAN)
        if title:
            self.text(65, 90, 1470, 90, title, 52)
        self.rect(65, 850, 1470, 1, "304057")
        self.text(65, 866, 1350, 23, footer, 18, MUTED)
        self.text(1460, 864, 80, 25, f"{number:02d} / 08", 19, CYAN)

    def rect(self, x, y, w, h, color=PANEL):
        self.objects.append(dict(kind="rect", x=x, y=y, w=w, h=h, color=color))

    def text(self, x, y, w, h, text, size=30, color=TEXT, mono=False):
        font_path = MONO if mono else CN if any('\u4e00' <= c <= '\u9fff' for c in text) else EN
        font = ImageFont.truetype(font_path, size)
        lines = []
        for paragraph in text.split("\n"):
            line = ""
            for char in paragraph:
                if line and font.getlength(line + char) > w:
                    lines.append(line)
                    line = ""
                line += char
            lines.append(line)
        if ((len(lines) - 1) * 1.32 + 1) * size > h + 1:
            raise ValueError(f"Slide {self.number} text overflow: {text[:60]}")
        self.objects.append(dict(kind="text", x=x, y=y, w=w, h=h, color=color,
                                 size=size, lines=lines, font_path=font_path, mono=mono))

    def card(self, x, y, w, h, title, body, accent=CYAN):
        self.rect(x, y, w, h)
        self.rect(x, y, 5, h, accent)
        self.text(x+24, y+22, w-48, 62, title, 33, accent)
        self.text(x+24, y+94, w-48, h-106, body, 27)

    def image(self, x, y, w, h, path):
        self.objects.append(dict(kind="image", x=x, y=y, w=w, h=h, path=Path(path)))

    def preview(self):
        im = Image.new("RGB", (1600, 900), "#" + BG)
        draw = ImageDraw.Draw(im)
        for o in self.objects:
            x, y, w, h = [o[k] for k in ("x", "y", "w", "h")]
            if o["kind"] == "rect":
                draw.rectangle((x, y, x+w, y+h), fill="#"+o["color"])
            elif o["kind"] == "image":
                asset = Image.open(o["path"]).convert("RGBA").resize((w, h))
                im.paste(asset, (x, y), asset)
            else:
                font = ImageFont.truetype(o["font_path"], o["size"])
                for index, line in enumerate(o["lines"]):
                    draw.text((x, y + index * o["size"] * 1.32), line,
                              font=font, fill="#"+o["color"], anchor="lt")
        return im


def slides():
    report = json.loads((ROOT / "demo/artifacts/first_run.json").read_text())
    measured = report["execution_checks"][0]["resources"]
    s = []
    p = Slide("", "COURSE PROJECT", 1); s.append(p)
    p.text(65, 150, 950, 95, "QRefactor", 76, CYAN)
    p.text(65, 270, 870, 205, "AI 辅助的\n选择性量子程序重构", 64)
    p.text(65, 510, 850, 115, "识别可以改的部分，保留不该改的部分，\n用实际运行检查原软件行为。", 31, MUTED)
    p.text(65, 724, 840, 85, "Python + Qiskit + 本地交互界面\nAI Programming 编程大作业", 28)
    for y, a, b in [(170,"WHERE","定位计算区域"),(335,"WHETHER","判断适用与保留"),(500,"HOW","描述条件量子方案")]:
        p.card(1060,y,475,140,a,b)
    p.text(1084, 700, 420, 80, "可运行代码 + 8 页答辩\n真实模拟，无需 API Key", 28, AMBER)

    p = Slide("问题：计算很慢，就应该量子化吗？", "MOTIVATION", 2); s.append(p)
    p.card(65,205,700,405,"案例 A · 布尔赋值是否存在", "枚举 2ⁿ 个赋值，检查是否满足所有子句。\n\n潜在映射：谓词 → oracle → Grover。\n\n软件要求：返回精确 True / False。")
    p.card(795,205,740,405,"案例 B · 顺序哈希与审计", "每次结果依赖前一次 digest，\n并触发有顺序要求的外部回调。\n\n保留经典实现，不能丢弃可观察副作用。", AMBER)
    p.text(65,660,1470,75,"核心原则：结构上能映射 ≠ 实际值得采用",43,CYAN)
    p.text(65,745,1470,65,"课程目标：接通理解、计划、实现与验证，展示可解释的选择过程。",30,MUTED)

    p = Slide("AI 的作用：提出方案，代码与检查落实约束", "AI ROLE", 3); s.append(p)
    p.card(65,210,460,310,"程序分析", "历史 gpt-5.6-sol / high 输出\n\n候选区域、计算意图、\n结构与实用性判断。")
    p.card(550,210,465,310,"条件计划", "结构 YES 时描述 HOW，\n即使最终建议保留经典。\n\n输出为可检查的 JSON。")
    p.card(1040,210,495,310,"AI 辅助开发", "本次用 Codex 编写\nQiskit 实现、界面与测试。\n\n运行时使用确定性检查。")
    p.rect(65,565,1470,236)
    p.text(92,593,600,70,"0 → 8",58,CYAN)
    p.text(420,600,1050,74,"历史诊断中，8 个结构 YES 回答的非空计划数",30)
    p.text(92,687,1360,85,"只改变“无论是否采用，都给条件计划”的指令；结果提示输出受任务分解影响。\n这是已完成的配对诊断，不是本作业新跑的实验，也不证明计划正确。",25,MUTED)

    p = Slide("代码结构：一条小而完整的演示流程", "IMPLEMENTATION", 4); s.append(p)
    boxes=[(65,"浏览器交互","coursework/index.html\n\n选择公式 / 修改输入\n展示分布与兜底路径"),
           (560,"本地 Python 服务","coursework/app.py\n\n只接收有界 JSON 数据\n拒绝非法输入；无代码执行 API"),
           (1055,"量子混合核心","demo/hybrid_search.py\n\n可逆 oracle + Grover\n测量验证 + 精确经典兜底")]
    for x,t,b in boxes: p.card(x,215,480,335,t,b)
    p.text(510,345,50,55,"→",40,CYAN);p.text(1005,345,50,55,"→",40,CYAN)
    p.card(65,595,715,195,"复用原有代码", "原经典函数、语义比较、Qiskit 资源提取。")
    p.card(805,595,730,195,"无服务依赖", "离线界面，本地 CPU 模拟；本次无模型调用。", AMBER)

    p = Slide("核心实现：用验证与兜底守住精确结果", "CORE ALGORITHM", 5); s.append(p)
    p.rect(65,205,795,588)
    p.text(93,232,735,59,"从程序条件构造量子电路",34,CYAN)
    p.text(93,317,735,425,"H 初始化候选空间\n    ↓\n计算各子句 → 全满足时相位翻转\n    ↓\n反计算辅助位 → 扩散操作\n    ↓\n抽样候选 → 原 satisfies 验证",32)
    p.text(905,219,630,66,"保留原函数接口",33,CYAN)
    p.rect(895,310,640,296)
    code="def has_assignment(n, clauses):\n    samples = quantum_search(...)\n    for candidate in samples:\n        if satisfies(candidate, clauses):\n            return True\n    return original_has_assignment(...)"
    p.text(918,337,590,240,code,23,mono=True)
    p.text(905,637,625,145,"上方为控制逻辑简图；实际实现见源码。\n没测到解，不等于无解。\n经典兜底可能消除潜在收益。",29,AMBER)

    p = Slide("实际演示：点击运行，查看候选与资源", "LIVE DEMO", 6); s.append(p)
    p.image(65,192,900,641,ROOT / "coursework/artifacts/browser-search.png")
    p.card(995,205,540,195,"有解输入", "x₁ ∧ x₂ ∧ x₃\n验证候选 111，返回 True。")
    p.card(995,425,540,195,"无解输入", "x₁ ∧ ¬x₁\n回退原穷举，认证返回 False。",AMBER)
    p.text(1015,664,500,120,f"示例：{measured['num_qubits']} qubits / depth {measured['depth']}\nCX {measured['two_qubit_gate_count']} / 16 shots\n均为分解电路统计，非硬件成本。",28,MUTED)

    p = Slide("验证：检查实现行为，而不是只看能否运行", "VALIDATION", 7); s.append(p)
    for x,num,title in [(65,"13","量子 demo 测试"),(565,"7","课程界面后端测试"),(1065,"144","oracle 基态检查")]:
        p.rect(x,205,470,190);p.text(x+27,223,420,99,num,72,CYAN);p.text(x+27,328,420,50,title,29)
    p.card(65,435,710,353,"覆盖了什么", "有解、无解、空输入与重复文字；\n测量漏解时仍返回精确结果；\n辅助位复位、相位正确性；\n回调顺序与异常传播。")
    p.card(805,435,730,353,"证据边界", "浏览器实际执行 SAT / UNSAT，\n检查非法输入与经典保留路径。\n\n有限测试 ≠ 一般正确性证明；\n模拟器运行 ≠ 量子加速证据。",AMBER)

    p = Slide("交付与总结：先做成可解释、可验证的原型", "DELIVERABLES", 8); s.append(p)
    p.card(65,210,720,325,"可以现场打开的作品", "代码：经典函数 + Qiskit 混合实现\n交互：本地页面 + 原终端 demo\n证据：测试、真实截图、JSON 报告\n汇报：8 页 PPT + PDF + 讲稿")
    p.card(815,210,720,325,"当前边界与下一步", "分析使用已保存 AI 回答；\n不是任意程序的自动转译器。\n\n下一步：依据课程要求与反馈，\n再选择实时分析或更多验证。",AMBER)
    p.text(65,590,1470,80,"bash scripts/run_coursework.sh",40,CYAN,mono=True)
    p.text(65,689,1470,67,"浏览器打开 http://127.0.0.1:8765",34)
    p.text(65,771,1470,46,"收获：把 AI 提案变成可检查的程序行为，同时明确保留不确定性。",29,MUTED)
    return s


def rels(entries):
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{t}" Target="{v}"/>' for i,t,v in entries)+'</Relationships>'


def tree():
    return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'


def write_pptx(pages, path):
    overrides=[('/ppt/presentation.xml','presentation.main'),('/ppt/slideMasters/slideMaster1.xml','slideMaster'),('/ppt/slideLayouts/slideLayout1.xml','slideLayout')]
    overrides += [(f'/ppt/slides/slide{i}.xml','slide') for i in range(1,len(pages)+1)]
    content='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'+''.join(f'<Override PartName="{p}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{t}+xml"/>' for p,t in overrides)+'<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',content)
        z.writestr('_rels/.rels',rels([('rId1','officeDocument','ppt/presentation.xml')]))
        z.writestr('ppt/presentation.xml',f'<p:presentation {NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>' for i in range(1,len(pages)+1))+'</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
        z.writestr('ppt/_rels/presentation.xml.rels',rels([('rId1','slideMaster','slideMasters/slideMaster1.xml')]+[(f'rId{i+1}','slide',f'slides/slide{i}.xml') for i in range(1,len(pages)+1)]))
        cmap='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
        z.writestr('ppt/slideMasters/slideMaster1.xml',f'<p:sldMaster {NS}><p:cSld><p:spTree>{tree()}</p:spTree></p:cSld>{cmap}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
        z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels',rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')]))
        z.writestr('ppt/slideLayouts/slideLayout1.xml',f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{tree()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
        z.writestr('ppt/slideLayouts/_rels/slideLayout1.xml.rels',rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')]))
        colors=[('dk1',BG),('lt1',TEXT),('dk2',PANEL),('lt2',MUTED),('accent1',CYAN),('accent2',AMBER),('accent3','77A7FF'),('accent4','C7A0FF'),('accent5','FF9EAA'),('accent6','FFFFFF'),('hlink',CYAN),('folHlink',AMBER)]
        solid='<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        z.writestr('ppt/theme/theme1.xml','<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="QRefactor"><a:themeElements><a:clrScheme name="QRefactor">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in colors)+'</a:clrScheme><a:fontScheme name="Chinese"><a:majorFont><a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/><a:cs typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/><a:cs typeface="Arial"/></a:minorFont></a:fontScheme><a:fmtScheme name="Minimal"><a:fillStyleLst>'+solid*3+'</a:fillStyleLst><a:lnStyleLst>'+('<a:ln w="12700">'+solid+'<a:prstDash val="solid"/></a:ln>')*3+'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>')*3+'</a:effectStyleLst><a:bgFillStyleLst>'+solid*3+'</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>')
        for index,page in enumerate(pages,1):
            objects=[];links=[('rId1','slideLayout','../slideLayouts/slideLayout1.xml')]
            for ident,o in enumerate(page.objects,2):
                x,y,w,h=[int(o[k]*EMU) for k in ['x','y','w','h']]
                transform=f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
                geom='<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                if o['kind']=='image':
                    name=f'image{index}_{ident}.png';rid=f'rId{len(links)+1}'
                    z.write(o['path'],f'ppt/media/{name}');links.append((rid,'image',f'../media/{name}'))
                    objects.append(f'<p:pic><p:nvPicPr><p:cNvPr id="{ident}" name="Demo screenshot"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>{transform}{geom}</p:spPr></p:pic>');continue
                fill=f'<a:solidFill><a:srgbClr val="{o["color"]}"/></a:solidFill>' if o['kind']=='rect' else '<a:noFill/>'
                obj=f'<p:sp><p:nvSpPr><p:cNvPr id="{ident}" name="{o["kind"]} {ident}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>{transform}{geom}{fill}<a:ln><a:noFill/></a:ln></p:spPr>'
                if o['kind']=='text':
                    size=int(o['size']*60);font='Consolas' if o['mono'] else 'Microsoft YaHei'
                    obj+='<p:txBody><a:bodyPr wrap="none" lIns="0" rIns="0" tIns="0" bIns="0" anchor="t"/><a:lstStyle/>'
                    for line in o['lines']:
                        obj+=f'<a:p><a:pPr><a:lnSpc><a:spcPts val="{int(size*1.32)}"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft></a:pPr><a:r><a:rPr lang="zh-CN" sz="{size}"><a:solidFill><a:srgbClr val="{o["color"]}"/></a:solidFill><a:latin typeface="{font}"/><a:ea typeface="Microsoft YaHei"/></a:rPr><a:t>{escape(line)}</a:t></a:r><a:endParaRPr sz="{size}"/></a:p>'
                    obj+='</p:txBody>'
                objects.append(obj+'</p:sp>')
            z.writestr(f'ppt/slides/slide{index}.xml',f'<p:sld {NS}><p:cSld><p:spTree>{tree()}'+''.join(objects)+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')
            z.writestr(f'ppt/slides/_rels/slide{index}.xml.rels',rels(links))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages=slides();previews=[]
    for index, page in enumerate(pages,1):
        preview=page.preview();preview.save(OUT/f'slide-{index:02}.png');previews.append(preview)
    previews[0].save(OUT/'QRefactor_AI_Programming.pdf',save_all=True,append_images=previews[1:],resolution=120)
    write_pptx(pages,OUT/'QRefactor_AI_Programming.pptx')
    sheet=Image.new('RGB',(1600,900),'#'+BG)
    for i,im in enumerate(previews):sheet.paste(im.resize((400,225)),((i%4)*400,(i//4)*450+100))
    sheet.save(OUT/'overview.png')
    print('Built 8 slides: PPTX + PDF + PNG previews')


if __name__=='__main__':main()
