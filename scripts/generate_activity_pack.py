from __future__ import annotations

from io import BytesIO
from pathlib import Path
import random

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ASSETS / "documents" / "aeri-learning-activity-pack.pdf"
PAGE_W, PAGE_H = 595.28, 841.89  # A4 portrait, points
INK = (31, 41, 51)
SAGE = (76, 105, 87)
SOFT = (151, 164, 156)
PALE = (221, 226, 221)
CORAL = (198, 126, 105)
BEIGE = (221, 207, 181)


def rgb(color):
    return " ".join(f"{v / 255:.3f}" for v in color)


def pdf_text(x, y, text, size=11, font="F1", color=INK):
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"q {rgb(color)} rg BT /{font} {size} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({text}) Tj ET Q\n"


def line(x1, y1, x2, y2, color=INK, width=1, dash=None):
    dash_cmd = "[] 0 d" if dash is None else f"[{dash[0]} {dash[1]}] 0 d"
    return f"q {rgb(color)} RG {width:.2f} w {dash_cmd} {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q\n"


def path(points, color=INK, width=1.5, fill=None, close=False, dash=None):
    dash_cmd = "[] 0 d" if dash is None else f"[{dash[0]} {dash[1]}] 0 d"
    out = f"q {rgb(color)} RG {width:.2f} w {dash_cmd} "
    if fill is not None:
        out += f"{rgb(fill)} rg "
    if not points:
        return ""
    out += f"{points[0][0]:.2f} {points[0][1]:.2f} m "
    for x, y in points[1:]:
        out += f"{x:.2f} {y:.2f} l "
    if close:
        out += "h "
    out += "B Q\n" if fill is not None else "S Q\n"
    return out


def cubic(start, segments, color=INK, width=1.5, dash=None):
    dash_cmd = "[] 0 d" if dash is None else f"[{dash[0]} {dash[1]}] 0 d"
    out = f"q {rgb(color)} RG {width:.2f} w {dash_cmd} {start[0]:.2f} {start[1]:.2f} m "
    for x1, y1, x2, y2, x3, y3 in segments:
        out += f"{x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} {x3:.2f} {y3:.2f} c "
    return out + "S Q\n"


def circle(cx, cy, r, stroke=INK, width=1.4, fill=None):
    k = r * 0.55228475
    out = f"q {rgb(stroke)} RG {width:.2f} w "
    if fill is not None:
        out += f"{rgb(fill)} rg "
    out += (
        f"{cx+r:.2f} {cy:.2f} m "
        f"{cx+r:.2f} {cy+k:.2f} {cx+k:.2f} {cy+r:.2f} {cx:.2f} {cy+r:.2f} c "
        f"{cx-k:.2f} {cy+r:.2f} {cx-r:.2f} {cy+k:.2f} {cx-r:.2f} {cy:.2f} c "
        f"{cx-r:.2f} {cy-k:.2f} {cx-k:.2f} {cy-r:.2f} {cx:.2f} {cy-r:.2f} c "
        f"{cx+k:.2f} {cy-r:.2f} {cx+r:.2f} {cy-k:.2f} {cx+r:.2f} {cy:.2f} c "
    )
    return out + ("B Q\n" if fill is not None else "S Q\n")


def ellipse(cx, cy, rx, ry, stroke=INK, width=1.4, fill=None):
    k = 0.55228475
    out = f"q {rgb(stroke)} RG {width:.2f} w "
    if fill is not None:
        out += f"{rgb(fill)} rg "
    out += (
        f"{cx+rx:.2f} {cy:.2f} m "
        f"{cx+rx:.2f} {cy+k*ry:.2f} {cx+k*rx:.2f} {cy+ry:.2f} {cx:.2f} {cy+ry:.2f} c "
        f"{cx-k*rx:.2f} {cy+ry:.2f} {cx-rx:.2f} {cy+k*ry:.2f} {cx-rx:.2f} {cy:.2f} c "
        f"{cx-rx:.2f} {cy-k*ry:.2f} {cx-k*rx:.2f} {cy-ry:.2f} {cx:.2f} {cy-ry:.2f} c "
        f"{cx+k*rx:.2f} {cy-ry:.2f} {cx+rx:.2f} {cy-k*ry:.2f} {cx+rx:.2f} {cy:.2f} c "
    )
    return out + ("B Q\n" if fill is not None else "S Q\n")


