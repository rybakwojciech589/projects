"""
===============================================
 KRONIKI POLBOGOW / DEMIGOD CHRONICLES RPG
 Engine: Python 3.10+ / google-genai
===============================================

Run:
    pip install google-genai colorama
    set GEMINI_API_KEY=your_key        (Windows)
    export GEMINI_API_KEY=your_key     (Linux/Mac)
    python rpg_engine.py
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field

try:
    from colorama import init, Fore, Style

    init(autoreset=True)
except ImportError:
    class Fore:
        RED = YELLOW = GREEN = CYAN = MAGENTA = WHITE = BLUE = ""
        LIGHTBLACK_EX = LIGHTCYAN_EX = LIGHTYELLOW_EX = LIGHTGREEN_EX = ""

    class Style:
        BRIGHT = RESET_ALL = DIM = ""


GEMINI_MODEL = "gemini-2.5-flash"
API_KEY = os.getenv("GEMINI_API_KEY", "")
MAX_RETRIES = 3
DEFAULT_MAX_TOKENS = 2048
INTRO_MAX_TOKENS = 3000


SYSTEM_INSTRUCTION_PL = """
Jestes Mistrzem Gry prowadzacym przygode RPG osadzona w swiecie Percy'ego Jacksona
autorstwa Ricka Riordana. Prowadz historie po polsku. Twoj styl jest przygodowy,
lekko humorystyczny, ale prawdziwe zagrozenie musi byc odczuwalne.

## SWIAT I ZASADY
- Bogowie greccy sa realni i aktywni we wspolczesnym Nowym Jorku
- Polbogowie maja ADHD i dysleksje jako efekt uboczny boskiej krwi
- Mgla sprawia, ze smiertelni nie widza potworow ani magii
- Potwory czuja zapach polbogow i ich szukaja
- Celestial bronze rani potwory, zwykla stal nie dziala
- Camp Half-Blood na Long Island to jedyne bezpieczne miejsce
- Satyry sa opiekunami przydzielanymi polbogom i zwykle udaja ludzi

## BOSKIE POCHODZENIE GRACZA
Na poczatku gry losowo wybierz jednego ojca z tej listy i zapamietaj go w notatce:
Zeus, Posejdon, Hades, Ares, Apollo, Hefajstos, Hermes.
Trzymaj wybor w tajemnicy az do dotarcia do obozu. Dawaj tylko subtelne wskazowki:
- Zeus: dreszcz przy burzach, elektryzujace sie wlosy
- Posejdon: spokoj przy wodzie, woda nie robi mu krzywdy
- Hades: widzi duchy, dobrze czuje sie w ciemnosci
- Ares: instynkt walki, adrenalina, trudno go przestraszyc
- Apollo: talent do luku i muzyki, czasem mowi poetycko
- Hefajstos: intuicyjnie rozumie maszyny i naprawy
- Hermes: szybki refleks, przekonywanie, kradziez, spryt
Ujawnij pochodzenie dopiero w obozie.

## STRUKTURA HISTORII

### AKT 1 - ZWYKLE ZYCIE
- Gracz jest nastolatkiem w Nowym Jorku
- Pokaz jego klopoty w szkole, ADHD, dysleksje i dziwne wypadki
- Wprowadz Grovera jako najlepszego przyjaciela
- Buduj narastajace dziwne zdarzenia i sledzenie
- Zakoncz akt publicznym atakiem potwora

### AKT 2 - ODKRYCIE
- Grover ujawnia, ze jest satyrem i ze gracz jest polbogiem
- Tlumaczy bogow, oboz i niebezpieczenstwo
- Daj graczowi chwile na reakcje
- Ruszaja razem do obozu na Long Island

### AKT 3 - DROGA DO OBOZU
- Minimum 2-3 spotkania z potworami lub przeszkodami
- Grover uzywa fletni Pana, komunikuje sie ze zwierzetami, je puszki ze stresu
- Gracz odkrywa pierwsze subtelne moce
- Mozliwe spotkania: Harpia, Minotaur, Furia, Empousa, psy z Tartaru

