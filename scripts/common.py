"""Shared tables: physical key names <-> Oryx indices <-> Yuzu ids, and keystroke notation."""
import json, os, re
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "master.yaml")

# Physical key name for every Oryx key index (ErgoDox EZ, Oryx geometry ergodox-ez-st).
# Left: columns 1-7 left->right, rows A-E top->bottom. Right: R1 (centre) -> R7 (outer).
# Thumbs: T1 T2 top pair, T3 big outer, T4 big inner, T5 upper small, T6 lower small; RT* mirrored.
NAMES = {}
for i, n in enumerate(["1A","2A","3A","4A","5A","6A","7A"]): NAMES[i] = n
for i, n in enumerate(["1B","2B","3B","4B","5B","6B","7B"]): NAMES[7+i] = n
for i, n in enumerate(["1C","2C","3C","4C","5C","6C"]): NAMES[14+i] = n
for i, n in enumerate(["1D","2D","3D","4D","5D","6D","7D"]): NAMES[20+i] = n
for i, n in enumerate(["1E","2E","3E","4E","5E"]): NAMES[27+i] = n
for i, n in enumerate(["T1","T2","T5","T3","T4","T6"]): NAMES[32+i] = n
for i, n in enumerate(["R1A","R2A","R3A","R4A","R5A","R6A","R7A"]): NAMES[38+i] = n
for i, n in enumerate(["R1B","R2B","R3B","R4B","R5B","R6B","R7B"]): NAMES[45+i] = n
for i, n in enumerate(["R2C","R3C","R4C","R5C","R6C","R7C"]): NAMES[52+i] = n
for i, n in enumerate(["R1D","R2D","R3D","R4D","R5D","R6D","R7D"]): NAMES[58+i] = n
for i, n in enumerate(["R3E","R4E","R5E","R6E","R7E"]): NAMES[65+i] = n
for i, n in enumerate(["RT2","RT1","RT5","RT6","RT4","RT3"]): NAMES[70+i] = n
ORYX_INDEX = {n: i for i, n in NAMES.items()}

YUZU_ID = {  # Oryx index -> Yuzu Playground key id (ErgoDox stock layout export)
    0:"7P28FW",1:"GZQFPA",2:"FzWhED",3:"0R3YCk",4:"rW9ob7",5:"zYPGbQ",6:"A59P47",
    7:"CEBPLX",8:"l7DqSU",9:"dfYXnc",10:"2bSRwq",11:"JaOAd8",12:"J9JHWP",13:"4JFX3U",
    14:"3R8UDS",15:"I9bsjW",16:"dXk9mu",17:"0XL1hR",18:"Cg7Wc0",19:"SGQPN7",
    20:"3UK6NS",21:"h9SSVX",22:"s6w7jw",23:"UAeurI",24:"NGDt4W",25:"M8QS7R",26:"AMR4XD",
    27:"f19Yvj",28:"kOxNNJ",29:"fzsvxA",30:"dqz1KA",31:"K84UUS",
    32:"GGCFEK",33:"LFQR52",34:"XACG6H",35:"54TSLP",36:"CD9XSL",37:"TLB9ES",
    38:"P56DXT",39:"TIDz6n",40:"0C6IJF",41:"vTVl8h",42:"cNAoas",43:"UVi9dK",44:"MKMFS4",
    45:"GYPDRJ",46:"ZBNA2M",47:"EyXwyF",48:"6Sh7Tl",49:"Y1R9rb",50:"1wB5ta",51:"T24GU9",
    52:"8EYLJ4",53:"DmcEQn",54:"7tj5BS",55:"cGx7Jw",56:"emeZD1",57:"QEKHQW",
    58:"ZRHML7",59:"BFSHE3",60:"Uzb6qW",61:"q4tLCR",62:"CRIsLR",63:"KbSM4v",64:"EGDHBG",
    65:"R4QLAP",66:"SkCBkD",67:"kCDQMH",68:"Y2XSTU",69:"RTHPEX",
    70:"4GSW3A",71:"ZK573M",72:"LLAJET",73:"SQPXD7",74:"Y53RLB",75:"H2CWXF",
}