def rectangle(x, y, w, h, stroke=INK, width=1, fill=None, dash=None):
    dash_cmd = "[] 0 d" if dash is None else f"[{dash[0]} {dash[1]}] 0 d"
    out = f"q {rgb(stroke)} RG {width:.2f} w {dash_cmd} "
    if fill is not None:
        out += f"{rgb(fill)} rg "
    out += f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re "
    return out + ("B Q\n" if fill is not None else "S Q\n")


def star(cx, cy, outer=9, inner=4, stroke=INK, width=1.2, fill=None):
    pts = []
    for i in range(10):
        import math
        angle = math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    return path(pts, stroke, width, fill, close=True)


def leaf(cx, cy, scale=1.0, color=SAGE):
    out = cubic((cx-12*scale, cy-1*scale), [
        (cx-8*scale, cy+12*scale, cx+6*scale, cy+12*scale, cx+12*scale, cy+1*scale),
        (cx+8*scale, cy-11*scale, cx-4*scale, cy-10*scale, cx-12*scale, cy-1*scale),
    ], color=color, width=1.4)
    out += line(cx-9*scale, cy-5*scale, cx+8*scale, cy+6*scale, color=color, width=1)
    return out


def fish(cx, cy, s=1, color=INK):
    out = ellipse(cx, cy, 20*s, 12*s, color, 1.6)
    out += path([(cx+18*s,cy),(cx+31*s,cy+11*s),(cx+31*s,cy-11*s)], color, 1.6, close=True)
    out += circle(cx-10*s,cy+2*s,1.5*s,color,1,fill=color)
    out += cubic((cx-1*s,cy+8*s),[(cx+3*s,cy+2*s,cx+3*s,cy-2*s,cx-1*s,cy-8*s)],color,1)
    return out


def cat(cx, cy, s=1, color=INK):
    out = path([(cx-17*s,cy+4*s),(cx-22*s,cy+21*s),(cx-6*s,cy+14*s),(cx+5*s,cy+14*s),(cx+21*s,cy+21*s),(cx+17*s,cy+3*s)],color,1.6)
    out += cubic((cx-17*s,cy+4*s),[(cx-21*s,cy-20*s,cx+20*s,cy-20*s,cx+17*s,cy+4*s)],color,1.6)
    out += circle(cx-7*s,cy+1*s,1.2*s,color,1,fill=color)+circle(cx+7*s,cy+1*s,1.2*s,color,1,fill=color)
    out += path([(cx,cy-3*s),(cx-2*s,cy-6*s),(cx+2*s,cy-6*s)],color,1)
    out += cubic((cx,cy-6*s),[(cx-3*s,cy-10*s,cx-7*s,cy-9*s,cx-9*s,cy-8*s)],color,1)
    out += cubic((cx,cy-6*s),[(cx+3*s,cy-10*s,cx+7*s,cy-9*s,cx+9*s,cy-8*s)],color,1)
    out += line(cx-11*s,cy-5*s,cx-20*s,cy-4*s,color,0.8)+line(cx+11*s,cy-5*s,cx+20*s,cy-4*s,color,0.8)
    return out


def bird(cx, cy, s=1, color=INK):
    out = ellipse(cx,cy,19*s,13*s,color,1.6)
    out += path([(cx+15*s,cy+3*s),(cx+28*s,cy+8*s),(cx+17*s,cy-3*s)],color,1.4,close=True)
    out += cubic((cx-11*s,cy+2*s),[(cx-1*s,cy+11*s,cx+4*s,cy-1*s,cx-10*s,cy-7*s)],color,1.2)
    out += circle(cx-10*s,cy+5*s,1.3*s,color,1,fill=color)
    out += line(cx-3*s,cy-12*s,cx-4*s,cy-18*s,color,1.2)+line(cx+8*s,cy-11*s,cx+8*s,cy-18*s,color,1.2)
    out += line(cx-9*s,cy-18*s,cx+1*s,cy-18*s,color,1.2)+line(cx+3*s,cy-18*s,cx+13*s,cy-18*s,color,1.2)
    return out


