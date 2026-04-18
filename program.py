from pathlib import Path
from datetime import datetime
import json
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from urllib.request import Request, urlopen

import pygame


WINDOW_SIZE = [1600, 750]  # 리스트로 변경해 동적 갱신
FPS = 60
PLAYER_RADIUS = 18
TOOL_PANEL_RECT = pygame.Rect(15, 15, 190, 545)
PITCH_LEFT_OFFSET = 230
def get_pitch_rect():
	return pygame.Rect(PITCH_LEFT_OFFSET, 0, WINDOW_SIZE[0] - PITCH_LEFT_OFFSET, WINDOW_SIZE[1])
PITCH_RECT = get_pitch_rect()
LASER_DRAW_MIN_DIST_SQ = 9
LASER_FADE_FRAMES = 22
LETTERBOX_COLOR = (12, 18, 22)
PLAYER_INFO_FILE = "player_candidates.txt"
CAPTURE_DIR_NAME = "captures"
ROSTER_DIR_NAME = "roster"
ASSETS_DIR_NAME = "assets"
APP_ICON_FILE = "thumbnail.ico"
WINDOWS_APP_ID = "TacticalPad.App"
ROSTER_LEFT_FILE = "left_roster.txt"
ROSTER_RIGHT_FILE = "right_roster.txt"
MENU_WIDTH = 260
MENU_ITEM_HEIGHT = 28
MENU_MAX_ROWS = 20
MENU_HEADER_HEIGHT = 62
MENU_FOOTER_HEIGHT = 24
ZONE_MIN_RADIUS = 10
ZONE_STRIPE_GAP = 16
ZONE_STRIPE_WIDTH = 7
LINK_PICK_TOLERANCE = 11

MENU_PICK_NAME = "name"
MENU_PICK_NUMBER = "number"
MENU_PICK_POSITION = "position"

POSITION_OPTIONS = [
	"GK", "LB", "LCB", "CB", "RCB", "RB",
	"LWB", "RWB", "LDM", "DM", "RDM",
	"LCM", "CM", "RCM", "LAM", "AM", "RAM",
	"LM", "RM", "LST", "RST",
	"LW", "RW", "CF", "ST",
]

PLAYER_COLOR_OPTIONS = [
	("Amber", (255, 190, 0)),
	("Blue", (30, 120, 255)),
	("Red", (225, 70, 70)),
	("Green", (70, 180, 95)),
	("Purple", (140, 90, 220)),
	("White", (235, 235, 235)),
	("Black", (35, 35, 35)),
]

DEFAULT_FORMATION = "4-2-3-1"

FORMATION_LAYOUTS_LEFT = {
	"4-2-3-1": [
		("GK", 0.16, 0.50),
		("LB", 0.20, 0.18),
		("LCB", 0.24, 0.38),
		("RCB", 0.24, 0.62),
		("RB", 0.20, 0.82),
		("LDM", 0.37, 0.40),
		("RDM", 0.37, 0.60),
		("LAM", 0.51, 0.24),
		("AM", 0.56, 0.50),
		("RAM", 0.51, 0.76),
		("ST", 0.67, 0.50),
	],
	"4-3-3": [
		("GK", 0.16, 0.50),
		("LB", 0.20, 0.18),
		("LCB", 0.24, 0.38),
		("RCB", 0.24, 0.62),
		("RB", 0.20, 0.82),
		("DM", 0.44, 0.50),
		("LCM", 0.40, 0.30),
		("RCM", 0.40, 0.70),
		("LW", 0.58, 0.22),
		("ST", 0.64, 0.50),
		("RW", 0.58, 0.78),
	],
	"4-4-2": [
		("GK", 0.16, 0.50),
		("LB", 0.20, 0.18),
		("LCB", 0.24, 0.38),
		("RCB", 0.24, 0.62),
		("RB", 0.20, 0.82),
		("LM", 0.39, 0.20),
		("LCM", 0.40, 0.40),
		("RCM", 0.40, 0.60),
		("RM", 0.39, 0.80),
		("LST", 0.62, 0.40),
		("RST", 0.62, 0.60),
	],
	"3-4-2-1": [
		("GK", 0.16, 0.50),
		("LCB", 0.23, 0.34),
		("CB", 0.26, 0.50),
		("RCB", 0.23, 0.66),
		("LWB", 0.37, 0.20),
		("LDM", 0.40, 0.40),
		("RDM", 0.40, 0.60),
		("RWB", 0.37, 0.80),
		("LAM", 0.56, 0.34),
		("RAM", 0.56, 0.66),
		("ST", 0.68, 0.50),
	],
}

MODE_MOVE = "move"
MODE_LASER = "laser"
MODE_ZONE = "zone"
MODE_LINK = "link"
MODE_DRAW = "draw"
TOOL_CAPTURE = "capture"
CAPTURE_NOTICE_FRAMES = 120
TOOL_LOAD_LEFT_ROSTER = "load_left_roster"
TOOL_SAVE_LEFT_ROSTER = "save_left_roster"
TOOL_LOAD_RIGHT_ROSTER = "load_right_roster"
TOOL_SAVE_RIGHT_ROSTER = "save_right_roster"
TOOL_COLOR_LEFT = "color_left"
TOOL_COLOR_RIGHT = "color_right"
TOOL_LOAD_FOTMOB = "load_fotmob"
TOOL_TOGGLE_LEFT_TEAM = "toggle_left_team"
TOOL_TOGGLE_RIGHT_TEAM = "toggle_right_team"
TOOL_CLEAR_ALL = "clear_all"

ROSTER_PICK_TEAM = "team"


class Player:
	def __init__(self, x, y, color, label):
		self.x = x
		self.y = y
		self.color = color
		self.label = label
		self.team = "left"
		self.starter = True
		self.player_name = ""
		self.jersey_no = ""
		self.info_mode = MENU_PICK_NAME

	def contains(self, mx, my):
		return (self.x - mx) ** 2 + (self.y - my) ** 2 <= PLAYER_RADIUS ** 2

	def draw(self, surface, font, info_font, show_info_label=True):
		pygame.draw.circle(surface, self.color, (self.x, self.y), PLAYER_RADIUS)
		pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), PLAYER_RADIUS, 2)
		text = font.render(self.label, True, (255, 255, 255))
		rect = text.get_rect(center=(self.x, self.y))
		surface.blit(text, rect)

		if not show_info_label:
			return

		info_text = self.player_name.strip() or self.jersey_no.strip()

		if info_text:
			text_color = (20, 20, 20) if sum(self.color) > 450 else (255, 255, 255)
			label_text = info_font.render(info_text, True, text_color)
			label_rect = label_text.get_rect()
			box_padding_x = 10
			box_padding_y = 5
			box_rect = label_rect.inflate(box_padding_x * 2, box_padding_y * 2)
			box_rect.center = (self.x, self.y + PLAYER_RADIUS + 11)
			box_rect.left = max(0, min(box_rect.left, surface.get_width() - box_rect.width))
			box_rect.top = max(0, min(box_rect.top, surface.get_height() - box_rect.height))
			pygame.draw.rect(surface, self.color, box_rect, border_radius=4)
			pygame.draw.rect(surface, (255, 255, 255), box_rect, 2, border_radius=4)
			surface.blit(label_text, label_text.get_rect(center=box_rect.center))


def load_player_candidates():
	path = Path(__file__).parent / PLAYER_INFO_FILE
	candidates = []

	if not path.exists():
		return candidates, path

	for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#"):
			continue

		if "," in line:
			name, number = [part.strip() for part in line.split(",", 1)]
		else:
			# If comma is missing, use the same token for both name and number.
			name = line
			number = line

		if name:
			candidates.append((name, number))

	return candidates, path


def build_lineup_candidates(players, team_name=None):
	seen = set()
	candidates = []
	for player in players:
		if team_name is not None and player.team != team_name:
			continue
		name = str(player.player_name).strip()
		number = str(player.jersey_no).strip()
		if not name and not number:
			continue
		if not name:
			name = number
		if not number:
			number = name
		key = (name, number)
		if key in seen:
			continue
		seen.add(key)
		candidates.append(key)
	return candidates


def get_available_candidates(players, extra_candidates=None, team_name=None):
	lineup_candidates = build_lineup_candidates(players, team_name=team_name)
	file_candidates, file_path = load_player_candidates()
	extra_candidates = extra_candidates or []

	if not lineup_candidates and not extra_candidates:
		return file_candidates, file_path

	# Keep lineup players first, then append runtime and txt candidates.
	seen = set(lineup_candidates)
	merged = list(lineup_candidates)
	for item in extra_candidates:
		if item in seen:
			continue
		merged.append(item)
		seen.add(item)
	for item in file_candidates:
		if item in seen:
			continue
		merged.append(item)
		seen.add(item)

	lineup_source = Path(__file__).parent / ROSTER_DIR_NAME / "current_lineup.txt"
	return merged, lineup_source


def prompt_fotmob_url():
	try:
		root = tk.Tk()
		root.withdraw()
		url = simpledialog.askstring(
			title="Load FotMob Lineups",
			prompt="Paste FotMob match URL:",
			initialvalue="https://www.fotmob.com/matches/",
			parent=root,
		)
		root.destroy()
		if not url:
			return None
		return url.strip()
	except Exception:
		return None


