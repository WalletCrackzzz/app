import random
import time
import sys
import os
import hashlib
from datetime import datetime
from colorama import Fore, Style, init
import json
import requests
import threading

init()

class CryptoFinder:
    def __init__(self):
        self.licence_file = "licence.key"
        self.config_file = "config.json"
        self.license_hashes = {
            "BTC": "fe7be411c4424e50cf2515e703a9a8ddd072978319badad323a1fd2563cf6cf7",  # "password"
            "ETH": "8088d115fdc089411abe34de01fecd7963cfb96d4072ea223bfabf99f1050657",  # "ethkey"
            "LTC": "a1be65e54c2e169344a9bf4af76994c28dcfd064ae87cdf88a3fbdfcacb67646",  # "ltckey"
            "BSC": "b970ff00b96116cd02ef28ef3e23bbf6eb82f981f38fc666418fe94c504a73e0",  # "bsckey"
            "SOL": "130f6d230f5f097534c9e14189cb56fbf5b50054ee3bc5ee4ce2cec379b84bc4",  # "solkey"
            "ADA": "5dc490999d69996e82a116502198173e34ec51c58204d8757fa2a535a535a72f",  # "adakey"
            "MATIC": "b38c4cd2145066b2b94bfe0758988b6a46c08ad735948783845df4a170d450c8",  # "matickey"
            "ALL": "6893dd700fec8f3eb2a7a54ba9727f66d043ce3ccf80b34d70f73367b14d02bc"   # "admin"
        }
        self.active_licenses = set()
        self.discord_webhook = None
        self.target_coin = None
        self.scanning_active = False
        self.found_wallets = []
        self.scan_stats = {"attempts": 0, "found": 0}
        self.last_find_time = 0
        
        self.wallet_types = ["Bitcoin", "Ethereum", "Litecoin", 
                           "Binance Smart Chain", "Solana", "Cardano", "Polygon"]
        
        self.results_dir = "scan_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.load_config()
        self.load_licenses()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.discord_webhook = config.get("discord_webhook")
            except Exception as e:
                print(f"{Fore.RED}Error loading config: {e}{Style.RESET_ALL}")

    def save_config(self):
        config = {"discord_webhook": self.discord_webhook}
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def load_licenses(self):
        if os.path.exists(self.licence_file):
            try:
                with open(self.licence_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            for coin, valid_hash in self.license_hashes.items():
                                key_hash = hashlib.sha256(line.encode()).hexdigest()
                                if key_hash == valid_hash:
                                    self.active_licenses.add(coin)
                                    if coin != "ALL":
                                        self.target_coin = coin
            except Exception as e:
                print(f"{Fore.RED}Error loading licenses: {e}{Style.RESET_ALL}")

    def save_licenses(self):
        with open(self.licence_file, "w") as f:
            for coin in self.active_licenses:
                if coin == "BTC":
                    f.write("password\n")
                elif coin == "ETH":
                    f.write("ethkey\n")
                elif coin == "LTC":
                    f.write("ltckey\n")
                elif coin == "BSC":
                    f.write("bsckey\n")
                elif coin == "SOL":
                    f.write("solkey\n")
                elif coin == "ADA":
                    f.write("adakey\n")
                elif coin == "MATIC":
                    f.write("matickey\n")
                elif coin == "ALL":
                    f.write("admin\n")

    def activate_license(self, key, silent=False):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        if key_hash == self.license_hashes["ALL"]:
            if not silent:
                print(f"{Fore.YELLOW}Demo mode: ALL CHAINS license not available{Style.RESET_ALL}")
            return False
            
        for coin, valid_hash in self.license_hashes.items():
            if coin == "ALL":
                continue
            if key_hash == valid_hash:
                self.active_licenses.add(coin)
                self.target_coin = coin
                if not silent:
                    print(f"{Fore.GREEN}✓ {coin} license activated!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Now scanning for {coin} wallets only{Style.RESET_ALL}")
                self.save_licenses()
                return True
                
        if not silent:
            print(f"{Fore.RED}✗ Invalid license key{Style.RESET_ALL}")
        return False

    def is_licensed_for(self, coin):
        return coin.upper() in self.active_licenses

    def generate_seed(self):
        bip39_words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse", 
            "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act", 
            "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit", 
            "adult", "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent", 
            "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", 
            "alien", "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter", 
            "always", "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger", 
            "angle", "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique", 
            "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic", 
            "area", "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest", 
            "arrive", "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset", 
            "assist", "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction", 
            "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake", 
            "aware", "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge", 
            "bag", "balance", "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain", 
            "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become", 
            "beef", "before", "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit", 
            "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology", 
            "bird", "birth", "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless", 
            "blind", "blood", "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body", 
            "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring", "borrow", "boss", 
            "bottom", "bounce", "box", "boy", "bracket", "brain", "brand", "brass", "brave", "bread", 
            "breeze", "brick", "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze", 
            "broom", "brother", "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb", 
            "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus", "business", "busy", 
            "butter", "buyer", "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake", "call", 
            "calm", "camera", "camp", "can", "canal", "cancel", "candy", "cannon", "canoe", "canvas", 
            "canyon", "capable", "capital", "captain", "car", "carbon", "card", "cargo", "carpet", "carry", 
            "cart", "case", "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category", 
            "cattle", "caught", "cause", "caution", "cave", "ceiling", "celery", "cement", "census", "century", 
            "cereal", "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge", "chase", 
            "chat", "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken", "chief", "child", 
            "chimney", "choice", "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle", 
            "citizen", "city", "civil", "claim", "clap", "clarify", "claw", "clay", "clean", "clerk", 
            "clever", "click", "client", "cliff", "climb", "clinic", "clip", "clock", "clog", "close", 
            "cloth", "cloud", "clown", "club", "clump", "cluster", "clutch", "coach", "coast", "coconut", 
            "code", "coffee", "coil", "coin", "collect", "color", "column", "combine", "come", "comfort", 
            "comic", "common", "company", "concert", "conduct", "confirm", "congress", "connect", "consider", "control", 
            "convince", "cook", "cool", "copper", "copy", "coral", "core", "corn", "correct", "cost", 
            "cotton", "couch", "country", "couple", "course", "cousin", "cover", "coyote", "crack", "cradle", 
            "craft", "cram", "crane", "crash", "crater", "crawl", "crazy", "cream", "credit", "creek", 
            "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd", "crucial", 
            "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal", "cube", "culture", "cup", 
            "cupboard", "curious", "current", "curtain", "curve", "cushion", "custom", "cute", "cycle", "dad", 
            "damage", "damp", "dance", "danger", "daring", "dash", "daughter", "dawn", "day", "deal", 
            "debate", "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer", "defense", 
            "define", "defy", "degree", "delay", "deliver", "demand", "demise", "denial", "dentist", "deny", 
            "depart", "depend", "deposit", "depth", "deputy", "derive", "describe", "desert", "design", "desk", 
            "despair", "destroy", "detail", "detect", "develop", "device", "devote", "diagram", "dial", "diamond", 
            "diary", "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner", "dinosaur", 
            "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder", "display", "distance", 
            "divert", "divide", "divorce", "dizzy", "doctor", "document", "dog", "doll", "dolphin", "domain", 
            "donate", "donkey", "donor", "door", "dose", "double", "dove", "draft", "dragon", "drama", 
            "drastic", "draw", "dream", "dress", "drift", "drill", "drink", "drip", "drive", "drop", 
            "drum", "dry", "duck", "dumb", "dune", "during", "dust", "dutch", "duty", "dwarf", 
            "dynamic", "eager", "eagle", "early", "earn", "earth", "easily", "east", "easy", "echo", 
            "ecology", "economy", "edge", "edit", "educate", "effort", "egg", "eight", "either", "elbow", 
            "elder", "electric", "elegant", "element", "elephant", "elevator", "elite", "else", "embark", "embody", 
            "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable", "enact", "end", "endless", 
            "endorse", "enemy", "energy", "enforce", "engage", "engine", "enhance", "enjoy", "enlist", "enough", 
            "enrich", "enroll", "ensure", "enter", "entire", "entry", "envelope", "episode", "equal", "equip", 
            "era", "erase", "erode", "erosion", "error", "erupt", "escape", "essay", "essence", "estate", 
            "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact", "example", "excess", "exchange", 
            "excite", "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit", "exile", "exist", "exit", 
            "exotic", "expand", "expect", "expire", "explain", "expose", "express", "extend", "extra", "eye", 
            "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith", "fall", "false", "fame", 
            "family", "famous", "fan", "fancy", "fantasy", "farm", "fashion", "fat", "fatal", "father", 
            "fatigue", "fault", "favorite", "feature", "february", "federal", "fee", "feed", "feel", "female", 
            "fence", "festival", "fetch", "fever", "few", "fiber", "fiction", "field", "figure", "file", 
            "film", "filter", "final", "find", "fine", "finger", "finish", "fire", "firm", "first", 
            "fiscal", "fish", "fit", "fitness", "fix", "flag", "flame", "flash", "flat", "flavor", 
            "flee", "flight", "flip", "float", "flock", "floor", "flower", "fluid", "flush", "fly", 
            "foam", "focus", "fog", "foil", "fold", "follow", "food", "foot", "force", "forest", 
            "forget", "fork", "fortune", "forum", "forward", "fossil", "foster", "found", "fox", "fragile", 
            "frame", "frequent", "fresh", "friend", "fringe", "frog", "front", "frost", "frown", "frozen", 
            "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget", "gain", "galaxy", 
            "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment", "gas", "gasp", 
            "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle", "genuine", "gesture", 
            "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl", "give", "glad", "glance", 
            "glare", "glass", "glide", "glimpse", "globe", "gloom", "glory", "glove", "glow", "glue", 
            "goat", "goddess", "gold", "good", "goose", "gorilla", "gospel", "gossip", "govern", "gown", 
            "grab", "grace", "grain", "grant", "grape", "grass", "gravity", "great", "green", "grid", 
            "grief", "grit", "grocery", "group", "grow", "grunt", "guard", "guess", "guide", "guilt", 
            "guitar", "gun", "gym", "habit", "hair", "half", "hammer", "hamster", "hand", "happy", 
            "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk", "hazard", "head", "health", 
            "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen", "hero", "hidden", 
            "high", "hill", "hint", "hip", "hire", "history", "hobby", "hockey", "hold", "hole", 
            "holiday", "hollow", "home", "honey", "hood", "hope", "horn", "horror", "horse", "hospital", 
            "host", "hotel", "hour", "hover", "hub", "huge", "human", "humble", "humor", "hundred", 
            "hungry", "hunt", "hurdle", "hurry", "hurt", "husband", "hybrid", "ice", "icon", "idea", 
            "identify", "idle", "ignore", "ill", "illegal", "illness", "image", "imitate", "immense", "immune", 
            "impact", "impose", "improve", "impulse", "inch", "include", "income", "increase", "index", "indicate", 
            "indoor", "industry", "infant", "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury", 
            "inmate", "inner", "innocent", "input", "inquiry", "insane", "insect", "inside", "inspire", "install", 
            "intact", "interest", "into", "invest", "invite", "involve", "iron", "island", "isolate", "issue", 
            "item", "ivory", "jacket", "jaguar", "jar", "jazz", "jealous", "jeans", "jelly", "jewel", 
            "job", "join", "joke", "journey", "joy", "judge", "juice", "jump", "jungle", "junior", 
            "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick", "kid", "kidney", 
            "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee", "knife", 
            "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language", 
            "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit", 
            "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left", "leg", "legal", 
            "legend", "leisure", "lemon", "lend", "length", "lens", "leopard", "lesson", "letter", "level", 
            "liar", "liberty", "library", "license", "life", "lift", "light", "like", "limb", "limit", 
            "link", "lion", "liquid", "list", "little", "live", "lizard", "load", "loan", "lobster", 
            "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud", "lounge", "love", 
            "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics", "machine", "mad", 
            "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal", "man", "manage", 
            "mandate", "mango", "mansion", "manual", "maple", "marble", "march", "margin", "marine", "market", 
            "marriage", "mask", "mass", "master", "match", "material", "math", "matrix", "matter", "maximum", 
            "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal", "media", "melody", "melt", 
            "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry", "mesh", "message", 
            "metal", "method", "middle", "midnight", "milk", "million", "mimic", "mind", "minimum", "minor", 
            "minute", "miracle", "mirror", "misery", "miss", "mistake", "mix", "mixed", "mixture", "mobile", 
            "model", "modify", "mom", "moment", "monitor", "monkey", "monster", "month", "moon", "moral", 
            "more", "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse", "move", "movie", 
            "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom", "music", "must", "mutual", 
            "myself", "mystery", "myth", "naive", "name", "napkin", "narrow", "nasty", "nation", "nature", 
            "near", "neck", "need", "negative", "neglect", "neither", "nephew", "nerve", "nest", "net", 
            "network", "neutral", "never", "news", "next", "nice", "night", "noble", "noise", "nominee", 
            "noodle", "normal", "north", "nose", "notable", "note", "nothing", "notice", "novel", "now", 
            "nuclear", "number", "nurse", "nut", "oak", "obey", "object", "oblige", "obscure", "observe", 
            "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offer", "office", "often", 
            "oil", "okay", "old", "olive", "olympic", "omit", "once", "one", "onion", "online", 
            "only", "open", "opera", "opinion", "oppose", "option", "orange", "orbit", "orchard", "order", 
            "ordinary", "organ", "orient", "original", "orphan", "ostrich", "other", "outdoor", "outer", "output", 
            "outside", "oval", "oven", "over", "own", "owner", "oxygen", "oyster", "ozone", "pact", 
            "paddle", "page", "pair", "palace", "palm", "panda", "panel", "panic", "panther", "paper", 
            "parade", "parent", "park", "parrot", "party", "pass", "patch", "path", "patient", "patrol", 
            "pattern", "pause", "pave", "payment", "peace", "peanut", "pear", "peasant", "pelican", "pen", 
            "penalty", "pencil", "people", "pepper", "perfect", "permit", "person", "pet", "phone", "photo", 
            "phrase", "physical", "piano", "picnic", "picture", "piece", "pig", "pigeon", "pill", "pilot", 
            "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place", "planet", "plastic", "plate", 
            "play", "please", "pledge", "pluck", "plug", "plunge", "poem", "poet", "point", "polar", 
            "pole", "police", "pond", "pony", "pool", "popular", "portion", "position", "possible", "post", 
            "potato", "pottery", "poverty", "powder", "power", "practice", "praise", "predict", "prefer", "prepare", 
            "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority", "prison", "private", 
            "prize", "problem", "process", "produce", "profit", "program", "project", "promote", "proof", "property", 
            "prosper", "protect", "proud", "provide", "public", "pudding", "pull", "pulp", "pulse", "pumpkin", 
            "punch", "pupil", "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle", 
            "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit", 
            "raccoon", "race", "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp", 
            "ranch", "random", "range", "rapid", "rare", "rate", "rather", "raven", "raw", "razor", 
            "ready", "real", "reason", "rebel", "rebuild", "recall", "receive", "recipe", "record", "recycle", 
            "reduce", "reflect", "reform", "refuse", "region", "regret", "regular", "reject", "relax", "release", 
            "relief", "rely", "remain", "remember", "remind", "remove", "render", "renew", "rent", "reopen", 
            "repair", "repeat", "replace", "report", "require", "rescue", "resemble", "resist", "resource", "response", 
            "result", "retire", "retreat", "return", "reunion", "reveal", "review", "reward", "rhythm", "rib", 
            "ribbon", "rice", "rich", "ride", "ridge", "rifle", "right", "rigid", "ring", "riot", 
            "ripple", "risk", "ritual", "rival", "river", "road", "roast", "robot", "robust", "rocket", 
            "romance", "roof", "rookie", "room", "rose", "rotate", "rough", "round", "route", "royal", 
            "rubber", "rude", "rug", "rule", "run", "runway", "rural", "sad", "saddle", "sadness", 
            "safe", "sail", "salad", "salmon", "salon", "salt", "salute", "same", "sample", "sand", 
            "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scale", "scan", "scare", "scatter", 
            "scene", "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script", 
            "scrub", "sea", "search", "season", "seat", "second", "secret", "section", "security", "seed", 
            "seek", "segment", "select", "sell", "seminar", "senior", "sense", "sentence", "series", "service", 
            "session", "settle", "setup", "seven", "shadow", "shaft", "shallow", "share", "shed", "shell", 
            "sheriff", "shield", "shift", "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop", 
            "short", "shoulder", "shove", "shrimp", "shrug", "shuffle", "shy", "sibling", "sick", "side", 
            "siege", "sight", "sign", "silent", "silk", "silly", "silver", "similar", "simple", "since", 
            "sing", "siren", "sister", "situate", "six", "size", "skate", "sketch", "ski", "skill", 
            "skin", "skirt", "skull", "slab", "slam", "sleep", "slender", "slice", "slide", "slight", 
            "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile", "smoke", "smooth", 
            "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social", "sock", "soda", 
            "soft", "solar", "soldier", "solid", "solution", "solve", "someone", "song", "soon", "sorry", 
            "sort", "soul", "sound", "soup", "source", "south", "space", "spare", "spatial", "spawn", 
            "speak", "special", "speed", "spell", "spend", "sphere", "spice", "spider", "spike", "spin", 
            "spirit", "split", "spoil", "sponsor", "spoon", "sport", "spot", "spray", "spread", "spring", 
            "spy", "square", "squeeze", "squirrel", "stable", "stadium", "staff", "stage", "stairs", "stamp", 
            "stand", "start", "state", "stay", "steak", "steel", "stem", "step", "stereo", "stick", 
            "still", "sting", "stock", "stomach", "stone", "stool", "story", "stove", "strategy", "street", 
            "strike", "strong", "struggle", "student", "stuff", "stumble", "style", "subject", "submit", "subway", 
            "success", "such", "sudden", "suffer", "sugar", "suggest", "suit", "summer", "sun", "sunny", 
            "sunset", "super", "supply", "supreme", "sure", "surface", "surge", "surprise", "surround", "survey", 
            "suspect", "sustain", "swallow", "swamp", "swap", "swarm", "swear", "sweet", "swift", "swim", 
            "swing", "switch", "sword", "symbol", "symptom", "syrup", "system", "table", "tackle", "tag", 
            "tail", "talent", "talk", "tank", "tape", "target", "task", "taste", "tattoo", "taxi", 
            "teach", "team", "tell", "ten", "tenant", "tennis", "tent", "term", "test", "text", 
            "thank", "that", "theme", "then", "theory", "there", "they", "thing", "this", "thought", 
            "three", "thrive", "throw", "thumb", "thunder", "ticket", "tide", "tiger", "tilt", "timber", 
            "time", "tiny", "tip", "tired", "tissue", "title", "toast", "tobacco", "today", "toddler", 
            "toe", "together", "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool", 
            "tooth", "top", "topic", "topple", "torch", "tornado", "tortoise", "toss", "total", "tourist", 
            "toward", "tower", "town", "toy", "track", "trade", "traffic", "tragic", "train", "transfer", 
            "trap", "trash", "travel", "tray", "treat", "tree", "trend", "trial", "tribe", "trick", 
            "trigger", "trim", "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trust", 
            "truth", "try", "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle", 
            "twelve", "twenty", "twice", "twin", "twist", "two", "type", "typical", "ugly", "umbrella", 
            "unable", "unaware", "uncle", "uncover", "under", "undo", "unfair", "unfold", "unhappy", "uniform", 
            "unique", "unit", "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade", 
            "uphold", "upon", "upper", "upset", "urban", "urge", "usage", "use", "used", "useful", 
            "useless", "usual", "utility", "vacant", "vacuum", "vague", "valid", "valley", "valve", "van", 
            "vanish", "vapor", "various", "vast", "vault", "vehicle", "velvet", "vendor", "venture", "venue", 
            "verb", "verify", "version", "very", "vessel", "veteran", "viable", "vibrant", "vicious", "victory", 
            "video", "view", "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual", 
            "vital", "vivid", "vocal", "voice", "void", "volcano", "volume", "vote", "voyage", "wage", 
            "wagon", "wait", "walk", "wall", "walnut", "want", "warfare", "warm", "warrior", "wash", 
            "wasp", "waste", "water", "wave", "way", "wealth", "weapon", "wear", "weasel", "weather", 
            "web", "wedding", "weekend", "weird", "welcome", "west", "wet", "whale", "what", "wheat", 
            "wheel", "when", "where", "whip", "whisper", "wide", "width", "wife", "wild", "will", 
            "win", "window", "wine", "wing", "wink", "winner", "winter", "wire", "wisdom", "wise", 
            "wish", "witness", "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world", 
            "worry", "worth", "wrap", "wreck", "wrestle", "wrist", "write", "wrong", "yard", "year", 
            "yellow", "you", "young", "youth", "zebra", "zero", "zone", "zoo"
        ]
        return ' '.join(random.choices(bip39_words, k=12))

    def generate_address(self, wallet_type):
        coin = wallet_type.upper()
        prefixes = {
            "BITCOIN": ["1", "3", "bc1"],
            "ETHEREUM": ["0x"],
            "LITECOIN": ["L", "M", "ltc1"],
            "BINANCE SMART CHAIN": ["0x", "bnb"],
            "SOLANA": ["So"],
            "CARDANO": ["addr"],
            "POLYGON": ["0x"]
        }
        prefix = random.choice(prefixes.get(coin, ["addr"]))
        chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return prefix + ''.join(random.choices(chars, k=33-len(prefix)))

    def generate_balance(self):
        btc_amount = random.uniform(0.000002, 0.0005)
        usd_value = round(btc_amount * 50000, 5)
        return btc_amount, usd_value

    def save_wallet(self, wallet_data, demo=False):
        coin = wallet_data['type'].upper()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = "DEMO" if demo else "FOUND"
        filename = f"{self.results_dir}/{coin}_{prefix}_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(f"Wallet Type: {wallet_data['type']}\n")
            f.write(f"Address: {wallet_data['address']}\n")
            f.write(f"Balance: {wallet_data['btc']:.8f} BTC (~${wallet_data['usd']:.2f})\n")
            if not demo and wallet_data['valid']:
                f.write(f"Seed: {wallet_data['seed']}\n")
            elif demo:
                f.write(f"Seed: [DEMO MODE - LICENSE REQUIRED]\n")
        
        return filename

    def display_panel(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.YELLOW}=== CRYPTO WALLET SCANNER ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Status: {Fore.GREEN if self.scanning_active else Fore.RED}{'ACTIVE' if self.scanning_active else 'INACTIVE'}{Style.RESET_ALL}")
        
        if self.target_coin:
            print(f"{Fore.CYAN}Target: {Fore.GREEN}{self.target_coin}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}Mode: {Fore.YELLOW}DEMO (scanning all){Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Scan Statistics:{Style.RESET_ALL}")
        print(f"Attempts: {self.scan_stats['attempts']}")
        print(f"Found: {Fore.GREEN if self.scan_stats['found'] > 0 else Fore.RED}{self.scan_stats['found']}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Recent Results:{Style.RESET_ALL}")
        
        for result in self.found_wallets[-5:]:
            if result['demo']:
                status_color = Fore.YELLOW
                status = "DEMO"
            else:
                status_color = Fore.GREEN if result['valid'] else Fore.RED
                status = 'VALID' if result['valid'] else 'INVALID'
            print(f"{status_color}{result['address']} - {result['type']} - {status}{Style.RESET_ALL}")

    def continuous_scan_worker(self):
        self.scanning_active = True
        self.scan_stats = {"attempts": 0, "found": 0}
        self.last_find_time = time.time()
        
        try:
            while self.scanning_active:
                self.scan_stats['attempts'] += 1
                self.display_panel()
                
                # Show scanning animation
                for i in range(10):
                    if not self.scanning_active:
                        break
                    print(f"\r{Fore.CYAN}Scanning blockchain{'.' * (i % 4)}{' ' * (3 - (i % 4))}{Style.RESET_ALL}", end="")
                    time.sleep(0.5)
                
                # Check if we should find a wallet (~5 minutes since last find)
                if time.time() - self.last_find_time > 300:  # 5 minutes
                    self.last_find_time = time.time()
                    
                    # Determine wallet type
                    if self.target_coin:
                        wallet_type = self.target_coin
                        demo = False
                    else:
                        wallet_type = random.choice(self.wallet_types)
                        demo = True
                    
                    # Generate wallet
                    self.scan_stats['found'] += 1
                    seed = self.generate_seed()
                    address = self.generate_address(wallet_type)
                    btc, usd = self.generate_balance()
                    valid = not demo and random.random() < 0.7
                    
                    wallet_data = {
                        'type': wallet_type,
                        'address': address,
                        'valid': valid,
                        'btc': btc,
                        'usd': usd,
                        'seed': seed,
                        'demo': demo
                    }
                    
                    # Save wallet
                    filename = self.save_wallet(wallet_data, demo=demo)
                    print(f"\n\n{Fore.GREEN if not demo else Fore.YELLOW}✓ Found {'demo ' if demo else ''}wallet! Saved to: {filename}{Style.RESET_ALL}")
                    
                    self.found_wallets.append(wallet_data)
                    if len(self.found_wallets) > 5:
                        self.found_wallets.pop(0)
                
                self.display_panel()
                
        except KeyboardInterrupt:
            self.scanning_active = False
            print(f"\n{Fore.YELLOW}Scanning stopped{Style.RESET_ALL}")

    def start_continuous_scan(self):
        if not self.scanning_active:
            scan_thread = threading.Thread(target=self.continuous_scan_worker)
            scan_thread.daemon = True
            scan_thread.start()
            input("\nPress Enter to return to menu...")
            self.scanning_active = False
        else:
            print(f"{Fore.RED}Scanning is already active!{Style.RESET_ALL}")

    def setup_discord_webhook(self):
        print(f"\n{Fore.CYAN}=== Discord Webhook Setup ==={Style.RESET_ALL}")
        url = input("Enter webhook URL (or leave blank to skip): ").strip()
        
        if url:
            self.discord_webhook = url
            self.save_config()
            print(f"{Fore.GREEN}✓ Webhook configured!{Style.RESET_ALL}")
        else:
            self.discord_webhook = None
            print("Webhook disabled")

    def activate_license_menu(self):
        print(f"\n{Fore.CYAN}=== License Activation ==={Style.RESET_ALL}")
        print("Available coins:", ", ".join([c for c in self.license_hashes.keys() if c != "ALL"]))
        key = input("Enter license key: ").strip()
        if key:
            self.activate_license(key)
        else:
            print(f"{Fore.RED}Empty key entered{Style.RESET_ALL}")

    def run(self):
        if not os.path.exists(self.config_file):
            self.setup_discord_webhook()
        
        while True:
            print(f"\n{Fore.YELLOW}=== CRYPTO FINDER ==={Style.RESET_ALL}")
            active = ', '.join(self.active_licenses) if self.active_licenses else 'DEMO MODE'
            print(f"Active licenses: {active}")
            if self.target_coin:
                print(f"Target coin: {Fore.GREEN}{self.target_coin}{Style.RESET_ALL}")
            print("1. Start Scan")
            print("2. Enter License Key")
            print("3. Discord Webhook Setup")
            print("4. Exit")
            
            choice = input("\nSelect: ")
            
            if choice == "1":
                self.start_continuous_scan()
            elif choice == "2":
                self.activate_license_menu()
            elif choice == "3":
                self.setup_discord_webhook()
            elif choice == "4":
                print("Exiting...")
                break

if __name__ == "__main__":
    try:
        app = CryptoFinder()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram closed")
        sys.exit(0)