def header(title, instruction, page_no, image_name="Logo"):
    out = f"q 28 0 0 26 43 784 cm /{image_name} Do Q\n"
    out += pdf_text(80, 797, "Aeri Learning", 12, "F2", INK)
    out += pdf_text(80, 783, "A THOUGHTFUL START FOR CURIOUS MINDS", 6.5, "F2", SAGE)
    out += pdf_text(485, 798, "AGES 3-5", 8, "F2", SAGE)
    out += line(44, 770, 551, 770, PALE, 0.8)
    out += pdf_text(44, 731, title, 24, "F2", INK)
    out += pdf_text(44, 705, instruction, 10.5, "F1", INK)
    out += pdf_text(44, 668, "Name:", 9, "F2", INK)
    out += line(80, 666, 320, 666, SOFT, 0.8)
    out += pdf_text(357, 668, "Date:", 9, "F2", INK)
    out += line(389, 666, 551, 666, SOFT, 0.8)
    out += line(44, 52, 551, 52, PALE, 0.7)
    out += pdf_text(44, 34, f"Aeri Learning  |  Activity Pack  |  {page_no} of 5", 7, "F1", SAGE)
    out += pdf_text(466, 34, "PRINT AND PLAY", 6.5, "F2", SAGE)
    return out


def tracing_page():
    out = header("Pencil paths", "Trace each dotted path from the start circle to the star.", 1)
    rows = [590, 500, 410, 320]
    for i, y in enumerate(rows, 1):
        out += pdf_text(47, y-3, str(i), 9, "F2", SAGE)
        out += circle(83, y, 8, SAGE, 1.4)
        out += star(520, y, 10, 4, CORAL, 1.3)
    out += line(94, rows[0], 509, rows[0], SOFT, 2, (1, 6))
    out += cubic((94,rows[1]),[(165,rows[1]+28,210,rows[1]+28,250,rows[1]),(295,rows[1]-28,340,rows[1]-28,380,rows[1]),(435,rows[1]+28,470,rows[1]+28,509,rows[1])],SOFT,2,(1,6))
    out += path([(94,rows[2]),(145,rows[2]+22),(196,rows[2]-22),(247,rows[2]+22),(298,rows[2]-22),(349,rows[2]+22),(400,rows[2]-22),(451,rows[2]+22),(509,rows[2])],SOFT,2,dash=(1,6))
    out += cubic((94,rows[3]),[(140,rows[3]+35,180,rows[3]+35,220,rows[3]),(260,rows[3]-35,300,rows[3]-35,340,rows[3]),(380,rows[3]+35,425,rows[3]+35,465,rows[3]),(485,rows[3]+20,498,rows[3]+15,509,rows[3])],SOFT,2,(1,6))
    out += pdf_text(44, 250, "Take your time. It is okay if your line wiggles along the way.", 10, "F1", SAGE)
    return out


def matching_page():
    out = header("Who goes together?", "Draw a line from each animal to its matching friend.", 2)
    left_y = [545, 405, 265]
    right_y = [545, 405, 265]
    out += pdf_text(73, 610, "ANIMALS", 8, "F2", SAGE)
    out += pdf_text(445, 610, "MATCH", 8, "F2", SAGE)
    out += fish(118,left_y[0],1.25)
    out += cat(118,left_y[1],1.15)
    out += bird(118,left_y[2],1.2)
    out += cat(475,right_y[0],1.15)
    out += bird(475,right_y[1],1.2)
    out += fish(475,right_y[2],1.25)
    for y in left_y:
        out += circle(165,y,3,SOFT,1)
    for y in right_y:
        out += circle(430,y,3,SOFT,1)
    out += pdf_text(44, 190, "Look closely at the shapes, tails, ears, and wings.", 10, "F1", SAGE)
    return out