### AKT 4 - OBOZ HEROSOW
- Dramatyczne przekroczenie granicy na wzgorzu Thalii
- Pierwsze spojrzenie na oboz
- Spotkanie z Chironem
- Kulminacja: boski znak ujawnia rodzica
- Gracz trafia do odpowiedniej chaty

## WAZNE POSTACIE
- Grover Underwood: satyr, najlepszy przyjaciel, nerwowy ale lojalny, je puszki, bardzo dba o gracza
- Chiron: centaur i trener, przed obozem udaje nauczyciela historii
- Rodzic gracza: nie pojawia sie fizycznie, ale jego wplyw jest wyczuwalny

## STYL
- Zwracaj sie do gracza per Ty, narracja w czasie terazniejszym
- Dodawaj humor sytuacyjny, ale nie rozbijaj stawki
- Nawiazuj do Nowego Jorku: metro, Central Park, mosty, hot-dogi, tlum
- Dawaj graczowi wybor i nie prowadz go za reke
- W zwyklych turach odpowiedzi maja miec 3-5 zdan, byc zywe i angazujace
- Intro oraz restart historii sa wyjatkiem i maja miec 6-8 zdan

## FORMAT ODPOWIEDZI
Kazda odpowiedz MUSI zawierac separator i JSON na koncu:

[opis fabularny]
---JSON---
{"damage": 0, "heal": 0, "gold_change": 0, "xp_gain": 0, "status_effect": "", "note": ""}

## ZASADY JSON
- damage: utracone HP
- heal: odzyskane HP
- gold_change: zmiana drachm
- xp_gain: 0-50 punktow
- status_effect: np. poisoned, blinded albo pusty string
- note: prywatna notatka o fabule, tajnym rodzicu i planach potworow

## LIMITY OBRAZEN
- Zwykly potwor: 3-8 damage
- Silny potwor: 10-20 damage
- Jesli gracz ma wiecej niz 15 HP, nie moze zginac od jednego ciosu

Pamietaj: zawsze zakoncz odpowiedz separatorem ---JSON--- i obiektem JSON.
"""


SYSTEM_INSTRUCTION_EN = """
You are the Game Master of an RPG adventure set in the world of Percy Jackson
by Rick Riordan. Run the story in English. Your style is adventurous, witty,
and lively, but real danger must always feel present.

## WORLD AND RULES
- Greek gods are real and active in modern New York City
- Demigods often have ADHD and dyslexia as side effects of divine blood
- The Mist hides monsters and magic from mortals
- Monsters can smell demigods and hunt them
- Celestial bronze hurts monsters, ordinary steel does not
- Camp Half-Blood on Long Island is the only truly safe place
- Satyrs are protectors assigned to demigods and often pretend to be human

## PLAYER'S DIVINE PARENT
At the start of the game, secretly choose one father from this list and keep it in your note:
Zeus, Poseidon, Hades, Ares, Apollo, Hephaestus, Hermes.
Keep the choice secret until the player reaches camp. Only give subtle hints:
- Zeus: static in storms, hair rising near lightning
- Poseidon: calm near water, water seems friendly
- Hades: sees ghosts, feels at ease in darkness
- Ares: battle instinct, adrenaline, hard to scare
- Apollo: talent for archery and music, sometimes sounds poetic
- Hephaestus: instinctively understands machines and repairs
- Hermes: quick reflexes, persuasion, lying, stealing, speed
Reveal the parent only at camp.

## STORY STRUCTURE

### ACT 1 - ORDINARY LIFE
- The player is a teenager in New York City
- Show school trouble, ADHD, dyslexia, strange accidents
- Introduce Grover as the best friend
- Build strange events and a sense of being watched
- End the act with a public monster attack

### ACT 2 - DISCOVERY
- Grover reveals he is a satyr and the player is a demigod
- He explains the gods, the camp, and the danger
- Give the player room to react
- They head toward Camp Half-Blood

### ACT 3 - THE ROAD TO CAMP
- Include at least 2-3 monster encounters or obstacles
- Grover uses pan pipes, talks to animals, and stress-eats cans
- The player starts discovering subtle powers
- Possible enemies: Harpy, Minotaur, Fury, Empousa, hellhound