def fetch_fotmob_next_data(match_url):
	request = Request(
		match_url,
		headers={
			"User-Agent": "Mozilla/5.0",
			"Accept-Language": "en-US,en;q=0.9",
		},
	)
	with urlopen(request, timeout=15) as response:
		html = response.read().decode("utf-8", errors="replace")

	match = re.search(
		r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
		html,
		re.DOTALL,
	)
	if not match:
		raise ValueError("FotMob page JSON (__NEXT_DATA__) not found")

	return json.loads(match.group(1))


def _iter_dicts(value):
	if isinstance(value, dict):
		yield value
		for inner in value.values():
			yield from _iter_dicts(inner)
	elif isinstance(value, list):
		for item in value:
			yield from _iter_dicts(item)


def _extract_player_entry(item):
	if not isinstance(item, dict):
		return None

	name = ""
	for key in ("name", "fullName", "shortName", "displayName"):
		value = item.get(key)
		if value:
			name = str(value).strip()
			break

	if not name:
		return None

	number = ""
	for key in ("shirtNumber", "shirtNo", "jerseyNumber", "number"):
		value = item.get(key)
		if value is not None:
			number = str(value).strip()
			break

	position = ""
	for key in ("position", "positionString", "positionName", "role"):
		value = item.get(key)
		if value:
			position = str(value).strip().upper()
			break

	position_id = None
	for key in ("positionId", "position_id", "formationPosition"):
		value = item.get(key)
		if value is not None:
			position_id = str(value).strip()
			break

	return {
		"name": name,
		"number": number,
		"position": position,
		"position_id": position_id,
	}


def _collect_players_from_keys(team_block, key_names):
	players = []
	if not isinstance(team_block, dict):
		return players

	for key in key_names:
		container = team_block.get(key)
		if container is None:
			continue
		for mapping in _iter_dicts(container):
			entry = _extract_player_entry(mapping)
			if entry is not None:
				players.append(entry)
	return players


def _dedupe_player_entries(entries):
	seen = set()
	result = []
	for entry in entries:
		key = (entry["name"], entry["number"])
		if key in seen:
			continue
		seen.add(key)
		result.append(entry)
	return result


def _read_team_lineup(team_block):
	starters = _collect_players_from_keys(team_block, ["starters", "startingLineup", "lineup", "players"])
	bench = _collect_players_from_keys(team_block, ["substitutes", "subs", "bench"])

	all_players = _collect_players_from_keys(team_block, ["lineup", "players", "squad"])
	starters = _dedupe_player_entries(starters)
	bench = _dedupe_player_entries(bench)
	all_players = _dedupe_player_entries(all_players)

	if not starters and all_players:
		starters = all_players[:11]

	if not bench and all_players:
		starter_keys = {(entry["name"], entry["number"]) for entry in starters}
		bench = [entry for entry in all_players if (entry["name"], entry["number"]) not in starter_keys]

	team_name = ""
	if isinstance(team_block, dict):
		for key in ("name", "teamName", "shortName"):
			value = team_block.get(key)
			if value:
				team_name = str(value).strip()
				break

	return team_name, starters, bench


def parse_fotmob_lineups(next_data):
	props = next_data.get("props", {}) if isinstance(next_data, dict) else {}
	page_props = props.get("pageProps", {}) if isinstance(props, dict) else {}
	content = page_props.get("content", {}) if isinstance(page_props, dict) else {}
	lineup = content.get("lineup", {}) if isinstance(content, dict) else {}

	if not isinstance(lineup, dict):
		raise ValueError("FotMob lineup block not found")

	home_block = lineup.get("homeTeam")
	away_block = lineup.get("awayTeam")

	if home_block is None or away_block is None:
		for mapping in _iter_dicts(lineup):
			if home_block is None and "homeTeam" in mapping:
				home_block = mapping.get("homeTeam")
			if away_block is None and "awayTeam" in mapping:
				away_block = mapping.get("awayTeam")

	if home_block is None or away_block is None:
		raise ValueError("Could not detect home/away lineup blocks")

	home_name, home_starters, home_bench = _read_team_lineup(home_block)
	away_name, away_starters, away_bench = _read_team_lineup(away_block)

	return {
		"left": {
			"team_name": home_name,
			"starters": home_starters,
			"bench": home_bench,
		},
		"right": {
			"team_name": away_name,
			"starters": away_starters,
			"bench": away_bench,
		},
	}


def apply_starters_to_team(players, team_name, starters):
	team_players = [player for player in players if player.team == team_name]

	def normalize_pos_token(text):
		return re.sub(r"[^A-Z0-9]+", "", str(text or "").upper())

	def map_fotmob_position_to_label(entry):
		raw = normalize_pos_token(entry.get("position", ""))
		position_map = {
			"GK": "GK",
			"GOALKEEPER": "GK",
			"LB": "LB",
			"DL": "LB",
			"LEFTBACK": "LB",
			"RB": "RB",
			"DR": "RB",
			"RIGHTBACK": "RB",
			"LCB": "LCB",
			"DCL": "LCB",
			"RCB": "RCB",
			"DCR": "RCB",
			"CB": "CB",
			"DC": "CB",
			"CENTERBACK": "CB",
			"CENTREBACK": "CB",
			"LWB": "LWB",
			"WBL": "LWB",
			"RWB": "RWB",
			"WBR": "RWB",
			"LDM": "LDM",
			"DML": "LDM",
			"RDM": "RDM",
			"DMR": "RDM",
			"DM": "DM",
			"CDM": "DM",
			"LCM": "LCM",
			"MCL": "LCM",
			"RCM": "RCM",
			"MCR": "RCM",
			"CM": "CM",
			"MC": "CM",
			"LAM": "LAM",
			"AML": "LAM",
			"RAM": "RAM",
			"AMR": "RAM",
			"AM": "AM",
			"AMC": "AM",
			"LM": "LM",
			"RM": "RM",
			"LW": "LW",
			"RW": "RW",
			"CF": "CF",
			"ST": "ST",
			"FW": "ST",
			"LST": "LST",
			"FCL": "LST",
			"RST": "RST",
			"FCR": "RST",
		}
		if raw in position_map:
			return position_map[raw]
		if raw.endswith("LEFT"):
			if "BACK" in raw:
				return "LB"
			if "WING" in raw:
				return "LW"
			if "MID" in raw:
				return "LM"
		if raw.endswith("RIGHT"):
			if "BACK" in raw:
				return "RB"
			if "WING" in raw:
				return "RW"
			if "MID" in raw:
				return "RM"
		return ""

	remaining_players = list(team_players)
	remaining_entries = []

	for entry in starters:
		target_label = map_fotmob_position_to_label(entry)
		
		matched_player = None
		if target_label:
			for player in remaining_players:
				if player.label.upper() == target_label:
					matched_player = player
					break

		if matched_player is None:
			remaining_entries.append(entry)
			continue

		matched_player.player_name = entry["name"]
		matched_player.jersey_no = entry["number"]
		matched_player.starter = True
		matched_player.info_mode = MENU_PICK_NAME
		remaining_players.remove(matched_player)

	fotmob_order = [
		"GK",
		"RWB", "RB", "RCB", "CB", "LCB", "LB", "LWB",
		"RDM", "DM", "LDM",
		"RM", "RCM", "CM", "LCM", "LM",
		"RW", "RAM", "AM", "LAM", "LW",
		"RST", "CF", "ST", "LST"
	]
	
	def sort_key(p):
		try:
			return fotmob_order.index(p.label.upper())
		except ValueError:
			return 999
			
	remaining_players.sort(key=sort_key)

	for player, entry in zip(remaining_players, remaining_entries):
		player.player_name = entry["name"]
		player.jersey_no = entry["number"]
		player.starter = True
		player.info_mode = MENU_PICK_NAME

	used_count = min(len(remaining_entries), len(remaining_players))
	for player in remaining_players[used_count:]:
		player.player_name = ""
		player.jersey_no = ""
		player.starter = True


def build_candidates_from_entries(entries):
	result = []
	for entry in entries:
		name = str(entry.get("name", "")).strip()
		number = str(entry.get("number", "")).strip()
		if not name and not number:
			continue
		if not name:
			name = number
		if not number:
			number = name
		result.append((name, number))
	seen = set()
	deduped = []
	for item in result:
		if item in seen:
			continue
		seen.add(item)
		deduped.append(item)
	return deduped


def parse_bool_token(text):
	value = str(text).strip().lower()
	return value in {"1", "true", "yes", "y", "start", "starter"}


def normalize_formation_text(text):
	value = str(text).strip().lower().replace(" ", "")
	if not value:
		return DEFAULT_FORMATION

	if value.startswith("formation"):
		for sep in (":", "=", ","):
			if sep in value:
				value = value.split(sep, 1)[1].strip().lower().replace(" ", "")
				break
		else:
			value = value[len("formation"):].strip()

	formation_alias = {
		"4231": "4-2-3-1",
		"433": "4-3-3",
		"442": "4-4-2",
	}
	value = formation_alias.get(value, value)

	if value in FORMATION_LAYOUTS_LEFT:
		return value
	return DEFAULT_FORMATION


def parse_formation_line(line):
	text = str(line).strip()
	if not text:
		return DEFAULT_FORMATION

	lower = text.lower().lstrip("#").strip()

	if lower.startswith("team,") or lower.startswith("starter,"):
		return None
	if "position" in lower and "," in lower:
		return None

	if lower.startswith("formation"):
		return normalize_formation_text(lower)

	if "," in lower:
		return None

	if any(ch.isdigit() for ch in lower):
		return normalize_formation_text(lower)

	return None