def make_maze(cols=5, rows=4, seed=17):
    random.seed(seed)
    walls = {(c,r): {"N","E","S","W"} for c in range(cols) for r in range(rows)}
    seen = {(0,0)}
    stack = [(0,0)]
    steps = [(0,1,"N","S"),(1,0,"E","W"),(0,-1,"S","N"),(-1,0,"W","E")]
    while stack:
        c,r = stack[-1]
        choices=[]
        for dc,dr,a,b in steps:
            n=(c+dc,r+dr)
            if 0<=n[0]<cols and 0<=n[1]<rows and n not in seen:
                choices.append((n,a,b))
        if not choices:
            stack.pop(); continue
        n,a,b=random.choice(choices)
        walls[(c,r)].remove(a);walls[n].remove(b);seen.add(n);stack.append(n)
    return walls


def maze_page():
    out = header("Bunny's little maze", "Can you help Bunny find the carrot? Follow a path through the maze.", 3)
    cols,rows=5,4
    cw,ch=57,54
    x0,y0=157,256
    walls=make_maze(cols,rows)
    wall_color=(105,118,110)
    # Draw each remaining cell wall once. Open the west entrance and east exit.
    for c in range(cols):
        for r in range(rows):
            x=x0+c*cw;y=y0+r*ch
            w=walls[(c,r)]
            if "S" in w and r>0: out += line(x,y,x+cw,y,wall_color,2.2)
            if "W" in w and c>0: out += line(x,y,x,y+ch,wall_color,2.2)
            if "N" in w and r<rows-1: out += line(x,y+ch,x+cw,y+ch,wall_color,2.2)
            if "E" in w and c<cols-1: out += line(x+cw,y,x+cw,y+ch,wall_color,2.2)
    # Outer edges with start and finish openings.
    out += line(x0,y0,x0+cw*cols,y0,wall_color,2.2)
    out += line(x0,y0+ch*rows,x0+cw*cols,y0+ch*rows,wall_color,2.2)
    out += line(x0,y0+ch,x0,y0+ch*rows,wall_color,2.2)
    out += line(x0+cw*cols,y0,x0+cw*cols,y0+ch*(rows-1),wall_color,2.2)
    # Start and destination symbols.
    by=y0+ch/2
    out += pdf_text(73, by+10, "START", 7, "F2", SAGE)
    out += circle(122,by,9,SAGE,1.2)
    out += line(122,by-4,122,by+4,SAGE,1)
    out += circle(119,by+7,2,SAGE,1)
    # Carrot at upper-right exit.
    cy=y0+ch*(rows-0.5)
    out += pdf_text(457, cy+12, "FINISH", 7, "F2", SAGE)
    out += path([(480,cy-5),(499,cy+3),(494,cy-20),(484,cy-18)],CORAL,1.2,fill=(245,222,211),close=True)
    out += line(485,cy-4,480,cy+8,SAGE,1.4)+line(489,cy-2,492,cy+10,SAGE,1.4)
    out += pdf_text(44, 206, "One step at a time. If you reach a dead end, try another way.", 10, "F1", SAGE)
    return out


def counting_page():
    out=header("Count and circle", "Count each group, then circle the number that matches.", 4)
    def task(label, count, y, kind):
        nonlocal out
        out += pdf_text(47,y+38,label,9,"F2",INK)
        xs=[90+i*42 for i in range(count)]
        for x in xs:
            if kind=="star": out += star(x,y,9,4,SOFT,1.2)
            elif kind=="leaf": out += leaf(x,y,0.7,SOFT)
            else: out += circle(x,y,7,SOFT,1.3)
        options=[count-1,count,count+1]
        for x,n in zip([390,450,510],options):
            out += circle(x,y,17,SOFT,1.1)
            out += pdf_text(x-4,y-5,str(n),11,"F1",INK)
    task("1. Count the stars",4,555,"star")
    out += line(46,488,549,488,PALE,.7)
    task("2. Count the leaves",5,435,"leaf")
    out += line(46,368,549,368,PALE,.7)
    task("3. Count the dots",7,315,"dot")
    out += line(46,248,549,248,PALE,.7)
    out += pdf_text(47,218,"Trace the numbers",9,"F2",INK)
    for i,n in enumerate(range(1,11)):
        row=0 if i<5 else 1
        col=i%5
        x=78+col*96
        y=155-row*42
        out += rectangle(x-17,y-10,35,29,PALE,.8)
        out += pdf_text(x-4,y-2,str(n),18,"F1",(171,179,174))
    out += pdf_text(47,70,"You can count again with your favorite small objects at home.",8.5,"F1",SAGE)
    return out