### ACT 4 - CAMP HALF-BLOOD
- Dramatic crossing of Thalia's hill
- First look at the camp
- Meeting with Chiron
- Climax: a divine sign reveals the parent
- The player joins the proper cabin

## IMPORTANT CHARACTERS
- Grover Underwood: satyr, best friend, nervous but loyal, eats cans, deeply cares about the player
- Chiron: centaur trainer, previously disguised as a teacher
- The player's divine parent: never appears physically, but their influence is felt

## STYLE
- Address the player as "you", use present tense narration
- Use situational humor without lowering the stakes
- Reference modern New York details
- Give the player choices instead of railroading them
- Regular turns should be 3-5 vivid, engaging sentences
- The intro and story restart are exceptions and should be 6-8 sentences long

## RESPONSE FORMAT
Every response MUST include a separator and JSON at the end:

[story text]
---JSON---
{"damage": 0, "heal": 0, "gold_change": 0, "xp_gain": 0, "status_effect": "", "note": ""}

## JSON RULES
- damage: HP lost
- heal: HP gained
- gold_change: change in drachmas
- xp_gain: 0-50 points
- status_effect: for example poisoned, blinded, or empty string
- note: your private note about the story state, hidden parent, and monster plans

## DAMAGE LIMITS
- Normal monster: 3-8 damage
- Strong monster: 10-20 damage
- If the player has more than 15 HP, they must not die from a single hit