def mirror_position_label(label):
	swap_map = {
		"LB": "RB",
		"RB": "LB",
		"LCB": "RCB",
		"RCB": "LCB",
		"LWB": "RWB",
		"RWB": "LWB",
		"LDM": "RDM",
		"RDM": "LDM",
		"LCM": "RCM",
		"RCM": "LCM",
		"LAM": "RAM",
		"RAM": "LAM",
		"LW": "RW",
		"RW": "LW",
		"LM": "RM",
		"RM": "LM",
		"LST": "RST",
		"RST": "LST",
	}
	return swap_map.get(label, label)


def get_team_formation_layout(team_name, formation):
	formation_key = normalize_formation_text(formation)
	left_layout = FORMATION_LAYOUTS_LEFT.get(formation_key, FORMATION_LAYOUTS_LEFT[DEFAULT_FORMATION])
	if team_name == "left":
		return left_layout

	right_layout = []
	for label, rx, ry in left_layout:
		right_layout.append((mirror_position_label(label), 1.0 - rx, ry))
	return right_layout


def apply_team_formation(players, team_name, formation):
	team_players = [player for player in players if player.team == team_name]
	layout = get_team_formation_layout(team_name, formation)
	for player, (label, rx, ry) in zip(team_players, layout):
		player.x = int(PITCH_RECT.left + rx * PITCH_RECT.width)
		player.y = int(PITCH_RECT.top + ry * PITCH_RECT.height)
		player.label = label


def detect_team_formation(players, team_name):
	layout = get_team_formation_layout(team_name, DEFAULT_FORMATION)
	team_players = [player for player in players if player.team == team_name]
	if len(team_players) < len(layout):
		return DEFAULT_FORMATION
	for player, (label, _, _) in zip(team_players, layout):
		if player.label != label:
			return DEFAULT_FORMATION
	return DEFAULT_FORMATION


def get_roster_dir():
	path = Path(__file__).parent / ROSTER_DIR_NAME
	path.mkdir(parents=True, exist_ok=True)
	return path


def get_default_roster_filename(team_name):
	return ROSTER_LEFT_FILE if team_name == "left" else ROSTER_RIGHT_FILE


def pick_roster_open_file(title="Load Roster File", team_name="left"):
	try:
		root = tk.Tk()
		root.withdraw()
		selected_path = filedialog.askopenfilename(
			initialdir=str(get_roster_dir()),
			title=title,
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
			initialfile=get_default_roster_filename(team_name),
		)
		root.destroy()
		return Path(selected_path) if selected_path else None
	except Exception:
		return None


def pick_roster_save_file(title="Save Roster File", team_name="left"):
	try:
		root = tk.Tk()
		root.withdraw()
		selected_path = filedialog.asksaveasfilename(
			initialdir=str(get_roster_dir()),
			title=title,
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
			initialfile=get_default_roster_filename(team_name),
		)
		root.destroy()
		return Path(selected_path) if selected_path else None
	except Exception:
		return None


def list_roster_files():
	roster_dir = get_roster_dir()
	return sorted(roster_dir.glob("*.txt"), key=lambda file_path: file_path.name.lower())


def parse_roster_file(roster_path, default_team=None):
	text_lines = roster_path.read_text(encoding="utf-8-sig").splitlines()
	formation = DEFAULT_FORMATION
	data_lines = text_lines

	if text_lines:
		parsed_formation = parse_formation_line(text_lines[0])
		if parsed_formation is not None:
			formation = parsed_formation
			data_lines = text_lines[1:]

	rows = []
	for raw_line in data_lines:
		line = raw_line.strip()
		if not line or line.startswith("#"):
			continue
		parts = [part.strip() for part in line.split(",")]
		if len(parts) >= 5:
			team, starter_text, position, name, number = parts[:5]
		elif len(parts) >= 4:
			if default_team is None:
				continue
			starter_text, position, name, number = parts[:4]
			team = default_team
		else:
			continue
		rows.append(
			{
				"team": team.lower(),
				"starter": parse_bool_token(starter_text),
				"position": position,
				"name": name,
				"number": number,
			}
		)
	return formation, rows


def save_roster_file(roster_path, players, include_team=True, formation=DEFAULT_FORMATION):
	formation_text = normalize_formation_text(formation)
	if include_team:
		lines = [formation_text, "# team,starter,position,name,number"]
	else:
		lines = [formation_text, "# starter,position,name,number"]
	for player in players:
		row_parts = [
			"1" if player.starter else "0",
			player.label,
			player.player_name,
			player.jersey_no,
		]
		if include_team:
			row_parts.insert(0, player.team)
		lines.append(",".join(row_parts))
	roster_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_roster_folder(roster_dir, players, team_formations=None):
	roster_dir.mkdir(parents=True, exist_ok=True)
	left_players = [player for player in players if player.team == "left"]
	right_players = [player for player in players if player.team == "right"]
	left_path = roster_dir / ROSTER_LEFT_FILE
	right_path = roster_dir / ROSTER_RIGHT_FILE
	if team_formations is None:
		team_formations = {
			"left": DEFAULT_FORMATION,
			"right": DEFAULT_FORMATION,
		}
	save_roster_file(left_path, left_players, formation=team_formations.get("left", DEFAULT_FORMATION))
	save_roster_file(right_path, right_players, formation=team_formations.get("right", DEFAULT_FORMATION))
	return left_path, right_path


def save_team_roster(roster_path, players, team_name, formation=DEFAULT_FORMATION):
	roster_path.parent.mkdir(parents=True, exist_ok=True)
	team_players = [player for player in players if player.team == team_name]
	save_roster_file(roster_path, team_players, include_team=False, formation=formation)
	return roster_path


def load_team_roster(players, roster_path, team_name):
	if not roster_path.exists():
		return 0, DEFAULT_FORMATION
	formation, rows = parse_roster_file(roster_path, default_team=team_name)
	apply_team_formation(players, team_name, formation)
	team_rows = [
		row for row in rows
		if row["team"] == team_name and row["starter"]
	]
	if not team_rows:
		return 0, formation
	apply_roster_rows(players, team_rows)
	return len(team_rows), formation


def apply_roster_rows(players, roster_rows):
	def normalize_position(position_text):
		return str(position_text).strip().upper()

	def resolve_position_alias(row_pos, available_labels):
		alias_pairs = {
			"LW": "LAM",
			"LAM": "LW",
			"RW": "RAM",
			"RAM": "RW",
		}
		aliased = alias_pairs.get(row_pos)
		if aliased and aliased in available_labels:
			return aliased
		return row_pos

	for team_name in ("left", "right"):
		team_players = [player for player in players if player.team == team_name]
		team_rows = [row for row in roster_rows if row["team"] == team_name]

		available_players = list(team_players)
		remaining_rows = []

		for row in team_rows:
			row_pos = normalize_position(row.get("position", ""))
			if not row_pos:
				remaining_rows.append(row)
				continue

			available_labels = {normalize_position(player.label) for player in available_players}
			if row_pos not in available_labels:
				row_pos = resolve_position_alias(row_pos, available_labels)

			matched_player = None
			for player in available_players:
				if normalize_position(player.label) == row_pos:
					matched_player = player
					break

			if matched_player is None:
				remaining_rows.append(row)
				continue

			matched_player.starter = row["starter"]
			matched_player.player_name = row["name"]
			matched_player.jersey_no = row["number"]
			matched_player.info_mode = MENU_PICK_NAME
			matched_player.team = team_name
			available_players.remove(matched_player)

		for player, row in zip(available_players, remaining_rows):
			player.starter = row["starter"]
			player.player_name = row["name"]
			player.jersey_no = row["number"]
			player.info_mode = MENU_PICK_NAME
			player.team = team_name


def load_roster_from_file(players, roster_path):
	formation, rows = parse_roster_file(roster_path)
	apply_team_formation(players, "left", formation)
	apply_team_formation(players, "right", formation)
	rows = [row for row in rows if row["starter"]]
	apply_roster_rows(players, rows)
	return len(rows)


def load_roster_folder(players, roster_dir):
	loaded_files = []
	left_path = roster_dir / ROSTER_LEFT_FILE
	right_path = roster_dir / ROSTER_RIGHT_FILE
	if left_path.exists():
		load_roster_from_file(players, left_path)
		loaded_files.append(left_path.name)
	if right_path.exists():
		load_roster_from_file(players, right_path)
		loaded_files.append(right_path.name)
	return loaded_files


def pick_player_at(players, pos):
	mx, my = pos
	for player in reversed(players):
		if player.contains(mx, my):
			return player
	return None


def apply_team_color(players, team_name, color):
	for player in players:
		if player.team == team_name:
			player.color = color


def pick_zone_at(zones, pos):
	mx, my = pos
	for idx in range(len(zones) - 1, -1, -1):
		zone = zones[idx]
		cx, cy = zone["center"]
		radius = zone["radius"]
		if (mx - cx) ** 2 + (my - cy) ** 2 <= radius ** 2:
			return idx
	return None


def point_to_segment_distance_sq(px, py, ax, ay, bx, by):
	abx = bx - ax
	aby = by - ay
	apx = px - ax
	apy = py - ay
	den = abx * abx + aby * aby
	if den == 0:
		dx = px - ax
		dy = py - ay
		return dx * dx + dy * dy
	t = max(0.0, min(1.0, (apx * abx + apy * aby) / den))
	closest_x = ax + t * abx
	closest_y = ay + t * aby
	dx = px - closest_x
	dy = py - closest_y
	return dx * dx + dy * dy