def creativity_page():
    out=header("Make it your own", "Draw your favorite animal. Add colors, patterns, and a little story.", 5)
    out += pdf_text(48,620,"My favorite animal is...",11,"F2",INK)
    out += line(187,618,545,618,SOFT,.8)
    out += rectangle(52,240,491,350,SOFT,1.2,dash=(4,5))
    # Quiet corner guide marks make the drawing area feel inviting without filling it in.
    out += star(76,565,7,3,SAGE,1)
    out += circle(519,265,4,CORAL,1.2)
    out += pdf_text(48,196,"It likes to...",10,"F2",INK)
    out += line(118,194,545,194,SOFT,.8)
    out += pdf_text(48,158,"A special thing about my animal:",10,"F2",INK)
    out += line(201,156,545,156,SOFT,.8)
    out += pdf_text(48,105,"There is no wrong way to make your picture.",9,"F1",SAGE)
    return out


class PDFBuilder:
    def __init__(self, logo_jpeg: bytes, logo_size: tuple[int,int]):
        self.objects=[None]
        self.catalog=self.reserve()
        self.pages=self.reserve()
        self.font_regular=self.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        self.font_bold=self.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        w,h=logo_size
        self.logo=self.add(b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n"%(w,h,len(logo_jpeg))+logo_jpeg+b"\nendstream")
        self.page_ids=[]

    def reserve(self):
        self.objects.append(None)
        return len(self.objects)-1

    def add(self, obj: bytes):
        self.objects.append(obj)
        return len(self.objects)-1

    def add_page(self, content: str):
        data=content.encode("ascii")
        stream=self.add(b"<< /Length %d >>\nstream\n"%len(data)+data+b"\nendstream")
        page=self.add((
            f"<< /Type /Page /Parent {self.pages} 0 R /MediaBox [0 0 {PAGE_W:.2f} {PAGE_H:.2f}] "
            f"/Resources << /Font << /F1 {self.font_regular} 0 R /F2 {self.font_bold} 0 R >> "
            f"/XObject << /Logo {self.logo} 0 R >> >> /Contents {stream} 0 R >>"
        ).encode("ascii"))
        self.page_ids.append(page)

    def write(self,path: Path):
        kids=" ".join(f"{i} 0 R" for i in self.page_ids)
        self.objects[self.catalog]=f"<< /Type /Catalog /Pages {self.pages} 0 R >>".encode("ascii")
        self.objects[self.pages]=f"<< /Type /Pages /Kids [{kids}] /Count {len(self.page_ids)} >>".encode("ascii")
        out=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets=[0]
        for number,obj in enumerate(self.objects[1:],start=1):
            offsets.append(len(out))
            out.extend(f"{number} 0 obj\n".encode("ascii"));out.extend(obj);out.extend(b"\nendobj\n")
        xref=len(out)
        out.extend(f"xref\n0 {len(self.objects)}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]: out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
        out.extend(f"trailer\n<< /Size {len(self.objects)} /Root {self.catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
        path.write_bytes(out)


def main():
    mark=Image.open(ASSETS/"icons"/"aeri-learning-mark.png").convert("RGBA")
    white=Image.new("RGBA",mark.size,(255,255,255,255))
    white.alpha_composite(mark)
    flat=white.convert("RGB")
    flat.thumbnail((180,165),Image.Resampling.LANCZOS)
    img_bytes=BytesIO();flat.save(img_bytes,format="JPEG",quality=88,optimize=True)
    builder=PDFBuilder(img_bytes.getvalue(),flat.size)
    for page in [tracing_page(),matching_page(),maze_page(),counting_page(),creativity_page()]:
        builder.add_page(page)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    builder.write(OUTPUT)
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__=="__main__":
    main()