# Oryx key code <-> human name used in master.yaml `key:` strings.
CODE2NAME = {
    "KC_ESCAPE":"Esc","KC_ENTER":"Enter","KC_SPACE":"Space","KC_TAB":"Tab","KC_DELETE":"Delete",
    "KC_HOME":"Home","KC_END":"End","KC_PAGE_UP":"PgUp","KC_PGDN":"PgDn",
    "KC_UP":"Up","KC_DOWN":"Down","KC_LEFT":"Left","KC_RIGHT":"Right",
    "KC_SCLN":";","KC_QUOTE":"'","KC_LBRC":"[","KC_RBRC":"]","KC_BSLS":"\\","KC_COMMA":",","KC_DOT":".",
    "KC_KP_MINUS":"KP-","KC_KP_PLUS":"KP+","KC_KP_SLASH":"KP/","KC_KP_ASTERISK":"KP*","KC_KP_DOT":"KP.",
    "KC_KP_ENTER":"KPEnter","KC_NUM":"NumLock",
    "KC_LEFT_ALT":"LAlt","KC_LEFT_SHIFT":"LShift","KC_LEFT_CTRL":"LCtrl","KC_RIGHT_GUI":"RWin",
    "KC_TRANSPARENT":"-",
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": CODE2NAME["KC_" + _c] = _c
for _d in "0123456789": CODE2NAME["KC_" + _d] = _d; CODE2NAME["KC_KP_" + _d] = "KP" + _d
for _f in range(1, 25): CODE2NAME[f"KC_F{_f}"] = f"F{_f}"
NAME2CODE = {v: k for k, v in CODE2NAME.items()}
MOD2NAME = {"leftCtrl":"Ctrl","leftShift":"Shift","leftAlt":"Alt","leftGui":"Win",
            "rightCtrl":"RCtrl","rightShift":"RShift","rightAlt":"RAlt","rightGui":"RWin"}
NAME2MOD = {v: k for k, v in MOD2NAME.items()}
MOD_ORDER = ["Win","Ctrl","Alt","Shift","RWin","RCtrl","RAlt","RShift"]

def action_to_str(a):
    """Oryx action dict -> 'Ctrl+Shift+Enter' | 'MO(1)' | 'OSL(3)' | 'macro: Win+Alt+Shift+C, Tab'."""
    if not a: return ""
    if a.get("macro"):
        steps = []
        for s in a["macro"]["keys"]:
            m = s.get("modifiers") or {}
            mods = [MOD2NAME[k] for k, v in m.items() if v]
            mods.sort(key=MOD_ORDER.index)
            steps.append("+".join(mods + [CODE2NAME.get(s["code"], s["code"])]))
        return "macro: " + ", ".join(steps)
    if a.get("code") in ("MO", "OSL", "TG", "TO", "TT", "LT"):
        return f"{a['code']}({a['layer']})"
    mods = sorted(a.get("mods", []), key=lambda m: MOD_ORDER.index(MOD2NAME[m]))
    return "+".join([MOD2NAME[m] for m in mods] + [CODE2NAME.get(a["code"], a["code"])])

def str_to_action(s):
    """Inverse of action_to_str. Returns an Oryx-style dict {code, mods?, layer?, macro?}."""
    s = (s or "").strip()
    if not s: return None
    if s.startswith("macro:"):
        steps = []
        for part in [p.strip() for p in s[6:].split(",") if p.strip()]:
            bits = part.split("+"); key = bits[-1]; mods = bits[:-1]
            md = {k: False for k in MOD2NAME}
            for m in mods: md[NAME2MOD[m]] = True
            steps.append({"code": NAME2CODE[key], "delay": 100, "modifiers": md if mods else None})
        return {"code": "KC_TRANSPARENT", "macro": {"keys": steps, "name": None, "applyAlt": False, "endEnter": False}}
    m = re.fullmatch(r"(MO|OSL|TG|TO|TT)\((\d)\)", s)
    if m: return {"code": m.group(1), "layer": int(m.group(2))}
    if s in NAME2CODE:                      # bare key, incl. names containing '+' such as 'KP+'
        return {"code": NAME2CODE[s]}
    for name in sorted(NAME2CODE, key=len, reverse=True):   # 'Ctrl+KP+' style: longest key name wins
        if s.endswith("+" + name):
            mods = s[: -len(name) - 1].split("+")
            return {"code": NAME2CODE[name], "mods": [NAME2MOD[m] for m in mods]}
    bits = s.split("+"); key = bits[-1]; mods = bits[:-1]
    d = {"code": NAME2CODE[key]}
    if mods: d["mods"] = [NAME2MOD[m] for m in mods]
    return d

def load_master():
    with open(MASTER, encoding="utf-8") as f:
        return yaml.safe_load(f)