def pick_link_at(links, pos, tolerance=LINK_PICK_TOLERANCE):
	mx, my = pos
	threshold = tolerance * tolerance
	for idx in range(len(links) - 1, -1, -1):
		start_player, end_player = links[idx]
		distance_sq = point_to_segment_distance_sq(
			mx,
			my,
			start_player.x,
			start_player.y,
			end_player.x,
			end_player.y,
		)
		if distance_sq <= threshold:
			return idx
	return None


def get_connected_link_indices(links, start_idx):
	if start_idx is None or start_idx < 0 or start_idx >= len(links):
		return set()

	connected = set()
	stack = [start_idx]

	while stack:
		idx = stack.pop()
		if idx in connected:
			continue
		connected.add(idx)
		start_player, end_player = links[idx]

		for other_idx, (other_start, other_end) in enumerate(links):
			if other_idx in connected:
				continue
			if (
				other_start is start_player
				or other_start is end_player
				or other_end is start_player
				or other_end is end_player
			):
				stack.append(other_idx)

	return connected


def build_candidate_menu(anchor_pos, candidate_count):
	x, y = anchor_pos
	row_count = max(1, min(candidate_count, MENU_MAX_ROWS))
	height = MENU_HEADER_HEIGHT + row_count * MENU_ITEM_HEIGHT + MENU_FOOTER_HEIGHT
	max_x = WINDOW_SIZE[0] - MENU_WIDTH - 10
	max_y = WINDOW_SIZE[1] - height - 10
	menu_x = max(10, min(x, max_x))
	menu_y = max(10, min(y, max_y))
	return pygame.Rect(menu_x, menu_y, MENU_WIDTH, height)


def get_menu_tab_rects(menu_rect):
	inner_w = menu_rect.width - 20
	tab_w = (inner_w - 12) // 3
	name_tab = pygame.Rect(menu_rect.x + 10, menu_rect.y + 30, tab_w, 22)
	number_tab = pygame.Rect(name_tab.right + 6, menu_rect.y + 30, tab_w, 22)
	position_tab = pygame.Rect(number_tab.right + 6, menu_rect.y + 30, tab_w, 22)
	return name_tab, number_tab, position_tab


def get_menu_row_rect(menu_rect, idx):
	return pygame.Rect(
		menu_rect.x + 8,
		menu_rect.y + MENU_HEADER_HEIGHT + idx * MENU_ITEM_HEIGHT,
		menu_rect.width - 16,
		MENU_ITEM_HEIGHT - 3,
	)


def to_number_sort_value(number):
	text = str(number).strip()
	if text.isdigit():
		return 0, int(text)
	return 1, text


def get_menu_items(candidates, pick_mode):
	if pick_mode == MENU_PICK_POSITION:
		return [(pos, pos) for pos in POSITION_OPTIONS]
	if pick_mode == MENU_PICK_NUMBER:
		return sorted(candidates, key=lambda item: (to_number_sort_value(item[1]), item[0].lower()))
	return sorted(candidates, key=lambda item: item[0].lower())


def draw_candidate_menu(surface, font, menu_rect, items, hovered_idx, file_path, pick_mode):
	panel = pygame.Surface((menu_rect.width, menu_rect.height), pygame.SRCALPHA)
	panel.fill((12, 18, 28, 220))
	surface.blit(panel, menu_rect.topleft)
	pygame.draw.rect(surface, (230, 230, 230), menu_rect, 2, border_radius=8)

	title = font.render("Select Player", True, (245, 245, 245))
	surface.blit(title, (menu_rect.x + 10, menu_rect.y + 8))
	name_tab, number_tab, position_tab = get_menu_tab_rects(menu_rect)
	name_active = pick_mode == MENU_PICK_NAME
	number_active = pick_mode == MENU_PICK_NUMBER
	position_active = pick_mode == MENU_PICK_POSITION
	pygame.draw.rect(surface, (70, 130, 180) if name_active else (58, 65, 80), name_tab, border_radius=6)
	pygame.draw.rect(surface, (70, 130, 180) if number_active else (58, 65, 80), number_tab, border_radius=6)
	pygame.draw.rect(surface, (70, 130, 180) if position_active else (58, 65, 80), position_tab, border_radius=6)
	name_text = font.render("Name", True, (255, 255, 255))
	number_text = font.render("Number", True, (255, 255, 255))
	position_text = font.render("Pos", True, (255, 255, 255))
	surface.blit(name_text, name_text.get_rect(center=name_tab.center))
	surface.blit(number_text, number_text.get_rect(center=number_tab.center))
	surface.blit(position_text, position_text.get_rect(center=position_tab.center))

	for idx, (name, number) in enumerate(items):
		row_rect = get_menu_row_rect(menu_rect, idx)
		fill = (72, 104, 140) if idx == hovered_idx else (58, 65, 80)
		pygame.draw.rect(surface, fill, row_rect, border_radius=6)
		if pick_mode == MENU_PICK_POSITION:
			text = f"Position: {name}"
		elif pick_mode == MENU_PICK_NUMBER:
			text = f"#{number}  {name}" if number else f"-  {name}"
		else:
			text = f"{name}  (#{number})" if number else name
		text_surf = font.render(text, True, (255, 255, 255))
		surface.blit(text_surf, text_surf.get_rect(midleft=(row_rect.x + 8, row_rect.centery)))

	file_hint = f"source: {file_path.name}"
	hint_surf = font.render(file_hint, True, (210, 210, 210))
	surface.blit(hint_surf, (menu_rect.x + 10, menu_rect.bottom - 20))


def try_load_background(size):
	base_dirs = [Path(__file__).parent]
	if getattr(sys, "frozen", False):
		base_dirs.insert(0, Path(sys.executable).resolve().parent)
		meipass = getattr(sys, "_MEIPASS", None)
		if meipass:
			base_dirs.insert(0, Path(meipass))

	filenames = [
		"filed.png",
		"filed.jpg",
		"filed.jpeg",
		"field.jpg",
		"field.jpeg",
		"field.png",
		"pitch.jpg",
		"pitch.png",
	]
	candidates = [base_dir / filename for base_dir in base_dirs for filename in filenames]
	for path in candidates:
		if path.exists():
			image = pygame.image.load(str(path)).convert()
			img_w, img_h = image.get_size()
			if img_w <= 0 or img_h <= 0:
				continue

			scale = min(PITCH_RECT.width / img_w, PITCH_RECT.height / img_h)
			target_w = max(1, int(img_w * scale))
			target_h = max(1, int(img_h * scale))
			scaled = pygame.transform.smoothscale(image, (target_w, target_h))
			rect = scaled.get_rect(center=PITCH_RECT.center)
			return scaled, rect
	return None, None


def find_app_icon_path():
	base_dirs = [Path(__file__).parent]
	if getattr(sys, "frozen", False):
		base_dirs.insert(0, Path(sys.executable).resolve().parent)
		meipass = getattr(sys, "_MEIPASS", None)
		if meipass:
			base_dirs.insert(0, Path(meipass))

	for base_dir in base_dirs:
		asset_icon = base_dir / ASSETS_DIR_NAME / APP_ICON_FILE
		if asset_icon.exists():
			return asset_icon
		plain_icon = base_dir / APP_ICON_FILE
		if plain_icon.exists():
			return plain_icon
	return None


def configure_windows_taskbar_identity():
	if sys.platform != "win32":
		return
	try:
		import ctypes
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_ID)
	except Exception:
		# Keep running even when Windows API is unavailable.
		pass


def apply_window_icon():
	icon_path = find_app_icon_path()
	if icon_path is None:
		return
	if sys.platform == "win32":
		apply_windows_taskbar_icon(icon_path)
	try:
		pygame.display.set_icon(pygame.image.load(str(icon_path)))
	except pygame.error:
		# Some pygame/SDL builds cannot decode .ico; taskbar icon is still set via Win32.
		return