Remember: always end with ---JSON--- and a JSON object.
"""


LANGUAGE_PACKS = {
    "pl": {
        "label": "Polski",
        "system_instruction": SYSTEM_INSTRUCTION_PL,
        "header_title": "KRONIKI POLBOGOW",
        "header_subtitle": "Swiat Percy'ego Jacksona x Gemini AI",
        "choose_language": "Wybierz jezyk / Choose language:",
        "language_options": ["1. Polski", "2. English"],
        "missing_api_key": "[BLAD] Brak klucza GEMINI_API_KEY w zmiennych srodowiskowych!",
        "missing_api_help": "Ustaw go: export GEMINI_API_KEY='twoj_klucz_api' lub set GEMINI_API_KEY=twoj_klucz_api",
        "api_key_site": "Klucz uzyskasz na: https://aistudio.google.com/app/apikey",
        "missing_library": "[BLAD] Brak biblioteki google-genai!",
        "missing_library_help": "Zainstaluj: pip install google-genai",
        "hero_name_prompt": "Jak ma na imie twoj bohater? ",
        "default_name": "Nieznajomy",
        "inventory_empty": "brak",
        "header_status": "Lvl",
        "status_label": "Efekt",
        "gold_label": "Drachmy",
        "inventory_label": "Ekwipunek",
        "gm_building": "[Mistrz Gry buduje swiat...]",
        "gm_thinking": "[Mistrz Gry rozwaza konsekwencje...]",
        "intro_error": "[BLAD intro]",
        "api_error": "[BLAD API]",
        "mist_fallback": "Mgla Olimpu na chwile zaciera rzeczywistosc...",
        "goodbye_interrupt": "Do zobaczenia, herosie...",
        "goodbye_quit": "Olimp cie zapamieta. Do zobaczenia.",
        "unknown_command": "Nieznana komenda. Wpisz /pomoc.",
        "help_title": "KOMENDY SYSTEMOWE:",
        "help_lines": [
            "/status    - pokaz statystyki",
            "/inwentarz - pokaz ekwipunek",
            "/wyjscie   - zakoncz gre",
            "/pomoc     - ta lista",
            "Wszystko inne trafia do Mistrza Gry!",
        ],
        "damage_msg": "Otrzymales {amount} obrazen!",
        "heal_msg": "Uleczono {amount} HP!",
        "gold_msg": "Drachmy: {value}",
        "xp_msg": "Doswiadczenie: {value}",
        "levelup_msg": "AWANS NA POZIOM! Boska krew budzi sie w tobie!",
        "status_msg": "Efekt statusu: {value}",
        "death_title": "ZOSTALES POKONANY",
        "death_line": "{name} pada na ziemie. Olimp milczy.",
        "death_stats": "Poziom: {level} | Drachmy: {gold} | XP: {xp}",
        "play_again_prompt": "Zagrac ponownie? (t/n): ",
        "new_story": "[Nowa historia zaczyna sie...]",
        "olympus_remembers": "Olimp bedzie cie wspominal.",
        "state_template": "[STAN GRACZA: HP={hp}/{max_hp}, Drachmy={gold}, Poziom={level}, Efekt={effect}, Ekwipunek={inventory}]",
        "reminder": "PAMIETAJ: zakoncz odpowiedz separatorem ---JSON--- i obiektem JSON!",
        "rewrite_retry": (
            "Odpowiedz jeszcze raz od poczatku na te sama prosbe. "
            "Nie przepraszaj, nie komentuj zasad i nie wyjasniaj bledu. "
            "Napisz tylko scene fabularna i od razu zakoncz odpowiedz separatorem ---JSON--- oraz poprawnym obiektem JSON."
        ),
        "choice_retry": (
            "Na koncu sceny musisz postawic przed graczem konkretna decyzje i podac dokladnie trzy opcje "
            "oznaczone A), B), C). Nie koncz samego opisu bez wyboru."
        ),
        "invalid_response_error": "Model nie zwrocil poprawnej odpowiedzi po kilku probach.",
        "intro_prompt": (
            "Zacznij historie. Gracz to {name}, nastolatek w Nowym Jorku. "
            "Pokaz typowy poranek: klopoty, ADHD, moze jakis dziwny wypadek. "
            "Wprowadz Grovera jako przyjaciela. "
            "Napisz wciagajace otwarcie w stylu Ricka Riordana: humor, zywe detale NYC i poczucie, "
            "ze cos niezwyklego wisi w powietrzu. "
            "Utrzymaj odpowiedz zwarta: najlepiej okolo 6-8 zdan i mniej wiecej 120-180 slow. "
            "Nie wykorzystuj calego limitu wyjscia; calosc ma spokojnie zmiescic sie w mniej niz polowie dostepnego budzetu. "
            "Zakoncz natychmiast po postawieniu pierwszej decyzji dnia. "
            "Na koncu MUSISZ podac dokladnie trzy opcje wyboru gracza oznaczone A), B), C). "
            "Dopiero potem dodaj ---JSON--- oraz poprawny obiekt JSON."
        ),
        "restart_prompt": (
            "{name} otwiera oczy. Dostal druga szanse. Zacznij historie od nowa. "
            "Utrzymaj odpowiedz zwarta: najlepiej okolo 6-8 zdan i mniej wiecej 120-180 slow. "
            "Nie wykorzystuj calego limitu wyjscia; calosc ma spokojnie zmiescic sie w mniej niz polowie dostepnego budzetu. "
            "Zakoncz na pierwszej decyzji gracza. "
            "Na koncu MUSISZ podac dokladnie trzy opcje wyboru gracza oznaczone A), B), C). "
            "Dopiero potem dodaj ---JSON--- i poprawny obiekt JSON."
        ),
    },
    "en": {
        "label": "English",
        "system_instruction": SYSTEM_INSTRUCTION_EN,
        "header_title": "DEMIGOD CHRONICLES",
        "header_subtitle": "Percy Jackson world x Gemini AI",
        "choose_language": "Choose language / Wybierz jezyk:",
        "language_options": ["1. Polish", "2. English"],
        "missing_api_key": "[ERROR] GEMINI_API_KEY is missing from environment variables!",
        "missing_api_help": "Set it with: export GEMINI_API_KEY='your_api_key' or set GEMINI_API_KEY=your_api_key",
        "api_key_site": "Get your key at: https://aistudio.google.com/app/apikey",
        "missing_library": "[ERROR] Missing google-genai library!",
        "missing_library_help": "Install it with: pip install google-genai",
        "hero_name_prompt": "What is your hero's name? ",
        "default_name": "Stranger",
        "inventory_empty": "none",
        "header_status": "Lvl",
        "status_label": "Status",
        "gold_label": "Drachmas",
        "inventory_label": "Inventory",
        "gm_building": "[The Game Master is building the world...]",
        "gm_thinking": "[The Game Master weighs the consequences...]",
        "intro_error": "[INTRO ERROR]",
        "api_error": "[API ERROR]",
        "mist_fallback": "Olympian mist blurs reality for a moment...",
        "goodbye_interrupt": "See you later, hero...",
        "goodbye_quit": "Olympus will remember you. Farewell.",
        "unknown_command": "Unknown command. Type /help.",
        "help_title": "SYSTEM COMMANDS:",
        "help_lines": [
            "/status    - show stats",
            "/inventory - show inventory",
            "/quit      - end the game",
            "/help      - this list",
            "Everything else is sent to the Game Master!",
        ],
        "damage_msg": "You took {amount} damage!",
        "heal_msg": "Recovered {amount} HP!",
        "gold_msg": "Drachmas: {value}",
        "xp_msg": "Experience: {value}",
        "levelup_msg": "LEVEL UP! Divine blood awakens within you!",
        "status_msg": "Status effect: {value}",
        "death_title": "YOU HAVE FALLEN",
        "death_line": "{name} collapses to the ground. Olympus stays silent.",
        "death_stats": "Level: {level} | Drachmas: {gold} | XP: {xp}",
        "play_again_prompt": "Play again? (y/n): ",
        "new_story": "[A new story begins...]",
        "olympus_remembers": "Olympus will remember you.",
        "state_template": "[PLAYER STATE: HP={hp}/{max_hp}, Drachmas={gold}, Level={level}, Status={effect}, Inventory={inventory}]",
        "reminder": "REMEMBER: end every response with ---JSON--- and a JSON object!",
        "rewrite_retry": (
            "Answer the same request again from scratch. "
            "Do not apologize, do not comment on the rules, and do not explain the mistake. "
            "Write only the story scene and then end with ---JSON--- and a valid JSON object."
        ),
        "choice_retry": (
            "At the end of the scene you must present a concrete player decision and provide exactly three options "
            "labeled A), B), and C). Do not end with description alone."
        ),
        "invalid_response_error": "The model did not return a valid formatted response after several attempts.",
        "intro_prompt": (
            "Start the story. The player is {name}, a teenager in New York City. "
            "Show a typical morning: trouble, ADHD, maybe a strange accident. "
            "Introduce Grover as a friend. "
            "Write an engaging opening in the style of Rick Riordan: humor, vivid NYC detail, and the sense "
            "that something impossible is hanging in the air. "
            "Keep the reply compact: aim for about 6-8 sentences and roughly 120-180 words. "
            "Do not use the full output limit; the whole reply should fit comfortably within less than half of the available output budget. "
            "End immediately after the player's first decision of the day. "
            "You MUST provide exactly three player options labeled A), B), and C). "
            "Only then add ---JSON--- and a valid JSON object."
        ),
        "restart_prompt": (
            "{name} opens their eyes. They have been given a second chance. Start the story again. "
            "Keep the reply compact: aim for about 6-8 sentences and roughly 120-180 words. "
            "Do not use the full output limit; the whole reply should fit comfortably within less than half of the available output budget. "
            "End on the player's first decision. "
            "You MUST provide exactly three player options labeled A), B), and C). "
            "Only then add ---JSON--- and a valid JSON object."
        ),
    },
}


def choose_language():
    print()
    print("Choose language / Wybierz jezyk:")
    print("  1. Polski")
    print("  2. English")
    print()
    choice = input("> ").strip().lower()
    if choice in ("2", "en", "english"):
        return "en"
    return "pl"


@dataclass
class PlayerState:
    name: str = "Unknown"
    hp: int = 100
    max_hp: int = 100
    gold: int = 10
    xp: int = 0
    level: int = 1
    status_effect: str = ""
    inventory: list = field(default_factory=lambda: ["pocket knife", "backpack"])

    @property
    def xp_to_next(self) -> int:
        return self.level * 100

    def apply_effects(self, data: dict) -> list:
        messages = []

        if data.get("damage", 0) > 0:
            dmg = data["damage"]
            self.hp = max(0, self.hp - dmg)
            messages.append(f"damage:{dmg}")

        if data.get("heal", 0) > 0:
            heal = data["heal"]
            self.hp = min(self.max_hp, self.hp + heal)
            messages.append(f"heal:{heal}")

        if data.get("gold_change", 0) != 0:
            gc = data["gold_change"]
            self.gold = max(0, self.gold + gc)
            messages.append(f"gold:{gc:+d}")

        if data.get("xp_gain", 0) > 0:
            self.xp += data["xp_gain"]
            messages.append(f"xp:+{data['xp_gain']}")
            if self.xp >= self.xp_to_next:
                self.xp -= self.xp_to_next
                self.level += 1
                self.max_hp += 10
                self.hp = min(self.hp + 20, self.max_hp)
                messages.append("LEVELUP")

        if data.get("status_effect"):
            self.status_effect = data["status_effect"]
            messages.append(f"status:{self.status_effect}")

        return messages

    def is_dead(self) -> bool:
        return self.hp <= 0


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def hp_bar(current: int, maximum: int, width: int = 20) -> str:
    filled = int(width * current / maximum)
    empty = width - filled
    color = Fore.GREEN if current > maximum * 0.6 else (Fore.YELLOW if current > maximum * 0.3 else Fore.RED)
    bar = color + "#" * filled + Fore.LIGHTBLACK_EX + "-" * empty + Style.RESET_ALL
    return f"[{bar}] {current}/{maximum}"


def xp_bar(current: int, needed: int, width: int = 20) -> str:
    filled = int(width * current / needed) if needed > 0 else 0
    bar = Fore.CYAN + "=" * filled + Fore.LIGHTBLACK_EX + "-" * (width - filled) + Style.RESET_ALL
    return f"[{bar}] {current}/{needed}"


def print_header(texts: dict):
    print(
        Fore.YELLOW
        + Style.BRIGHT
        + "\n"
        + "=" * 46
        + "\n"
        + f"  {texts['header_title']}\n"
        + f"  {texts['header_subtitle']}\n"
        + "=" * 46
        + Style.RESET_ALL
    )


def print_stats(player: PlayerState, texts: dict):
    status_text = player.status_effect if player.status_effect else "-"
    inventory = ", ".join(player.inventory) if player.inventory else texts["inventory_empty"]

    print(Fore.LIGHTBLACK_EX + "-" * 54 + Style.RESET_ALL)
    print(
        f"  {Style.BRIGHT}{player.name}{Style.RESET_ALL}  "
        f"{Fore.YELLOW}{texts['header_status']} {player.level}{Style.RESET_ALL}  "
        f"{Fore.MAGENTA}{texts['status_label']}: {status_text}{Style.RESET_ALL}"
    )
    print(f"  HP   {hp_bar(player.hp, player.max_hp)}")
    print(f"  XP   {xp_bar(player.xp, player.xp_to_next)}")
    print(
        f"  {Fore.YELLOW}{texts['gold_label']}: {player.gold}{Style.RESET_ALL}   "
        f"{Fore.CYAN}{texts['inventory_label']}: {inventory}{Style.RESET_ALL}"
    )
    print(Fore.LIGHTBLACK_EX + "-" * 54 + Style.RESET_ALL)


def print_gm_response(text: str):
    print()
    print(text.strip())
    print()


def print_effect_messages(messages: list, texts: dict):
    for msg in messages:
        if msg.startswith("damage:"):
            amount = msg.split(":")[1]
            print(f"  {Fore.RED}{texts['damage_msg'].format(amount=amount)}{Style.RESET_ALL}")
        elif msg.startswith("heal:"):
            amount = msg.split(":")[1]
            print(f"  {Fore.GREEN}{texts['heal_msg'].format(amount=amount)}{Style.RESET_ALL}")
        elif msg.startswith("gold:"):
            value = msg.split(":")[1]
            print(f"  {Fore.YELLOW}{texts['gold_msg'].format(value=value)}{Style.RESET_ALL}")
        elif msg.startswith("xp:"):
            value = msg.split(":")[1]
            print(f"  {Fore.CYAN}{texts['xp_msg'].format(value=value)}{Style.RESET_ALL}")
        elif msg == "LEVELUP":
            print(f"\n  {Fore.YELLOW}{Style.BRIGHT}{texts['levelup_msg']}{Style.RESET_ALL}\n")
        elif msg.startswith("status:"):
            value = msg.split(":", 1)[1]
            print(f"  {Fore.MAGENTA}{texts['status_msg'].format(value=value)}{Style.RESET_ALL}")


def print_death_screen(player: PlayerState, texts: dict):
    print(Fore.RED + Style.BRIGHT)
    print("=" * 38)
    print(f"  {texts['death_title']}")
    print("=" * 38)
    print(texts["death_line"].format(name=player.name))
    print(texts["death_stats"].format(level=player.level, gold=player.gold, xp=player.xp))
    print(Style.RESET_ALL)


def print_help(texts: dict):
    print(Fore.CYAN)
    print(f"  {texts['help_title']}")
    for line in texts["help_lines"]:
        print(f"    {line}")
    print(Style.RESET_ALL)


def default_game_data() -> dict:
    return {
        "damage": 0,
        "heal": 0,
        "gold_change": 0,
        "xp_gain": 0,
        "status_effect": "",
        "note": "",
    }


def try_parse_gm_response(raw: str):
    separator = "---JSON---"

    if separator not in raw:
        return None

    story_text, json_part = raw.split(separator, 1)
    story_text = story_text.strip()
    json_part = json_part.strip()
    if not story_text:
        return None

    match = re.search(r"\{.*\}", json_part, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None

    return story_text, {**default_game_data(), **data}


def parse_gm_response(raw: str) -> tuple:
    parsed = try_parse_gm_response(raw)
    if parsed is not None:
        return parsed
    return raw.strip(), default_game_data()


def has_choice_block(text: str) -> bool:
    return all(re.search(rf"(?mi)^\s*{label}\)", text) for label in ("A", "B", "C"))


def build_context_prompt(player: PlayerState, action: str, texts: dict) -> str:
    inventory = ", ".join(player.inventory) if player.inventory else texts["inventory_empty"]
    effect = player.status_effect if player.status_effect else "-"
    state_info = texts["state_template"].format(
        hp=player.hp,
        max_hp=player.max_hp,
        gold=player.gold,
        level=player.level,
        effect=effect,
        inventory=inventory,
    )
    return state_info + "\n\n" + action + "\n\n" + texts["reminder"]


def create_chat(client, texts: dict, max_tokens: int = DEFAULT_MAX_TOKENS):
    from google.genai import types

    return client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=texts["system_instruction"],
            temperature=0.85,
            max_output_tokens=max_tokens,
        ),
    )


def send_structured_message(
    chat,
    prompt: str,
    texts: dict,
    max_output_tokens: int = DEFAULT_MAX_TOKENS,
    validator=None,
    validator_retry_text: str | None = None,
):
    from google.genai import types

    for _ in range(MAX_RETRIES):
        response = chat.send_message(
            prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_output_tokens),
        )
        raw_text = getattr(response, "text", "") or ""
        parsed = try_parse_gm_response(raw_text)

        if parsed is not None:
            story_text, game_data = parsed
            if validator is None or validator(story_text):
                return story_text, game_data

            if validator_retry_text:
                prompt = prompt + "\n\n" + validator_retry_text
                continue

        prompt = prompt + "\n\n" + texts["rewrite_retry"]

    raise ValueError(texts["invalid_response_error"])


def main():
    lang = choose_language()
    texts = LANGUAGE_PACKS[lang]

    if not API_KEY:
        print(Fore.RED + "\n" + texts["missing_api_key"])
        print("  " + texts["missing_api_help"])
        print("  " + texts["api_key_site"] + "\n" + Style.RESET_ALL)
        sys.exit(1)

    try:
        from google import genai

        client = genai.Client(api_key=API_KEY)
    except ImportError:
        print(Fore.RED + "\n" + texts["missing_library"])
        print("  " + texts["missing_library_help"] + "\n" + Style.RESET_ALL)
        sys.exit(1)

    cls()
    print_header(texts)
    print(Fore.WHITE + "\n  " + texts["hero_name_prompt"], end="")
    player_name = input().strip() or texts["default_name"]

    default_inventory = ["scyzoryk", "plecak"] if lang == "pl" else ["pocket knife", "backpack"]
    player = PlayerState(name=player_name, inventory=default_inventory.copy())

    cls()
    print_header(texts)
    print_stats(player, texts)
    print_help(texts)

    chat = create_chat(client, texts, DEFAULT_MAX_TOKENS)

    print(Fore.LIGHTBLACK_EX + "\n  " + texts["gm_building"] + "\n" + Style.RESET_ALL)

    intro_prompt = build_context_prompt(
        player,
        texts["intro_prompt"].format(name=player_name),
        texts,
    )

    try:
        story, _ = send_structured_message(
            chat,
            intro_prompt,
            texts,
            max_output_tokens=INTRO_MAX_TOKENS,
            validator=has_choice_block,
            validator_retry_text=texts["choice_retry"],
        )
        print_gm_response(story)
    except Exception as exc:
        print(Fore.RED + f"{texts['intro_error']} {exc}" + Style.RESET_ALL)

    while True:
        print()
        print(Fore.LIGHTYELLOW_EX + "  > " + Style.RESET_ALL, end="")

        try:
            action = input().strip()
        except (EOFError, KeyboardInterrupt):
            print(Fore.YELLOW + "\n\n  " + texts["goodbye_interrupt"] + Style.RESET_ALL)
            break

        if not action:
            continue

        if action.startswith("/"):
            cmd = action.lower()
            if cmd in ("/wyjscie", "/exit", "/quit"):
                print(Fore.YELLOW + "\n  " + texts["goodbye_quit"] + Style.RESET_ALL)
                break
            elif cmd in ("/status", "/stat"):
                print_stats(player, texts)
            elif cmd in ("/inwentarz", "/inventory", "/inv"):
                inventory = ", ".join(player.inventory) if player.inventory else texts["inventory_empty"]
                print(Fore.CYAN + f"\n  {texts['inventory_label']}: {inventory}" + Style.RESET_ALL)
            elif cmd in ("/pomoc", "/help"):
                print_help(texts)
            else:
                print(Fore.LIGHTBLACK_EX + "  " + texts["unknown_command"] + Style.RESET_ALL)
            continue

        print(Fore.LIGHTBLACK_EX + "  " + texts["gm_thinking"] + "\n" + Style.RESET_ALL)

        full_prompt = build_context_prompt(player, action, texts)
        story_text = ""
        game_data = default_game_data()

        try:
            story_text, game_data = send_structured_message(chat, full_prompt, texts)
        except Exception as exc:
            print(Fore.RED + f"  {texts['api_error']} {exc}" + Style.RESET_ALL)
            story_text = texts["mist_fallback"]
            game_data = default_game_data()

        if story_text:
            print_gm_response(story_text)

        if game_data:
            messages = player.apply_effects(game_data)
            if messages:
                print_effect_messages(messages, texts)

        if player.is_dead():
            print_death_screen(player, texts)
            print(Fore.WHITE + "  " + texts["play_again_prompt"], end="")
            again = input().strip().lower()
            if again in ("t", "tak", "y", "yes"):
                player = PlayerState(name=player_name, inventory=default_inventory.copy())
                chat = create_chat(client, texts, DEFAULT_MAX_TOKENS)
                cls()
                print_header(texts)
                print_stats(player, texts)
                print(Fore.LIGHTBLACK_EX + "\n  " + texts["new_story"] + "\n" + Style.RESET_ALL)
                try:
                    story, _ = send_structured_message(
                        chat,
                        build_context_prompt(player, texts["restart_prompt"].format(name=player_name), texts),
                        texts,
                        max_output_tokens=INTRO_MAX_TOKENS,
                        validator=has_choice_block,
                        validator_retry_text=texts["choice_retry"],
                    )
                    print_gm_response(story)
                except Exception as exc:
                    print(Fore.RED + f"{texts['api_error']} {exc}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "\n  " + texts["olympus_remembers"] + Style.RESET_ALL)
                break

        print_stats(player, texts)


if __name__ == "__main__":
    main()