def apply_windows_taskbar_icon(icon_path):
	try:
		import ctypes
		from ctypes import wintypes

		wm_info = pygame.display.get_wm_info()
		hwnd = wm_info.get("window")
		if not hwnd:
			return

		IMAGE_ICON = 1
		LR_LOADFROMFILE = 0x0010
		LR_DEFAULTSIZE = 0x0040
		WM_SETICON = 0x0080
		ICON_SMALL = 0
		ICON_BIG = 1

		user32 = ctypes.windll.user32
		user32.LoadImageW.argtypes = [
			wintypes.HINSTANCE,
			wintypes.LPCWSTR,
			wintypes.UINT,
			ctypes.c_int,
			ctypes.c_int,
			wintypes.UINT,
		]
		user32.LoadImageW.restype = wintypes.HANDLE

		h_icon = user32.LoadImageW(None, str(icon_path), IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
		if not h_icon:
			return

		user32.SendMessageW(wintypes.HWND(hwnd), WM_SETICON, ICON_SMALL, h_icon)
		user32.SendMessageW(wintypes.HWND(hwnd), WM_SETICON, ICON_BIG, h_icon)
	except Exception:
		pass


def draw_fallback_pitch(surface, area_rect):
	pygame.draw.rect(surface, (95, 145, 65), area_rect)
	width, height = area_rect.width, area_rect.height
	margin = 40
	white = (240, 240, 240)
	offset_x = area_rect.x
	offset_y = area_rect.y

	pygame.draw.rect(surface, white, (offset_x + margin, offset_y + margin, width - 2 * margin, height - 2 * margin), 4)
	pygame.draw.line(surface, white, (offset_x + width // 2, offset_y + margin), (offset_x + width // 2, offset_y + height - margin), 4)
	pygame.draw.circle(surface, white, (offset_x + width // 2, offset_y + height // 2), 80, 4)

	box_w, box_h = 170, 320
	pygame.draw.rect(surface, white, (offset_x + margin, offset_y + (height - box_h) // 2, box_w, box_h), 4)
	pygame.draw.rect(surface, white, (offset_x + width - margin - box_w, offset_y + (height - box_h) // 2, box_w, box_h), 4)


def create_default_players(size):
	def pos(rx, ry):
		pitch_rect = get_pitch_rect()
		x = int(pitch_rect.left + rx * pitch_rect.width)
		y = int(pitch_rect.top + ry * pitch_rect.height)
		return x, y

	left_layout = get_team_formation_layout("left", DEFAULT_FORMATION)
	right_layout = get_team_formation_layout("right", DEFAULT_FORMATION)

	left_team = [
		Player(*pos(rx, ry), (255, 190, 0), label)
		for label, rx, ry in left_layout
	]

	right_team = [
		Player(*pos(rx, ry), (30, 120, 255), label)
		for label, rx, ry in right_layout
	]

	for player in left_team:
		player.team = "left"
		player.starter = True
	for player in right_team:
		player.team = "right"
		player.starter = True

	return left_team + right_team


def build_tool_buttons():
	left_team_toggle = pygame.Rect(30, 20, 75, 24)
	right_team_toggle = pygame.Rect(115, 20, 75, 24)
	move_button = pygame.Rect(30, 55, 75, 34)
	laser_button = pygame.Rect(115, 55, 75, 34)
	zone_button = pygame.Rect(30, 95, 160, 34)
	link_button = pygame.Rect(30, 135, 160, 34)
	capture_button = pygame.Rect(30, 175, 160, 34)
	color_left_button = pygame.Rect(30, 215, 75, 34)
	color_right_button = pygame.Rect(115, 215, 75, 34)
	load_left_roster_button = pygame.Rect(30, 255, 160, 34)
	save_left_roster_button = pygame.Rect(30, 295, 160, 34)
	load_right_roster_button = pygame.Rect(30, 335, 160, 34)
	save_right_roster_button = pygame.Rect(30, 375, 160, 34)
	load_fotmob_button = pygame.Rect(30, 415, 160, 34)
	draw_button = pygame.Rect(30, 455, 160, 34)
	clear_all_button = pygame.Rect(30, 495, 160, 28)
	return {
		TOOL_TOGGLE_LEFT_TEAM: left_team_toggle,
		TOOL_TOGGLE_RIGHT_TEAM: right_team_toggle,
		MODE_MOVE: move_button,
		MODE_LASER: laser_button,
		MODE_ZONE: zone_button,
		MODE_LINK: link_button,
		TOOL_CAPTURE: capture_button,
		TOOL_COLOR_LEFT: color_left_button,
		TOOL_COLOR_RIGHT: color_right_button,
		TOOL_LOAD_LEFT_ROSTER: load_left_roster_button,
		TOOL_SAVE_LEFT_ROSTER: save_left_roster_button,
		TOOL_LOAD_RIGHT_ROSTER: load_right_roster_button,
		TOOL_SAVE_RIGHT_ROSTER: save_right_roster_button,
		TOOL_LOAD_FOTMOB: load_fotmob_button,
		MODE_DRAW: draw_button,
		TOOL_CLEAR_ALL: clear_all_button,
	}

def draw_tool_panel(surface, font, mode, buttons, team_name_visibility):
	pygame.draw.rect(surface, (220, 220, 220), TOOL_PANEL_RECT, 2, border_radius=10)

	for key, rect in buttons.items():
		if key == TOOL_TOGGLE_LEFT_TEAM:
			name_visible = team_name_visibility.get("left", True)
			active = name_visible
			fill_color = (60, 170, 90) if name_visible else (70, 80, 95)
			label = "L Name"
		elif key == TOOL_TOGGLE_RIGHT_TEAM:
			name_visible = team_name_visibility.get("right", True)
			active = name_visible
			fill_color = (60, 170, 90) if name_visible else (70, 80, 95)
			label = "R Name"
		else:
			active = key == mode
			fill_color = (60, 170, 90) if active else (70, 80, 95)
			if key == MODE_MOVE:
				label = "Move"
			elif key == MODE_LASER:
				label = "Laser"
			elif key == MODE_ZONE:
				label = "Circle"
			elif key == MODE_LINK:
				label = "Link"
			elif key == TOOL_LOAD_LEFT_ROSTER:
				label = "Load L"
			elif key == TOOL_SAVE_LEFT_ROSTER:
				label = "Save L"
			elif key == TOOL_LOAD_RIGHT_ROSTER:
				label = "Load R"
			elif key == TOOL_SAVE_RIGHT_ROSTER:
				label = "Save R"
			elif key == TOOL_COLOR_LEFT:
				label = "Color L"
			elif key == TOOL_COLOR_RIGHT:
				label = "Color R"
			elif key == TOOL_LOAD_FOTMOB:
				label = "FotMob"
			elif key == MODE_DRAW:
				label = "Draw"
			elif key == TOOL_CLEAR_ALL:
				label = "Clear All"
			else:
				label = "Capture"
		pygame.draw.rect(surface, fill_color, rect, border_radius=8)
		pygame.draw.rect(surface, (220, 220, 220), rect, 2, border_radius=8)
		text = font.render(label, True, (255, 255, 255))
		surface.blit(text, text.get_rect(center=rect.center))

	help_text1 = "M:Move  L:Laser  C:Circle"
	help_text2 = "V:Link  D:Draw"
	help1 = font.render(help_text1, True, (230, 230, 230))
	help2 = font.render(help_text2, True, (230, 230, 230))
	surface.blit(help1, (TOOL_PANEL_RECT.x + 12, TOOL_PANEL_RECT.y + 528))
	surface.blit(help2, (TOOL_PANEL_RECT.x + 12, TOOL_PANEL_RECT.y + 543))


def draw_team_color_menu(surface, font, menu_rect, team_name, hovered_idx, current_color):
	panel = pygame.Surface((menu_rect.width, menu_rect.height), pygame.SRCALPHA)
	panel.fill((12, 18, 28, 220))
	surface.blit(panel, menu_rect.topleft)
	pygame.draw.rect(surface, (230, 230, 230), menu_rect, 2, border_radius=8)

	title_text = "Left Team Color" if team_name == "left" else "Right Team Color"
	title = font.render(title_text, True, (245, 245, 245))
	surface.blit(title, (menu_rect.x + 10, menu_rect.y + 8))

	for idx, (name, color_value) in enumerate(PLAYER_COLOR_OPTIONS):
		row_rect = get_menu_row_rect(menu_rect, idx)
		fill = (72, 104, 140) if idx == hovered_idx else (58, 65, 80)
		pygame.draw.rect(surface, fill, row_rect, border_radius=6)
		text_surf = font.render(name, True, (255, 255, 255))
		surface.blit(text_surf, text_surf.get_rect(midleft=(row_rect.x + 8, row_rect.centery)))

		swatch_rect = pygame.Rect(row_rect.right - 32, row_rect.y + 4, 22, row_rect.height - 8)
		pygame.draw.rect(surface, color_value, swatch_rect, border_radius=4)
		border_color = (255, 240, 90) if color_value == current_color else (240, 240, 240)
		border_width = 2 if color_value == current_color else 1
		pygame.draw.rect(surface, border_color, swatch_rect, border_width, border_radius=4)

	hint_surf = font.render("select color", True, (210, 210, 210))
	surface.blit(hint_surf, (menu_rect.x + 10, menu_rect.bottom - 20))


def draw_player_links(surface, links, active_indices=None):
	if not links:
		return
	if active_indices is None:
		active_indices = set()
	overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
	for idx, (start_player, end_player) in enumerate(links):
		start = (int(start_player.x), int(start_player.y))
		end = (int(end_player.x), int(end_player.y))
		is_active = idx in active_indices
		if is_active:
			pygame.draw.line(overlay, (255, 235, 90, 120), start, end, 14)
			pygame.draw.line(overlay, (255, 245, 150, 255), start, end, 7)
		else:
			pygame.draw.line(overlay, (50, 255, 240, 90), start, end, 10)
			pygame.draw.line(overlay, (50, 255, 240, 245), start, end, 5)
	surface.blit(overlay, (0, 0))


def load_roster_menu_items():
	files = list_roster_files()
	items = [(file_path.name, str(file_path)) for file_path in files]
	if not items:
		items = [("No roster txt found", "")]
	return items


def draw_file_menu(surface, font, menu_rect, items, hovered_idx, title_text):
	panel = pygame.Surface((menu_rect.width, menu_rect.height), pygame.SRCALPHA)
	panel.fill((12, 18, 28, 220))
	surface.blit(panel, menu_rect.topleft)
	pygame.draw.rect(surface, (230, 230, 230), menu_rect, 2, border_radius=8)

	title = font.render(title_text, True, (245, 245, 245))
	surface.blit(title, (menu_rect.x + 10, menu_rect.y + 8))

	for idx, (name, path_str) in enumerate(items):
		row_rect = get_menu_row_rect(menu_rect, idx)
		fill = (72, 104, 140) if idx == hovered_idx else (58, 65, 80)
		pygame.draw.rect(surface, fill, row_rect, border_radius=6)
		text_surf = font.render(name, True, (255, 255, 255))
		surface.blit(text_surf, text_surf.get_rect(midleft=(row_rect.x + 8, row_rect.centery)))


def open_roster_menu(event_pos):
	items = load_roster_menu_items()
	menu_rect = build_candidate_menu(event_pos, len(items))
	return items, menu_rect


def draw_hatched_zone(surface, center, radius, alpha_scale=1.0):
	if radius <= 0:
		return

	size = radius * 2 + 6
	local_center = (size // 2, size // 2)
	top_left = (center[0] - local_center[0], center[1] - local_center[1])

	fill_layer = pygame.Surface((size, size), pygame.SRCALPHA)
	fill_alpha = int(65 * alpha_scale)
	pygame.draw.circle(fill_layer, (255, 255, 255, fill_alpha), local_center, radius)

	stripe_layer = pygame.Surface((size, size), pygame.SRCALPHA)
	stripe_alpha = int(115 * alpha_scale)
	for sx in range(-size, size * 2, ZONE_STRIPE_GAP):
		start = (sx, size)
		end = (sx + size, 0)
		pygame.draw.line(stripe_layer, (255, 255, 255, stripe_alpha), start, end, ZONE_STRIPE_WIDTH)

	mask_layer = pygame.Surface((size, size), pygame.SRCALPHA)
	pygame.draw.circle(mask_layer, (255, 255, 255, 255), local_center, radius)
	stripe_layer.blit(mask_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

	surface.blit(fill_layer, top_left)
	surface.blit(stripe_layer, top_left)
	pygame.draw.circle(surface, (240, 240, 240), center, radius, 3)


def draw_laser_stroke(surface, points, alpha_scale=1.0):
	if len(points) == 0:
		return

	overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
	for i in range(1, len(points)):
		start = points[i - 1]
		end = points[i]
		ratio = i / max(1, len(points) - 1)
		glow_w = 10 + int(6 * ratio)
		beam_w = 5 + int(3 * ratio)
		core_w = 2 + int(2 * ratio)
		pygame.draw.line(overlay, (255, 35, 25, int(115 * alpha_scale)), start, end, glow_w)
		pygame.draw.line(overlay, (255, 70, 55, int(180 * alpha_scale)), start, end, beam_w)
		pygame.draw.line(overlay, (255, 255, 255, int(245 * alpha_scale)), start, end, core_w)

	px, py = points[-1]
	pygame.draw.circle(overlay, (255, 30, 20, int(130 * alpha_scale)), (px, py), 14)
	pygame.draw.circle(overlay, (255, 75, 60, int(180 * alpha_scale)), (px, py), 8)
	pygame.draw.circle(overlay, (255, 255, 255, int(255 * alpha_scale)), (px, py), 4)
	surface.blit(overlay, (0, 0))


def pick_draw_stroke_at(strokes, pos, tolerance=8):
	mx, my = pos
	threshold = tolerance * tolerance
	for idx in range(len(strokes) - 1, -1, -1):
		stroke = strokes[idx]
		for i in range(1, len(stroke)):
			if point_to_segment_distance_sq(mx, my, *stroke[i - 1], *stroke[i]) <= threshold:
				return idx
	return None


def draw_freehand_strokes(surface, strokes, active_idx=None):
	if not strokes:
		return
	overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
	for idx, stroke in enumerate(strokes):
		if len(stroke) < 2:
			continue
		is_active = idx == active_idx
		color = (255, 90, 90, 255) if is_active else (255, 220, 50, 230)
		width = 5 if is_active else 3
		for i in range(1, len(stroke)):
			pygame.draw.line(overlay, color, stroke[i - 1], stroke[i], width)
	surface.blit(overlay, (0, 0))


def main():
	pygame.init()
	configure_windows_taskbar_identity()
	screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
	pygame.display.set_caption("Tactical Pad")
	apply_window_icon()
	clock = pygame.time.Clock()
	font = pygame.font.SysFont("arial", 14, bold=True)
	info_font = pygame.font.SysFont("arial", 14, bold=True)
	mode_font = pygame.font.SysFont("arial", 18, bold=True)

	background, background_rect = try_load_background(WINDOW_SIZE)
	players = create_default_players(WINDOW_SIZE)
	team_formations = {
		"left": DEFAULT_FORMATION,
		"right": DEFAULT_FORMATION,
	}
	tool_buttons = build_tool_buttons()

	selected = None
	selected_zone_idx = None
	active_zone_idx = None
	zone_drag_offset = (0, 0)
	offset_x = 0
	offset_y = 0
	mode = MODE_MOVE
	laser_active = False
	laser_pos = None
	laser_points = []
	laser_fade_frames = 0
	capture_notice_frames = 0
	capture_notice_text = ""
	player_links = []
	link_start_player = None
	active_link_indices = set()
	roster_menu_open = False
	roster_menu_rect = None
	roster_menu_items = []
	roster_menu_hover_idx = -1
	zones = []
	zone_drawing = False
	zone_anchor = None
	zone_center = None
	zone_radius = 0
	menu_open = False
	menu_target_player = None
	menu_rect = None
	menu_items = []
	menu_hover_idx = -1
	menu_selectable = False
	menu_pick_mode = MENU_PICK_NAME
	menu_candidates = []
	team_color_menu_open = False
	team_color_menu_rect = None
	team_color_menu_team = None
	team_color_menu_hover_idx = -1
	team_name_visibility = {
		"left": True,
		"right": True,
	}
	candidate_file = Path(__file__).parent / PLAYER_INFO_FILE
	fotmob_candidates = {
		"left": [],
		"right": [],
	}
	draw_strokes = []
	current_draw_stroke = []
	draw_active = False
	active_draw_stroke_idx = None
	pending_capture = False
	running = True

	while running:
		for event in pygame.event.get():
			if event.type == pygame.VIDEORESIZE:
				# 창 크기 변경 시 처리
				WINDOW_SIZE[0], WINDOW_SIZE[1] = event.w, event.h
				screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
				global PITCH_RECT
				PITCH_RECT = get_pitch_rect()
				# 선수, 존 등 위치를 비율로 재계산
				def update_player_positions():
					for team_name in ("left", "right"):
						formation = team_formations.get(team_name, DEFAULT_FORMATION)
						apply_team_formation(players, team_name, formation)
				update_player_positions()
				background, background_rect = try_load_background(WINDOW_SIZE)
			if event.type == pygame.QUIT:
				running = False

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_m:
					mode = MODE_MOVE
					laser_active = False
					laser_pos = None
					laser_points.clear()
					laser_fade_frames = 0
					selected_zone_idx = None
					active_zone_idx = None
					active_link_indices.clear()
				elif event.key == pygame.K_l:
					mode = MODE_LASER
					selected_zone_idx = None
					active_zone_idx = None
					active_link_indices.clear()
				elif event.key == pygame.K_c:
					mode = MODE_ZONE
					selected_zone_idx = None
					active_zone_idx = None
					active_link_indices.clear()
				elif event.key == pygame.K_v:
					mode = MODE_LINK
					selected_zone_idx = None
					active_zone_idx = None
					selected = None
					link_start_player = None
				elif event.key == pygame.K_d:
					mode = MODE_DRAW
					selected = None
					selected_zone_idx = None
					active_zone_idx = None
					active_link_indices.clear()
					link_start_player = None
				elif event.key == pygame.K_DELETE and mode == MODE_DRAW:
					if active_draw_stroke_idx is not None and 0 <= active_draw_stroke_idx < len(draw_strokes):
						draw_strokes.pop(active_draw_stroke_idx)
						active_draw_stroke_idx = None
					else:
						draw_strokes.clear()
						current_draw_stroke.clear()
				elif event.key == pygame.K_DELETE and mode == MODE_MOVE:
					if active_link_indices:
						player_links = [
							link for idx, link in enumerate(player_links)
							if idx not in active_link_indices
						]
						active_link_indices.clear()
						link_start_player = None
					elif active_zone_idx is not None and 0 <= active_zone_idx < len(zones):
						zones.pop(active_zone_idx)
						active_zone_idx = None
						selected_zone_idx = None
				elif event.key == pygame.K_DELETE and mode == MODE_LINK:
					if active_link_indices:
						player_links = [
							link for idx, link in enumerate(player_links)
							if idx not in active_link_indices
						]
						active_link_indices.clear()
						link_start_player = None

			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mx, my = event.pos
				clicked_tool = False

				for key in (TOOL_TOGGLE_LEFT_TEAM, TOOL_TOGGLE_RIGHT_TEAM):
					rect = tool_buttons.get(key)
					if rect is not None and rect.collidepoint(mx, my):
						team_name = "left" if key == TOOL_TOGGLE_LEFT_TEAM else "right"
						team_name_visibility[team_name] = not team_name_visibility[team_name]
						clicked_tool = True
						break

				if clicked_tool:
					continue

				if team_color_menu_open:
					if team_color_menu_rect is not None and team_color_menu_rect.collidepoint(mx, my):
						if 0 <= team_color_menu_hover_idx < len(PLAYER_COLOR_OPTIONS):
							_, color_value = PLAYER_COLOR_OPTIONS[team_color_menu_hover_idx]
							apply_team_color(players, team_color_menu_team, color_value)
							team_label = "Left" if team_color_menu_team == "left" else "Right"
							capture_notice_text = f"{team_label} team color updated"
							capture_notice_frames = CAPTURE_NOTICE_FRAMES
					team_color_menu_open = False
					team_color_menu_rect = None
					team_color_menu_team = None
					team_color_menu_hover_idx = -1
					continue

				if menu_open:
					if menu_rect is not None and menu_rect.collidepoint(mx, my):
						name_tab, number_tab, position_tab = get_menu_tab_rects(menu_rect)
						if name_tab.collidepoint(mx, my):
							menu_pick_mode = MENU_PICK_NAME
							base_items = get_menu_items(menu_candidates, menu_pick_mode)
							if base_items:
								menu_items = base_items[:MENU_MAX_ROWS]
								menu_selectable = True
							else:
								menu_items = [("No candidates available", "")]
								menu_selectable = False
							menu_rect = build_candidate_menu((menu_rect.x, menu_rect.y), len(menu_items))
							menu_hover_idx = -1
							continue
						if number_tab.collidepoint(mx, my):
							menu_pick_mode = MENU_PICK_NUMBER
							base_items = get_menu_items(menu_candidates, menu_pick_mode)
							if base_items:
								menu_items = base_items[:MENU_MAX_ROWS]
								menu_selectable = True
							else:
								menu_items = [("No candidates available", "")]
								menu_selectable = False
							menu_rect = build_candidate_menu((menu_rect.x, menu_rect.y), len(menu_items))
							menu_hover_idx = -1
							continue
						if position_tab.collidepoint(mx, my):
							menu_pick_mode = MENU_PICK_POSITION
							menu_items = get_menu_items(menu_candidates, menu_pick_mode)[:MENU_MAX_ROWS]
							menu_selectable = True
							menu_rect = build_candidate_menu((menu_rect.x, menu_rect.y), len(menu_items))
							menu_hover_idx = -1
							continue
						if menu_selectable and 0 <= menu_hover_idx < len(menu_items) and menu_target_player is not None:
							name, number = menu_items[menu_hover_idx]
							if menu_pick_mode == MENU_PICK_POSITION:
								menu_target_player.label = name
							else:
								menu_target_player.player_name = name
								menu_target_player.jersey_no = number
								menu_target_player.info_mode = menu_pick_mode
					menu_open = False
					menu_target_player = None
					menu_rect = None
					menu_items = []
					menu_hover_idx = -1
					menu_selectable = False
					menu_candidates = []
					continue

				clicked_tool = False
				for key, rect in tool_buttons.items():
					if key in (TOOL_TOGGLE_LEFT_TEAM, TOOL_TOGGLE_RIGHT_TEAM):
						continue
					if rect.collidepoint(mx, my):
						if key == TOOL_CAPTURE:
							pending_capture = True
						elif key == TOOL_COLOR_LEFT or key == TOOL_COLOR_RIGHT:
							team_color_menu_open = True
							team_color_menu_team = "left" if key == TOOL_COLOR_LEFT else "right"
							team_color_menu_rect = build_candidate_menu((TOOL_PANEL_RECT.right + 10, rect.y), len(PLAYER_COLOR_OPTIONS))
							team_color_menu_hover_idx = -1
						elif key == TOOL_LOAD_LEFT_ROSTER:
							selected_roster = pick_roster_open_file("Load Left Team Roster File", "left")
							if selected_roster is not None and selected_roster.exists():
								loaded_count, loaded_formation = load_team_roster(players, selected_roster, "left")
								team_formations["left"] = loaded_formation
								if loaded_count > 0:
									capture_notice_text = f"Loaded: {selected_roster.name} ({loaded_formation})"
								else:
									capture_notice_text = f"No left-team starters in file ({loaded_formation})"
								capture_notice_frames = CAPTURE_NOTICE_FRAMES
						elif key == TOOL_LOAD_RIGHT_ROSTER:
							selected_roster = pick_roster_open_file("Load Right Team Roster File", "right")
							if selected_roster is not None and selected_roster.exists():
								loaded_count, loaded_formation = load_team_roster(players, selected_roster, "right")
								team_formations["right"] = loaded_formation
								if loaded_count > 0:
									capture_notice_text = f"Loaded: {selected_roster.name} ({loaded_formation})"
								else:
									capture_notice_text = f"No right-team starters in file ({loaded_formation})"
								capture_notice_frames = CAPTURE_NOTICE_FRAMES
						elif key == TOOL_SAVE_LEFT_ROSTER:
							selected_roster = pick_roster_save_file("Save Left Team Roster File", "left")
							if selected_roster is not None:
								formation = team_formations.get("left", DEFAULT_FORMATION)
								path = save_team_roster(selected_roster, players, "left", formation)
								capture_notice_text = f"Saved: {path.name}"
								capture_notice_frames = CAPTURE_NOTICE_FRAMES
						elif key == TOOL_SAVE_RIGHT_ROSTER:
							selected_roster = pick_roster_save_file("Save Right Team Roster File", "right")
							if selected_roster is not None:
								formation = team_formations.get("right", DEFAULT_FORMATION)
								path = save_team_roster(selected_roster, players, "right", formation)
								capture_notice_text = f"Saved: {path.name}"
								capture_notice_frames = CAPTURE_NOTICE_FRAMES
						elif key == TOOL_LOAD_FOTMOB:
							fotmob_url = prompt_fotmob_url()
							if fotmob_url:
								try:
									next_data = fetch_fotmob_next_data(fotmob_url)
									lineups = parse_fotmob_lineups(next_data)
									left_lineup = lineups["left"]
									right_lineup = lineups["right"]
									apply_starters_to_team(players, "left", left_lineup["starters"])
									apply_starters_to_team(players, "right", right_lineup["starters"])
									fotmob_candidates["left"] = build_candidates_from_entries(
										left_lineup["starters"] + left_lineup["bench"]
									)
									fotmob_candidates["right"] = build_candidates_from_entries(
										right_lineup["starters"] + right_lineup["bench"]
									)
									candidate_file = Path(__file__).parent / "fotmob_lineup.txt"
									left_name = left_lineup["team_name"] or "Home"
									right_name = right_lineup["team_name"] or "Away"
									capture_notice_text = (
										f"FotMob loaded (Home->Left, Away->Right): {left_name} vs {right_name} | "
										f"bench {len(left_lineup['bench']) + len(right_lineup['bench'])}"
									)
								except Exception as exc:
									capture_notice_text = f"FotMob load failed: {exc}"
								capture_notice_frames = CAPTURE_NOTICE_FRAMES
						elif key == TOOL_CLEAR_ALL:
							try:
								root = tk.Tk()
								root.withdraw()
								confirmed = messagebox.askyesno(
									title="Clear All",
									message="Remove all circles, links, and drawings?",
									parent=root,
								)
								root.destroy()
							except Exception:
								confirmed = False
							if confirmed:
								zones.clear()
								player_links.clear()
								draw_strokes.clear()
								current_draw_stroke.clear()
								laser_points.clear()
								active_draw_stroke_idx = None
								active_zone_idx = None
								active_link_indices.clear()
								capture_notice_text = "Cleared all overlays"
								capture_notice_frames = CAPTURE_NOTICE_FRAMES
						else:
							mode = key
						selected = None
						selected_zone_idx = None
						active_zone_idx = None
						laser_active = False
						laser_pos = None
						laser_points.clear()
						laser_fade_frames = 0
						link_start_player = None
						active_link_indices.clear()
						clicked_tool = True
						break

				if clicked_tool:
					continue

				if mode == MODE_MOVE:
					selected = None
					for player in reversed(players):
						if player.contains(mx, my):
							selected = player
							selected_zone_idx = None
							active_zone_idx = None
							active_link_indices.clear()
							offset_x = player.x - mx
							offset_y = player.y - my
							players.remove(player)
							players.append(player)
							break
					if selected is None:
						picked_zone_idx = pick_zone_at(zones, (mx, my))
						if picked_zone_idx is not None:
							selected_zone_idx = picked_zone_idx
							active_zone_idx = picked_zone_idx
							active_link_indices.clear()
							zcx, zcy = zones[picked_zone_idx]["center"]
							zone_drag_offset = (zcx - mx, zcy - my)
						else:
							active_zone_idx = None
							picked_link_idx = pick_link_at(player_links, (mx, my))
							active_link_indices = get_connected_link_indices(player_links, picked_link_idx)
				elif mode == MODE_LASER:
					laser_active = True
					laser_pos = (mx, my)
					laser_points = [laser_pos]
					laser_fade_frames = 0
					selected_zone_idx = None
					active_zone_idx = None
					active_link_indices.clear()
				elif mode == MODE_ZONE:
					zone_drawing = True
					zone_anchor = (mx, my)
					zone_center = (mx, my)
					zone_radius = 0
					selected_zone_idx = None
					active_zone_idx = None
					active_link_indices.clear()
				elif mode == MODE_LINK:
					target_player = pick_player_at(players, (mx, my))
					selected_zone_idx = None
					active_zone_idx = None
					selected = None
					if target_player is None:
						picked_link_idx = pick_link_at(player_links, (mx, my))
						active_link_indices = get_connected_link_indices(player_links, picked_link_idx)
						link_start_player = None
					else:
						active_link_indices.clear()
						if link_start_player is None:
							link_start_player = target_player
						elif link_start_player is target_player:
							link_start_player = None
						else:
							exists = any(
								(start_player is link_start_player and end_player is target_player)
								or (start_player is target_player and end_player is link_start_player)
								for start_player, end_player in player_links
							)
							if not exists:
								player_links.append((link_start_player, target_player))
							link_start_player = target_player
				elif mode == MODE_DRAW:
					near_idx = pick_draw_stroke_at(draw_strokes, (mx, my))
					if near_idx is not None:
						active_draw_stroke_idx = near_idx
					else:
						active_draw_stroke_idx = None
						draw_active = True
						current_draw_stroke = [(mx, my)]

			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
				if team_color_menu_open:
					team_color_menu_open = False
					team_color_menu_rect = None
					team_color_menu_team = None
					team_color_menu_hover_idx = -1
					continue

				target_player = pick_player_at(players, event.pos)
				if target_player is None:
					menu_open = False
					menu_target_player = None
					menu_rect = None
					menu_items = []
					menu_hover_idx = -1
					menu_selectable = False
					menu_candidates = []
					continue

				team_candidates = fotmob_candidates.get(target_player.team, [])
				candidates, candidate_file = get_available_candidates(
					players,
					team_candidates,
					team_name=target_player.team,
				)
				menu_candidates = candidates
				if not menu_candidates:
					menu_items = [("No candidates available", "")]
					menu_selectable = False
				else:
					menu_items = get_menu_items(menu_candidates, menu_pick_mode)[:MENU_MAX_ROWS]
					menu_selectable = True

				menu_target_player = target_player
				menu_rect = build_candidate_menu(event.pos, len(menu_items))
				menu_open = True
				menu_hover_idx = -1
				selected = None
				laser_active = False
				laser_pos = None
				laser_points.clear()
				laser_fade_frames = 0
				link_start_player = None
				active_link_indices.clear()

			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				selected = None
				selected_zone_idx = None
				laser_active = False
				laser_pos = None
				if laser_points:
					laser_fade_frames = LASER_FADE_FRAMES
				if zone_drawing and zone_center is not None and zone_radius >= ZONE_MIN_RADIUS:
					zones.append({"center": zone_center, "radius": zone_radius})
				zone_drawing = False
				zone_anchor = None
				zone_center = None
				zone_radius = 0
				if draw_active and len(current_draw_stroke) >= 2:
					draw_strokes.append(list(current_draw_stroke))
				draw_active = False
				current_draw_stroke = []

			elif event.type == pygame.MOUSEMOTION and mode == MODE_MOVE and selected is not None:
				mx, my = event.pos
				selected.x = max(PITCH_RECT.left + PLAYER_RADIUS, min(PITCH_RECT.right - PLAYER_RADIUS, mx + offset_x))
				selected.y = max(PLAYER_RADIUS, min(WINDOW_SIZE[1] - PLAYER_RADIUS, my + offset_y))

			elif event.type == pygame.MOUSEMOTION and mode == MODE_MOVE and selected_zone_idx is not None:
				mx, my = event.pos
				zone = zones[selected_zone_idx]
				radius = zone["radius"]
				new_x = max(PITCH_RECT.left + radius, min(PITCH_RECT.right - radius, mx + zone_drag_offset[0]))
				new_y = max(radius, min(WINDOW_SIZE[1] - radius, my + zone_drag_offset[1]))
				zone["center"] = (new_x, new_y)

			elif event.type == pygame.MOUSEMOTION and mode == MODE_LASER and laser_active:
				laser_pos = event.pos
				if not laser_points:
					laser_points.append(laser_pos)
				else:
					last_x, last_y = laser_points[-1]
					dx = laser_pos[0] - last_x
					dy = laser_pos[1] - last_y
					if dx * dx + dy * dy >= LASER_DRAW_MIN_DIST_SQ:
						laser_points.append(laser_pos)

			elif event.type == pygame.MOUSEMOTION and mode == MODE_ZONE and zone_drawing and zone_anchor is not None:
				ax, ay = zone_anchor
				cx, cy = event.pos
				center_x = (ax + cx) // 2
				center_y = (ay + cy) // 2
				radius = int(max(abs(cx - ax), abs(cy - ay)) / 2)
				zone_center = (center_x, center_y)
				zone_radius = radius

			elif event.type == pygame.MOUSEMOTION and mode == MODE_DRAW and draw_active:
				mx, my = event.pos
				if not current_draw_stroke:
					current_draw_stroke.append((mx, my))
				else:
					lx, ly = current_draw_stroke[-1]
					dx, dy = mx - lx, my - ly
					if dx * dx + dy * dy >= LASER_DRAW_MIN_DIST_SQ:
						current_draw_stroke.append((mx, my))

			if event.type == pygame.MOUSEMOTION and menu_open and menu_rect is not None:
				menu_hover_idx = -1
				for idx in range(len(menu_items)):
					row_rect = get_menu_row_rect(menu_rect, idx)
					if row_rect.collidepoint(event.pos):
						menu_hover_idx = idx
						break

			if event.type == pygame.MOUSEMOTION and team_color_menu_open and team_color_menu_rect is not None:
				team_color_menu_hover_idx = -1
				for idx in range(len(PLAYER_COLOR_OPTIONS)):
					row_rect = get_menu_row_rect(team_color_menu_rect, idx)
					if row_rect.collidepoint(event.pos):
						team_color_menu_hover_idx = idx
						break

		if background is not None and background_rect is not None:
			screen.fill(LETTERBOX_COLOR)
			screen.blit(background, background_rect)
		else:
			screen.fill(LETTERBOX_COLOR)
			draw_fallback_pitch(screen, PITCH_RECT)

		if not laser_active and laser_fade_frames > 0:
			laser_fade_frames -= 1
			if laser_fade_frames <= 0:
				laser_points.clear()

		for idx, zone in enumerate(zones):
			draw_hatched_zone(screen, zone["center"], zone["radius"])
			if idx == active_zone_idx:
				pygame.draw.circle(screen, (255, 235, 90), zone["center"], zone["radius"] + 2, 2)

		if mode == MODE_ZONE and zone_drawing and zone_center is not None and zone_radius > 0:
			draw_hatched_zone(screen, zone_center, zone_radius, alpha_scale=0.7)

		draw_player_links(screen, player_links, active_indices=active_link_indices)
		draw_freehand_strokes(screen, draw_strokes, active_idx=active_draw_stroke_idx)
		if draw_active and len(current_draw_stroke) >= 2:
			draw_freehand_strokes(screen, [current_draw_stroke])

		for player in players:
			show_info_label = team_name_visibility.get(player.team, True)
			player.draw(screen, font, info_font, show_info_label=show_info_label)

		if mode == MODE_LINK and link_start_player is not None:
			pygame.draw.circle(screen, (255, 240, 90), (link_start_player.x, link_start_player.y), PLAYER_RADIUS + 5, 3)

		if laser_active and laser_points:
			draw_laser_stroke(screen, laser_points, alpha_scale=1.0)
		elif laser_points and laser_fade_frames > 0:
			fade_ratio = laser_fade_frames / LASER_FADE_FRAMES
			draw_laser_stroke(screen, laser_points, alpha_scale=fade_ratio)

		if pending_capture:
			# exe 빌드 환경에서도 안전하게 저장 경로 지정
			if getattr(sys, 'frozen', False):
				base_dir = Path(sys.executable).parent
			else:
				base_dir = Path(__file__).parent
			capture_dir = base_dir / CAPTURE_DIR_NAME
			capture_dir.mkdir(parents=True, exist_ok=True)
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			capture_path = capture_dir / f"tactical_{timestamp}.png"
			pygame.image.save(screen, str(capture_path))
			pending_capture = False
			capture_notice_text = f"Saved: {capture_path.name}"
			capture_notice_frames = CAPTURE_NOTICE_FRAMES

		draw_tool_panel(screen, font, mode, tool_buttons, team_name_visibility)
		if mode == MODE_MOVE:
			mode_text = "Mode: Move"
		elif mode == MODE_LASER:
			mode_text = "Mode: Laser"
		elif mode == MODE_ZONE:
			mode_text = "Mode: Circle"
		elif mode == MODE_LINK:
			mode_text = "Mode: Link"
		elif mode == MODE_DRAW:
			mode_text = "Mode: Draw  (Del: clear)"
		else:
			mode_text = "Mode: Tool"
		mode_surface = mode_font.render(mode_text, True, (255, 255, 255))
		screen.blit(mode_surface, (20, WINDOW_SIZE[1] - 38))

		if menu_open and menu_rect is not None:
			draw_candidate_menu(screen, font, menu_rect, menu_items, menu_hover_idx, candidate_file, menu_pick_mode)

		if team_color_menu_open and team_color_menu_rect is not None:
			current_color = (255, 190, 0) if team_color_menu_team == "left" else (30, 120, 255)
			for player in players:
				if player.team == team_color_menu_team:
					current_color = player.color
					break
			draw_team_color_menu(
				screen,
				font,
				team_color_menu_rect,
				team_color_menu_team,
				team_color_menu_hover_idx,
				current_color,
			)

		if capture_notice_frames > 0 and capture_notice_text:
			notice_surface = pygame.Surface((WINDOW_SIZE[0], 42), pygame.SRCALPHA)
			notice_surface.fill((10, 10, 10, 165))
			notice_font = pygame.font.SysFont("arial", 18, bold=True)
			text_surface = notice_font.render(capture_notice_text, True, (255, 255, 255))
			notice_surface.blit(text_surface, text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, 21)))
			screen.blit(notice_surface, (0, WINDOW_SIZE[1] - 56))
			capture_notice_frames -= 1

		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()


if __name__ == "__main__":
	main()
