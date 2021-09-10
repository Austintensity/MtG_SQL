#  2021  Paul Austin
# Thanks to https://scryfall.com/docs/api
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mtg_main
import re

regex_searchmode = {
    'fullpatternsearch': "[aA]dd {[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]}({[wubrcgWUBRCG0123456789]\/[wubrcgWUBRCG0123456789]})*|[Aa]dd {[wubrcgWUBCRG0123456789]}({[wubrcgWUBRGC0123456789]})*|[Aa]dd .+mana",
    'hybridmanasearch': "[Aa]dd {[WUBRCGwubrcg0123456789]\/[WUBCRGwubrcg0123456789]}({[WUBCRGwubrcg0123456789]\/[WUBCRGwubrcg0123456789]})*",
    'plainmanasearch': "[Aa]dd {[WUBRGCwubrcg0123456789]}({[WUBRGCwubrcg0123456789]})*",
    'plainmanasearchmultiples': "[Aa]dd {[WUBRGCwubrcg0123456789]}({[WUBRGCwubrcg0123456789]})*, {[WUBRGCwubrcg0123456789]}({[WUBRGCwubrcg0123456789]})*, ({[WUBRGCwubrcg0123456789]}{[WUBRGCwubrcg0123456789]}, )*or {[WUBRGCwubrcg123456789]}({[WUBRGCwubrcg0123456789]})*",
    'wordmanasearch': "[Aa]dd .+mana",
    'keywordsearch': "'keywords': \[()?(.)*?\]",
    'imagesearch': "'image_uris': ?{.*?}",
    'normal_image_search': "'normal':.*?,",
    'activeabilitysearch': "({[01234567890TWURBGCwubrcg]}):|({[01234567890TWURBGCwubrcg]\/[01234567890TWURBGCwubrcg]})*({[01234567890TWURBGCwubrcg]})*,(.)*:|({[01234567890TWURBGCwubrcg]})*({[01234567890TWURBGCwubrcg]\/[01234567890TWURBGCwubrcg]})*({[01234567890TWURBGCwubrcg]})*,(.)*:",
    'gains_life_isolater': "gains? life equal to|gains? (.)*life",
    'all_life_gains': "gains? .*life (for each)?(equal to)?|gains? .*life[\. ,]",
    'all_damage_gains': "deals?t? damage (equal to)?|loses? .*life[\. ,]|deals?.*damage",
    'planeswalker_ability_index': ".*:",
    'planeswalker_boosts': "\+.*:",
    'planeswalker_costs': "\-.*:|0:",
    'etb_filter': "((return.* to)|enters?) the battlefield.*",
    'wipe_filter': "(destroy|exile|sacrifices*|shuffle|return|damage( to))( all( other)?| each( other)?|( the rest))",
    'target_filter': "(damaged?s?|flips?(ped)?|library?(ies)?|activate|move|put|distributes?|token|attach(ed)?s?|sacrificed?s?|destroy(ed)?s?|gets?|exiles?d?|return(ed)?s?|shuffles?|remove|(gains? control)|reveal|enchant|flip|discard|counter|(deal.*damage)|attack(ed)?s?|block(ed)?s?|fights?|(los.*life)|(life lost)|(gain.*life)|copy?(ied)?s?|spells?|ability?(ies)?).* target|target.*(distributes?|token|attach(ed)?s?|sacrificed?s?|destroy(ed)?s?|gets?|exiles?d?|return(ed)?s?|shuffles?|remove|(gains? control)|reveal|enchant|flip|discard|counter|(deal.*damage)|attack(ed)?s?|block(ed)?s?|fights?|(los.*life)|(life lost)|(gain.*life)|copy?(ied)?s?|spells?|ability?(ies)?)|damaged?s?|flips?(ped)?|gains?|library?(ies)?",
    'changeling': "(every|all other).*creature type",
    'board_wipe_dud': "(every|each|all).*land.*types",
    'cast': "(when|whenever).*cast.*spell.*,.*\."
    }

regex_draw_modes = {
    'basic_draw_search': "draw.*((an additional)|a|x|one|two|three|four|five|six|seven|eight|nine|ten|((as|that) many)) cards*",   ##  Basic draw x card(s)
    'lootn_rummage_search': "Discard.*card.*draw.*card|draw.*card.*discard.*card",  ## Rummage and Loot , might not really be worried about this distinction though
    'draw_x_search': "draws* cards* equal to"   ## Draw value will be set to 'X', since it is a variable amount 
    }

regex_etb_modes = {
    'land_tutor': "search (your|their) library for .* (land|plains|island|swamp|mountain|forest|((basic )*land)).*hand",   # search your library for a land and add to your hand
    'dork_rock': "\n{t}: add {[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]}({[wubrcgWUBRCG0123456789]\/[wubrcgWUBRCG0123456789]})*|{T}: Add ({[wubrcgWUBRGC0123456789]})*|\n{T}: Add .+mana|{T}:.* Add .+mana",   # removed {T},.*: Add ({[wubrcgWUBRGC0123456789]})*   , this is more for treasure tokens
    'land_ramp': "(land|plains|island|swamp|mountain|forest).*on.*battlefield",   ## search your library for a land and put it on the battlefield
    'sac_rock': "{T},.*: Add ({[wubrcgWUBRGC0123456789]})*(one|two|three|four|five)?( mana)?",
    'get_+1': "get.*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X]",
    'get_+1_counters': "(get|put|move|remove|add|with|distribute).*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X] counter",
    #get_fancy_counters is very thorough in searching through the list from https://mtg.fandom.com/wiki/Counter_(marker)/Full_List  - July 12 2021
    'get_fancy_counters': "(get|put|remove|add|move|with).*(deathtouch|lifelink|trample|indestructible|double strike|first strike|flying|hexproof|menace|reach|vigilance|verse|trap|growth|treasure|page|vitality|training|charge|spark|time|level|loyalty|spore|storage|lore|luck|plague|magnet|manabond|manifestation|knowledge|poison|energy|fat?d?e|healing|wish|egg|fungus|brick|experience|bribery|bounty|blaze|corruption|depletion|age|prey|quest|sleep|slumber|doom|flood|acorn|aegis|aim|arrow|arrowhead|awakening|blood|book|cage|carrion|coin|component|credit|corpse|crystal|cube|currency|death|delay|despair|devotion|divinity|dream|echo|elixir|enlightened|eon|eyeball|eyestalk|feather|fetch|filibuster|flame|foreshadow|fuse|gem|ghostform|glyph|gold|harmony|hatchling|hit|hone|hoofprint|hour|hourglass|hunger|ice|incarnation|incubation|infection|intervention|isolation|javelin|ki|landmark|mannequin|mask|matrix|mine|mining|mire|music|muster|met|night|omen|ore|pain|paralyzation|petal|petrification|phylactery|pin|point|polyp|pressure|pupa|rust|scream|scroll|shell|shield|silver|shred|sleight|slime|soot|soul|spark|spite|strife|study|task|theft|tide|tower|velocity|void|volatile|vow|voyage|wage|winch|wind).*counter",
    'gain_control': "gain.*control",
    'gain_life': "gain.*life",
    'lose_life': "lose.*life",
    'free_deploy': "put.*hand.*battlefield",
    'tap': " taps?.*(permanent|creature|artifact|enchantment|land)|\ntaps?.*(permanent|creature|artifact|enchantment|land)",
    'untap':" untaps?.*(permanent|creature|artifact|enchantment|land)|\nUntaps?.*(permanent|creature|artifact|enchantment|land)",
    'monarch': "become.*monarch",
    'mill': "mill.*card|card.*library.*graveyard",
    'treasure': "create.*treasure token|{T},.*: Add one mana",
    'mana_gain': "add {[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]}({[wubrcgWUBRCG0123456789]\/[wubrcgWUBRCG0123456789]})*|add ({[wubrcgWUBRGC0123456789]})*|add .+mana",
    'attachee': "attach.*(aura|equipment)|attach ",
    'temp_gains': "(get|gain|has).*(first strike|trample|lifelink|haste|\+[123456789]\/\+[123456789]|hexproof|shroud|indestructible|unblockable|menace|flying|double strike|vigilance).*end of turn",
    'buff': "(get|gain|has).*(first strike|trample|lifelink|haste|\+[1234567890x]\/\+[1234567890x]|hexproof|shroud|indestructible|unblockable|menace|flying|double strike|vigilance)",
    'debuff': "(get|has|lose).*((-)[1234567890x]\/(-)[1234567890x])*(flying|shadow|trample|first strike)",
    }

regex_ramp_modes = {
    'land_tutor': "search.*library.*(land|plains|island|swamp|mountain|forest).*hand",   
    'fetch_land': "search.*library.*(land|plains|island|swamp|mountain|forest).*on.*battlefield",
    'top_deck': "(look|reveal).*top.*library.*(land|plains|island|swamp|mountain|forest).*on.*battlefield",
    'hand_land': "(put|place).*(land|plains|island|swamp|mountain|forest).*hand.*battlefield",
    'grave_land': "(put|place).*(land|plains|island|swamp|mountain|forest).*graveyard.*battlefield",
    'dork_rock': "\n{t}: add {[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]}({[wubrcgWUBRCG0123456789]\/[wubrcgWUBRCG0123456789]})*|{T}: Add ({[wubrcgWUBRGC0123456789]})*|\n{T}: Add .+mana|{T}:.* Add .+mana",
    'treasure': "create.*treasure token|{T},.*: Add one mana",
    'phony': "{[wubrcgWUBRGC0123456789]}: add ({[wubrcgWUBRGC0123456789]})*|({[wubrcgWUBRGC0123456789]})*, {t}: add .+mana",
    'sac_ramp': "sacrifice.*: add ({[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]})*({[wubrcgWUBRCG0123456789]})*|sacrifice.*: add.*mana",    
    }

regex_mana_costs = {
    'mixed_mana': "{[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]}",
    'plain_mana': "{[1234567890]+}",
    'colour_mana': "{[wubrg]}",
    'white_symbol': "{w}",
    'blue_symbol': "{u}",
    'black_symbol': "{b}",
    'red_symbol': "{r}",
    'green_symbol': "{g}",
    'ignore_mana': "{x}+"
    }

regex_target_modes = {
    'exchange': "exchange.*target",
    'tap': "\ntaps?.*target|target.* taps?| taps?.*target|^taps? (up to )?(x|one|two|three|four|five|six|seven|as many|each) target|tap target",
    'untap':"untaps?.*target|target.*untaps?",    
    'buff': "target.*(get|gain|has).*( it|first strike|all creature types|trample|fear|phasing|lifelink|haste|\+[1234567890x]+\/\+[1234567890x]+|hexproof|protection|shroud|deathtouch|indestructible|unblockable|menace|flying|shadow|double strike|vigilance)",
    'debuff': "target.*(get|gain|has|lose).*((-)[1234567890x]+\/(-)[1234567890x]+)*( it|first strike|trample|shadow|phasing|all abilities)",
    'rebuff':"target.*(get|gain|has).*-[1234567890x]\/\+[1234567890x]|target.*(get|gain|has).*((\+)[1234567890x]\/-[1234567890x])",
    'control': "target.*gains control|gains control.*target|target.*gain control|gain control.*target",
    'draw': "target.*draw",
    'transform': "target.*become|target.*becomes",
    'graveyard': "target.*graveyard.*(battlefield|hand|library)|target.*(battlefield|hand|library).*graveyard",
    'fight': "fight.*target|target.*fight",
    'regenerate': "regenerate.*target|target.*regenerate",
    'ward': "spells.*opponents.*target.*cost.*more",
    'library_meddle': "look.*target.*library.*any order",
    'card_to_library': "(put|place|shuffle) target.*library",
    'retarget': "change the target.*target",
    'retext': "change the text.*target",
    'facedown': "(turn|flip( over)?|look at).*target.*face down|(turn|flip( over)?|look at) target.*face-down",
    'loselife': "target.*lose.*life",
    'looky_loo': "look at.*target.*(hand|library)",
    'deny': "target.* can't",
    'cheaper': "spells.*target.*cost.*less",
    'get_+1_counters': "(get|put|move|remove|add|with|distribute).*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X] counter",
    'counterspell': "counter.*target.*(spells?|ability|abilities)",
    'base_stats': "target.*(get|gain|has|lose).*base ",
    'stat_switch': "switch target creature's power and toughness",
    'fancy_counters': "(get|put|remove|add|move|with).*(deathtouch|lifelink|trample|indestructible|double strike|first strike|flying|hexproof|menace|reach|vigilance|verse|trap|growth|treasure|page|vitality|training|charge|spark|time|level|loyalty|spore|storage|lore|luck|plague|magnet|manabond|manifestation|knowledge|poison|energy|fat?d?e|healing|wish|egg|fungus|brick|experience|bribery|bounty|blaze|corruption|depletion|age|prey|quest|sleep|slumber|doom|flood|acorn|aegis|aim|arrow|arrowhead|awakening|blood|book|cage|carrion|coin|component|credit|corpse|crystal|cube|currency|death|delay|despair|devotion|divinity|dream|echo|elixir|enlightened|eon|eyeball|eyestalk|feather|fetch|filibuster|flame|foreshadow|fuse|gem|ghostform|glyph|gold|harmony|hatchling|hit|hone|hoofprint|hour|hourglass|hunger|ice|incarnation|incubation|infection|intervention|isolation|javelin|ki|landmark|mannequin|mask|matrix|mine|mining|mire|music|muster|met|night|omen|ore|pain|paralyzation|petal|petrification|phylactery|pin|point|polyp|pressure|pupa|rust|scream|scroll|shell|shield|silver|shred|sleight|slime|soot|soul|spark|spite|strife|study|task|theft|tide|tower|velocity|void|volatile|vow|voyage|wage|winch|wind|loyalty).*counter"
    }

regex_wipe_modes = {
    'debuff': "(every|each|all|creatures).*(get|gain|has).*((-)[1234567890x]\/(-)[1234567890x])",
    'tap': "^taps?.*(every|each|all)|(every|each|all).* taps?| tap.*(every|each|all)",
    'untap':"untaps?.*(every|each|all)|(every|each|all).*untaps?",    
    'buff': "(every|each|all|creatures you control).*(get|gain|has|have).*(first strike|all creature types|trample|phasing|lifelink|haste|\+[1234567890x]+\/\+[1234567890x]+|hexproof|protection|shroud|deathtouch|indestructible|unblockable|menace|flying|shadow|double strike|vigilance)",
    'boost': "(get|have|has|with).*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X] .*for (every|each|all|creatures|other)",
    'spell_copy': "copy.* (spell|ability|spell) for (each|every|all)",
    'rebuff':"(every|each|all|creatures).*(get|gain|has).*-[1234567890x]\/\+[1234567890x]|target.*(get|gain|has).*((\+)[1234567890x]\/-[1234567890x])",
    'control': "(every|each|all).*gains control|gains control.*(every|each|all)|(every|each|all).*gain control|gain control.*(every|each|all)",
    'draw': "(every|each|all|each other) player.*draw",
    'transform': "(every|each|all).*become|(every|each|all).*becomes",
    'graveyard': "(every|each|all).*graveyard.*(battlefield|hand|library)|(every|each|all).*(battlefield|hand|library).*graveyard",
    'fight': "fight.*(every|each|all)|(every|each|all).*fight",
    'regenerate': "regenerate.*(every|each|all)|(every|each|all).*regenerate",
    'card_to_library': "(put|place|shuffle) (every|each|all).*library",
    'facedown': "(turn|flip( over)?|look at).*(every|each|all).*face down|(turn|flip( over)?|look at) (every|each|all).*face-down",
    'loselife': "each.*lose.*life",
    'deny': "(every|each|all|creatures|permanents|lands|artifacts|sorceries|instants|enchantments).* can't",
    'base_stats': "(every|each|all|creatures).*(get|gain|has|lose).*base ",
    'get_+1_counters': "(get|put|move|remove|add|with|distribute|place).*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X] counter.*(every|each|all|creatures)|(every|each|all|creatures).*(get|put|move|remove|add|with|distribute|place).*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X] counter",
    'mill': "(every|each|all|each other).*mill.*card",
    'discard': "(every|each|all|each other) player.*discards",
    'damage': "deal.*damage.*to.*(each|every|all|other|creatures|players|planeswalkers)",
    'lifegain': "gain.* life.*for (every|each|all|other)",
    'sacrifice': "sacrifice.*(each|all|other)|(each|all|other).*sacrifice",
    'destroy': "destroy.*and (all|each) other.*with|destroy.* (all|each|every).*",
    'exile': "exile.*and (all|each) other.*with",
    'return': "return.*and (all|each) other.*with|return.* (cards|all|each|every).*",
    'ETB_counters': "each other.*(creature|planeswalker|permanent|artifact).*enter.*additional.*counter",
    'frogify': "loses all.*abilities",
    'cost_more': "(every|each|all|activated|white|blue|red|black|green|colorless).*(spell|ability).*cost.*more",
    'cost_less': "(every|each|all|activated|white|blue|red|black|green|colorless).*(spell|ability).*cost.*less",
    'PW_Abilities': "(each|all|every|each other).*planeswalker.*abilities",
    'copy': "(copy|copies).*for each"
    }

regex_triggered_modes = {
    'phases': "(start|beginning|end|before|during|at) (of|your|an|the).* (end step|main phase|upkeep|untap|combat).*,.*\.|.*(start|beginning|end|before|during).*(end step|main phase|upkeep|untap step|combat)",
    'cast_noncreature': "(when|whenever).*cast.*(instant|aura|vehicle|equipment|sorcery|kicked|this|noncreature|artifact|enchantment|arcane|planeswalker).*,.*\.",
    'cast_creature': "(when|whenever).*cast.*( creature|commander).*,.*\.",
    'cast_historic': "(when|whenever).*cast.*(historic|artifact|legendary|saga).*spell.*,.*\.",
    'heroic?': "(when|whenever).*cast.*(instant|sorcery|kicked|this|noncreature|artifact|enchantment|arcane|planeswalker|spell).*targets.*,.*\.",
    'color_spell': "(when|whenever).*cast.*(red|white|blue|green|black|colorless|multicolored).*spell,.*\.",
    'cost_spell': "(when|whenever).*cast.*spell with.*({x}|mana value|converted mana cost).*,.*\.",
    'attacks': "(when|whenever).*attack.*\.",
    'blocks': "(when|whenever).*block.*\.",
    'damages': "(when|whenever).*deal.*damage.*,.*\.",
    'shuffle': "(when|whenever).*shuffle.*\.",
    'surveil': "(when|whenever).*surveil.*\.",
    'mutate': "(when|whenever).*mutate.*\.",
    'exile': "(when|whenever).*exile.*\.",    
    'loot': "(when|whenever).*draw.*,.*discard.*\.",
    'death': "(when|whenever).*(die|into.*graveyard|leave).*,.*\.",
    'draw': "(when|whenever).*(you|opponent|player).*draws.*,.*\.",
    'ETB': "enters? the battlefield.*",
    'grave_cast': "(when|whenever).*(cast).*from.*(graveyard|other than your hand).*,.*\.",
    'sacrifice': "(when|whenever).*sacrifice.*,.*\.",
    'activate': "(when|whenever).*activate.*(ability),.*\.",
    'gain_life': "(when|whenever).*gain.*life.*,.*\.",
    'lose_life': "(when|whenever).*lose.*life.*,.*\.",
    'discard': "(when|whenever).* (you|player|opponent).* (cycle|discard).*,.*\.",
    'counters': "(when|whenever).*(counter).*(put|place|add|remove|move|with).*,.*\.",
    'morph': "(when|whenever).*(turn|flip).*face (up|down).*,.*",
    'tutor': "(when|whenever).*(player|you|opponent).*search.*library.*,.*\.",
    'tapped': "(when|whenever).*(becomes tapped|tap).*,.*",
    'monstrous': "(when|whenever).*monstrous.*,.*",
    'targeted': "(when|whenever).*becomes the target.*,.*",
    'miracle': "miracle cost when you draw",
    'extort': "extort|Whenever you cast a spell, you may pay",
    'returned': "(when|whenever).*(creature|artifact|enchantment|permanent).*return.*,.*\.",
    # triggered keyword abilities..
    # persist, landfall, enrage, heroic, inspired, etc
    }

regex_activated_modes = {
    'tap': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgceT0]})*,*: tap.*\.|({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgcT0]})*:.*may tap .*\.",
    'untap': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgceT0]})*,*:.*untap.*\.",
    'destroy': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubregcT0]})*,*: destroy.*\.",
    'exile': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgceT0]})*,*: exile.*\.",
    'deploy': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*:.*(put|place).*(card|creature|instant|sorcery|artifact|planeswalker|enchantment|aura).*hand.*battlefield",
    'reanimate': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*(put|place).*(card|creature|instant|sorcery|artifact|elemental|planeswalker|enchantment|aura).*(graveyard|exile).*battlefield",
    'recycle': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubregcT0]})*,*:.*(put|place|shuffle).*(card|creature|instant|permanent|sorcery|artifact|planeswalker|enchantment|aura).*(battlefield|graveyard|own).*library",
    'selective': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789weubrgcT0]})*,*:.*(target|all|each).*(card|creature|instant|permanent|sorcery|artifact|planeswalker|enchantment|aura).*(with|without) (flying|power|toughness|defender).*",
    'deny': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*:.*(this turn|target).*(card|creature|instant|sorcery|artifact|planeswalker|enchantment|aura).*can't",
    'reveal': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubergcT0]})*,*: reveal.*\.",
    'control': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789weubrgcT0]})*,*:.*gain.*control.*\.",
    'tutor': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*: search.*library.*\.",
    'sacrifice': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456e789wubrgcT0]})*,*: sacrifice .*\.",
    'return': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[12345678e9wubrgcT0]})*,*: return .*\.",
    'manifest': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[12345678e9wubrgcT0]})*,*: manifest .*\.",
    'regenerate': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123e456789wubrgcT0]})*,*: regenerate .*\.",
    'blink': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[1234567e89wubrgcT0]})*,*: (exile|remove) .*(,|\.).*return.*battlefield",
    'token': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[12345678e9wubrgcT0]})*,*:.* create.*token",
    'mana': "{t}: add {[wubrcgWUBRCG0123456789]\/[wubrcgWUBRGC0123456789]}({[wubrcgWUBRCG0123456789]\/[wubrcgWUBRCG0123456789]})*|{t}: add ({[wubrcgWUBRGC0123456789]})*|\n{t}: Add .+mana|{t}:.* Add .+mana|({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*(remove|put).*counter.*: add.* ({[wubrgc2341567890]})*mana|{[123456789t]}:.*add.*mana",
    'buff': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789weubrgcT0]})*,*:.*(get|gain|has).*( it(,|\.)* |first strike|all creature types|trample|infect|fear|phasing|lifelink|haste|\+[1234567890x]+\/\+[1234567890x]+|hexproof|protection|shroud|deathtouch|indestructible|walk|unblockable|menace|flying|shadow|double strike|vigilance)",
    'debuff': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*(get|gain|has|lose).*( it(,|\.)* |first strike|all creature types|trample|infect|fear|phasing|lifelink|haste|-[1234567890x]+\/-[1234567890x]+|hexproof|protection|shroud|deathtouch|indestructible|unblockable|menace|flying|shadow|double strike|vigilance)",
    'rebuff': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*(has|lose).*( it(,|\.)* |base (power|toughness)|first strike|all creature types|trample|infect|fear|phasing|lifelink|haste|-[1234567890x]\/\+[1234567890x]|\+[1234567890x]\/\-[1234567890x]|hexproof|protection|shroud|deathtouch|indestructible|unblockable|menace|flying|shadow|double strike|vigilance)",
    'proliferate': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*proliferate",
    'redirect': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*damage.*would.*dealt.*target.*instead",
    'charge_cntr': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*(get|put|remove|add|move|with).*(deathtouch|lifelink|trample|indestructible|double strike|first strike|flying|hexproof|menace|reach|vigilance|verse|trap|growth|treasure|page|vitality|training|charge|spark|time|level|loyalty|spore|storage|lore|luck|plague|magnet|manabond|manifestation|knowledge|poison|energy|fat?d?e|healing|wish|egg|fungus|brick|experience|bribery|bounty|blaze|corruption|depletion|age|prey|quest|sleep|slumber|doom|flood|acorn|aegis|aim|arrow|arrowhead|awakening|blood|book|cage|carrion|coin|component|credit|corpse|crystal|cube|currency|death|delay|despair|devotion|divinity|dream|echo|elixir|enlightened|eon|eyeball|eyestalk|feather|fetch|filibuster|flame|foreshadow|fuse|gem|ghostform|glyph|gold|harmony|hatchling|hit|hone|hoofprint|hour|hourglass|hunger|ice|incarnation|incubation|infection|intervention|isolation|javelin|ki|landmark|mannequin|mask|matrix|mine|mining|mire|music|muster|met|night|omen|ore|pain|paralyzation|petal|petrification|phylactery|pin|point|polyp|pressure|pupa|rust|scream|scroll|shell|shield|silver|shred|sleight|slime|soot|soul|spark|spite|strife|study|task|theft|tide|tower|velocity|void|volatile|vow|voyage|wage|winch|wind|loyalty).*counter on",
    'draw': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*:.*draw.*\.",
    'discard': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubregcT0]})*,*:.*discard.*\.",
    'block': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*:.*block.*turn.*\.",
    'attack': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubregcT0]})*,*:.*attack.*turn.*\.",
    'end_turn': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubergcT0]})*,*:.*end.*turn\.",
    'spell-ability_copy': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789ewubrgcT0]})*,*:.*(copy|copies).*(target|each|all).*(activated|triggered)* (spell|ability|abilities|instant|sorcery).*\.",
    'xtra_turn': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789ewubrgcT0]})*,*:.*take.*extra turn",
    'mill': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubergcT0]})*,*:.*mill.*\.",
    'damage': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubergcT0]})*,*:.*deal.*damage.*\.",
    'prevent_damage': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789weubrgcT0]})*,*:.*prevent.*damage.*\.",
    'phases': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*:.*phase.*\.",
    'transform': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubergcT0]})*,*:.*target.*become|target.*becomes",    
    'lifegain': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wuebrgcT0]})*,*:.*gain.*life.*\.",
    'lifeloss': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789weubrgcT0]})*,*,*:.*lose.*life.*\.",    
    'scry': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*: scry.*\.",
    'top_deck': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubregcT0]})*,*:.* look.*top.*library.*\.",
    'populate': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*.*:.*populate",
    'mo_counters': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*.*:.*(double|triple).*counter.*(artifact|enchantment|creature|permanent|historic|land)",
    'counterspell': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789wubrgecT0]})*,*.*:.*counter.*(target|all|each) (spell|ability|abilities).*",
    'get_+1_counters': "({[wubrcg0123456789]\/[wubrcgWUBRCG0123456789]})*({[123456789weubrgcT0]})*,*:.*(get|put|move|remove|add|with|distribute).*[\+?\-?[0123456789X]\/+\+?\-?[0123456789X] counter",    
    # equip, cycle, morph, 
    }

regex_manacolor = {
    'getland_m_clr': ": Add (.)* any (.)*color|: Add (.)*mana(.)*different color",
    'getland_m_clr2': ": Add {[WUBRGC]}[^, {]",   # for single color lands only
    'getland_m_clr3': ": Add {[WUBRGC]} or {[WUBRGC]}|Add {[WUBRGC]\/[WUBRGC]}", # for dual lands only
    'getland_m_tri': "Add {[WUBRGC]}(, )*({[WUBRGC]})*(, )*(or)* ({[WUBRGC]})",  # for tri-ome only
    'getland_m_dbl': ": Add {[WUBRGC]}{[WUBRGC]}[^, {]"  ,  # for 2mana-lands only
    'combination_mana': "any combination of {[WUBRG]} and\/or ({[WUBRG]})*",
    'mana_symbols': "{[WUBRG1]}({[WUBRG1]})*|{[WUBRG1]\/[WUBRG1]}"    #  just for regex_get_mana
    }

def regex_get_mana_symbols(search_this):
    white_count = len(re.findall(regex_mana_costs['white_symbol'], search_this, re.IGNORECASE))
    blue_count = len(re.findall(regex_mana_costs['blue_symbol'], search_this, re.IGNORECASE))
    black_count = len(re.findall(regex_mana_costs['black_symbol'], search_this, re.IGNORECASE))
    red_count = len(re.findall(regex_mana_costs['red_symbol'], search_this, re.IGNORECASE))
    green_count = len(re.findall(regex_mana_costs['green_symbol'], search_this, re.IGNORECASE))
    
    pattern = re.compile(regex_mana_costs['mixed_mana'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        if 'w' in matchfound.lower():
            white_count += 1
        if 'u' in matchfound.lower():
            blue_count += 1
        if 'b' in matchfound.lower():
            black_count += 1
        if 'r' in matchfound.lower():
            red_count += 1
        if 'g' in matchfound.lower():
            green_count += 1

    print ("white dedication: ", white_count)
    print ("blue dedication: ", blue_count)
    print ("black dedication: ", black_count)
    print ("red dedication: ", red_count)
    print ("green dedication: ", green_count)
    return (white_count, blue_count, black_count, red_count, green_count)
    
def regex_get_cmc(search_this):
    total_cmc = 0
    pattern = re.compile(regex_mana_costs['mixed_mana'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        if len(matchfound) > 2:
            # print ("mixed mana search:" , len(matchfound), matchfound)
            total_cmc +=1
            
    pattern = re.compile(regex_mana_costs['colour_mana'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        if len(matchfound) > 2:
            # print ("colour mana search:" , len(matchfound), matchfound)
            total_cmc +=1
            
    pattern = re.compile(regex_mana_costs['plain_mana'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        # print ("plain mana" , matchfound)
        matchfound = matchfound.replace("{","")
        matchfound = matchfound.replace("}","")        
        total_cmc = total_cmc + int(matchfound)
    
    # print ("total CMC: ",total_cmc )
    return total_cmc
    
def regex_get_aac(search_this):
    """Regex search to count the number of activated abilities are on card (usually lands)
    Parameters: search_this:  Oracle text of the card, after check_oracle_text()
    Returns: Integer 'count_abilities' 
    """
    count_abilities = 0
    # if(re.search(searchtype, search_this)):
        # has_additional = 0
    pattern = re.compile(regex_searchmode['activeabilitysearch'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    otext = search_this
    mana_ability_counter = 0
    for match in matches:
        """Extract the relevant parts """
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        count_abilities += 1
    return count_abilities
    
def regex_get_mv(searchtype, search_this):
    """Regex search to find the greatest amount of mana acquired per TAP for Lands (though I guess it doesn't need to be just lands)
    Parameters: searchtype:  The Regex search pattern  (this is called from Land_handle() in MTG_Main in a For loop) 
                search_this:  Oracle text of the card, after check_oracle_text()
    Returns: String or Integer 'mana_value'  - usually 1, sometimes 2 or 'X'
    """

    pattern = re.compile(searchtype)
    matches = pattern.finditer(search_this)
    mana_value = 0
    highest_mana = 0
    comma_counter = 0
    """It's expected that there usually won't be more than 1 or 2 matches     """
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        manacostread = matchfound.replace("Add ","")
        """searchtype will determine how to filter the results and affect how to count the number of abilities"""
        if searchtype == regex_searchmode['wordmanasearch']:
            manacostread = manacostread.replace("mana","         ")
            usethis = manacostread[0:7]
            # print (usethis)
            mana_value = mtg_main.convert_manawords.get(usethis.lower().strip())
            # print (usethis, " converted to " , mana_value)
        elif searchtype == regex_searchmode['plainmanasearchmultiples']:
            """Add {B}, {W}, {R}, or {2}:   this would need to count as generating 2, not 5 """
            comma_counter = matchfound.count(",")
            if comma_counter > 0: mana_value = regex_get_cmc(manacostread) - comma_counter
            else:
                if "or" in matchfound: mana_value = regex_get_cmc(manacostread) - 1
        else:
            mana_value = regex_get_cmc(manacostread)
        # try:
        #     if int(mana_value) > highest_mana: highest_mana = mana_value
        # except:
        #     if mana_value > highest_mana: highest_mana = mana_value
        # print (matchfound, " Mana Cost: ",manacostread, " -> ", mana_value)
    if "for each" in search_this:
        # print ("Found likely X-mana generator")
        mana_value = "X"

    return mana_value

def regex_get_mana(search_this): 
    """Searching within mana generated from tap abilities  (part 2),  ex  {'Add {R} or {B} or {W/U}'} and pulling out the colors
     - called from regex_get_mclr()
    Parameters:   search_this:  Oracle text of the card, after check_oracle_text()
    Returns: String  'mana_code'  - not necessarily the colour identity of a card, only counts color symbols for mana generated
    """
    pattern = re.compile(regex_manacolor['mana_symbols'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    mana_code = ""
    mana_color_terms = ['W','U','B','R','G']
    """this for loop is done outside the following for loop just incase no matches are found"""
    for colors in mana_color_terms:
        if colors in search_this:
            mana_code = mana_code + str(colors)    
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        # print (matchfound)
        for colors in mana_color_terms:
            if colors in matchfound:
                mana_code = mana_code + str(colors)    
    return mana_code

def regex_get_mclr(search_this):
    """Searching within mana generated from tap abilities for colour codes (part 1),   {'Add one mana of any color'} or {'Add an amount equal to number of storage counters removed'}
     - called from Land_handle() in MTG_Main.    RUNS regex_get_mana() to narrow down color symbols
    Parameters:   search_this:  Oracle text of the card, after check_oracle_text()
    Returns: String  'mana_code'  - not necessarily the colour identity of a card, only counts color symbols for mana generated
    """
    mana_code = ""
    mana_color_terms = ['W','U','B','R','G']
    
    for pattern_search in regex_manacolor:
        pattern = re.compile(regex_manacolor[pattern_search], re.IGNORECASE)
        matches = pattern.finditer(search_this)
        for match in matches:
            startgrab = min(match.span())
            endgrab = max(match.span())
            matchfound = search_this[startgrab:endgrab]
            # print (pattern_search, matchfound, search_this)
            """For looping through the different Regex pattern searches in regex_manacolor{}, only some are utilized"""
            if regex_manacolor[pattern_search] == regex_manacolor['mana_symbols']:
                ## This is already done in regex_get_mana()
                continue
            elif regex_manacolor[pattern_search]  == regex_manacolor['getland_m_clr']:
                mana_code = "WUBRG"
                break
            elif regex_manacolor[pattern_search]  == regex_manacolor['combination_mana']:
                matchfound = matchfound.replace("any combination of {","")
                matchfound = matchfound.replace("} and/or {","")
                matchfound = matchfound.replace("}","")
                results = regex_get_mana(matchfound)
                mana_code = str(mana_code)+str(results)                
            else:
                matchfound = matchfound.replace("}: Add ","")
                # print ("Searching in ", matchfound)
                results = regex_get_mana(matchfound)
                mana_code = str(mana_code)+str(results)
    if mana_code is None or mana_code == "": mana_code = "C"
    # print (set(mana_code))
    return set(mana_code)
     
def regex_get_keywords(search_this):
    """"Searching with the card object dictionary for the 'keywords'
    Called from Single_Sided_Card() and Handle_Double() in MTG_Main
    Parameters:  search_this: The card object dictionary,  str(the_card.__dict__.items()
    Returns:  String 'card_keywords' - it will looks like a list on the table though """

    # results = re.findall(searchtype, search_this) ## Not using this yet
    # for result in results:
    #     print (result)
    pattern = re.compile(regex_searchmode['keywordsearch'])
    matches = pattern.finditer(search_this)
    card_keywords = ""
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        card_keywords = matchfound.replace("'keywords': [","")
        card_keywords = card_keywords.replace("]","")
        # if len(card_keywords) > 4: print (card_keywords)
        break
    return card_keywords

def regex_get_image(search_this):
    ##   'normal': 'https://c1.scryfall.com/file/scryfall-cards/normal/front/6/4/647c2269-bdc7-4455-9158-73abbff6e50e.jpg?1627705778',
    """"Searching with the card object dictionary for the "image_uris":{...} 
    then searching within that block for "normal":"http....."
    Parameters:  search_this: The card object dictionary,  str(the_card.__dict__.items()"""
    
    image_link = ""
    pattern = re.compile(regex_searchmode['imagesearch'])
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        # print ("Now search string: ", matchfound)
        ## Next search within 
        pattern = re.compile(regex_searchmode['normal_image_search'])
        submatch = pattern.finditer(matchfound)
        for result in submatch:
            startgrab = min(result.span())
            endgrab = max(result.span())
            normal_image = matchfound[startgrab:endgrab]
            image_link = normal_image.replace("'normal': '","")
            image_link = image_link.replace("',","")
    
    return image_link

def regex_get_lifegains(search_this):
    """Searching for life gain effects from spells or etb effects and determining how much life is restored
    Parameters:  search_this: Oracle text of the card, after check_oracle_text()
    Returns: String 'best_yet'
    """
    lifegain = ""
    pattern = re.compile(regex_searchmode['all_life_gains'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    best_yet = 0
    x_triggered = False
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        if "life equal to" in matchfound.lower() or "x life" in matchfound.lower() or "life for each" in matchfound.lower():
            x_triggered = True
            break
        else:
            lifegain = [int(s) for s in matchfound.split() if s.isdigit()]
            """pulls numbers only """
            
            try:
                if max(lifegain) > best_yet: best_yet = max(lifegain)
            except Exception as e:
                print ("exception encountered ", e, "lifegain:",lifegain , matchfound, " best yet: ", best_yet)
                lifegain = [0]            
    
    if x_triggered == True: best_yet = "X"
    return str(best_yet)

def regex_get_dmggains(search_this):
    """Searching for damage effects from spells or etb effects and determining how much damage is dealt (to each possible target, not total)
    Parameters:  search_this: Oracle text of the card, after check_oracle_text()
    Returns: String 'best_yet'
    """
    dmggain = ""
    x_damage_terms_list = ["damage equal to", "x damage", "x life", ]
    pattern = re.compile(regex_searchmode['all_damage_gains'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    best_yet = 0
    x_triggered = False
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        for terms in x_damage_terms_list:
            if terms in matchfound.lower() or terms in search_this.lower():
                """Once determined that this deals a variable amount of damage, than 'X' is returned and what will be used in the table"""
                x_triggered = True
                break
        if x_triggered == True: break
        
        dmggain = [int(s) for s in matchfound.split() if s.isdigit()]
        """Looping through the regex matches, and checking the new damage values against what was found earlier """
        if dmggain != []:
            try:
                if max(dmggain) > best_yet: best_yet = max(dmggain)
            except Exception as e:
                print ("exception encountered ", e, "dmggain:",dmggain , matchfound, " best yet: ", best_yet)
                dmggain = [0]
        else:
            dmggain = [0]

    if x_triggered == True: best_yet = "X"    
    return str(best_yet)

def regex_get_ppa(search_this):
    """Searching for Planeswalkers passive abilities, usually listed before the activated abilities
    Parameters:  search_this: Oracle text of the card, after check_oracle_text()
    Returns: String 'Passive'  {'TRUE'/'FALSE}
    """    
    
    Passive = 'FALSE'
    pattern = re.compile(regex_searchmode['planeswalker_ability_index'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    # ability_count = 0
    index = 0
    """Just need to retrieve the index of where the activated abilities start """
    for match in matches:
        # ability_count += 1
        if index == 0: index = int(min(match.span()))
        # print (index)
        # print ("First ability found at index ", min(match.span()))        
        break

    if index > 12:
        Passive = 'TRUE'
    return Passive

def regex_get_pboosts(search_this):
    """Searching for Planeswalker's boost or {+X} activated abilities
    Parameters:  search_this: Oracle text of the card, after check_oracle_text()
    Returns: List 'pboosts'   - How much the 'X' value is.   usually expecting 0 or 1 abilities, but sometimes there are 2
    """    
    pboosts = ""
    pattern = re.compile(regex_searchmode['planeswalker_boosts'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    ability_count = 0
    for match in matches:
        ability_count += 1
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        matchfound = matchfound.replace(":","")
        matchfound = matchfound.replace("+","")
        pboosts = pboosts + matchfound

    if pboosts == "": pboosts = ""
    # print (ability_count, " boosts found", pboosts)
    # print (list(pboosts))
    return (list(pboosts))

def regex_get_pcosts(search_this):
    """Searching for Planeswalker's cost or {-X} activated abilities
    Parameters:  search_this: Oracle text of the card, after check_oracle_text()
    Returns: List 'pcosts'   - How much the 'X' value is.   usually expecting 1 ability, but sometimes there are 2
    """    
    pcosts = ""
    pattern = re.compile(regex_searchmode['planeswalker_costs'], re.IGNORECASE)
    matches = pattern.finditer(search_this)
    ability_count = 0
    for match in matches:
        ability_count += 1
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        matchfound = matchfound.replace(":","")
        matchfound = matchfound.replace("-","")
        pcosts = pcosts + matchfound
    if pcosts == "": pcosts = ""
    # print (ability_count, " costs found", pcosts)
    # print (list(pcosts))
    return (list(pcosts))

def regex_deeper_ETB(search_this, card_type):
    """Called from regex_get_ETB() - Looking through the enter the battlefield text to narrow down what type of effects it has
    Does several Regex searches to try and find as many details on the effects as possible, within reason
    Parameters:   search_this:  ETB portion of the card's oracle text
                    card_type:  self explanatory, used with regex_etb_modes['dork_rock'] 
    Returns:  String 'etb'  - All effects found separated by spaces where regex_get_ETB() will process
    """
    types_of_counters = ['deathtouch','lifelink','trample','indestructible', 'double strike', 'first strike', 'flying', 'hexproof','menace','reach','vigilance',
                         'verse','trap','growth','treasure','page','vitality','training','charge','spark','time','level',
                        'loyalty','spore','storage','lore','luck','plague', 'magnet','manabond','manifestation','knowledge','poison','energy','fate','fade',
                        'healing','wish','egg','fungus','brick','experience','bribery','bounty','blaze','corruption','depletion','age','prey','quest','sleep',
                        'slumber','doom','flood','acorn','aegis','aim','arrow','arrowhead','awakening','blood','book','cage','carrion','coin','component',
                        'credit','corpse','crystal','cube','currency','death','delay','despair','devotion','divinity','dream','echo','elixir','enlightened',
                        'eon','eyeball', 'eyestalk','feather','fetch','filibuster','flame','foreshadow','fuse','gem','ghostform','glyph','gold','harmony',
                        'hatchling','hit','hone','hoofprint','hour','hourglass','hunger','ice','incarnation','incubation','infection','intervention', 'isolation',
                        'javelin','keyword','ki','landmark','mannequin','mask','matrix','mine','mining','mire','music','muster','met','night','omen','ore','pain',
                        'paralyzation','petal','petrification','phylactery','pin','point','polyp','pressure','pupa', 'rust','scream','scroll','shell','shield',
                        'silver','shred','sleight','slime','soot','soul','spark','spite','strife','study','task','theft','tide','tower','velocity','void',
                        'volatile','vow','voyage','wage','winch','wind']
    
    etb = ""
    
    pattern = re.compile(regex_etb_modes['get_fancy_counters'], re.IGNORECASE)    
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        for terms in types_of_counters:
            if terms in matchfound: etb = etb + terms.capitalize()+ "_counters "

    for etbs in regex_etb_modes:
        if re.findall(regex_etb_modes[etbs], search_this, re.IGNORECASE):
            # print ("  :found ", etbs)
            if etbs == 'dork_rock':
                if "artifact" in card_type.lower() and "creature" not in card_type.lower(): etb = etb + "Mana_Rock "
                if "creature" in card_type.lower(): etb = etb + "Mana_Dork "
            elif etbs == 'get_fancy_counters':
                continue
            else:
                etb = etb + etbs.capitalize() + " "

    return etb

def regex_get_ETB(search_this, card_type, keyword_list):
    """Searching for ETB effects from a list of terms and adding them to the list of effects on the card
    RUNS regex_deeper_ETB()
    Parameters:   search_this:  Card's oracle text after check_oracle_text()
                    card_type:  Card type, to pass to regex_deeper_ETB(), used to separate the 'mana_dorks' from the 'mana_rocks' 
    Returns:  List  'list(filter_list)'  
    """
    etb = ""
    keywords = mtg_main.rebuild_list(keyword_list)    
    regex_etb_terms = ['target', 'draw', 'energy', 'scry', 'sacrifice', 'tapped', 'damage', 'destroy', 'return', 'exile', 'discard', 'token', 'library','copy', 'choose', 'untap']  # or will these be searched under 'TARGET' and 'WIPE'

    pattern = re.compile(regex_searchmode['etb_filter'], re.IGNORECASE)    
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        for terms in regex_etb_terms:
            if terms in matchfound.lower(): etb = etb + terms.capitalize() + " "

        # if re.match(regex_searchmode['wipe_filter'], matchfound, re.IGNORECASE):           ##  I seem to have trouble getting results with this statement
        pattern = re.compile(regex_searchmode['wipe_filter'], re.IGNORECASE)    
        matches = pattern.finditer(matchfound)
        for match in matches:
            etb = etb + "Wipe "
            break
        """regex_deeper_ETB() looks at cards where the term can't be extracted from a single word on the card"""
        deeper_etb_search = regex_deeper_ETB(matchfound, card_type)
        etb = etb + deeper_etb_search

    if 'landfall' in keywords.lower(): etb = etb + "Landfall "
    if 'sunburst' in keywords.lower(): etb = etb + "Sunburst "
    if 'soulbond' in keywords.lower(): etb = etb + "Soulbond "
    if 'enchant' in keywords.lower(): etb = etb + "Enchant "
    if 'revolt' in keywords.lower(): etb = etb + "Revolt "
    if 'evoke' in keywords.lower(): etb = etb + "Evoke "
    if 'constellation' in keywords.lower(): etb = etb + "Constellation "
    if 'equipment' in card_type.lower(): etb = etb + "Equipment "
    if etb == "": etb = "Other"
    
    final_etb = set(etb.split(" "))
    filter_list = filter(lambda x: x != "", final_etb)
    """Removes all empty items in the list """
    return list(filter_list)

def regex_get_wipe(search_this, keyword_list):
    """Searching through regex_searchmode['wipe_filter'] looking for board wipe lexicon ('each','all', etc) and
    searching within the results throught the list of regex_wipe_terms[]
    Called by Wipe_Search() from MTG_Main.py
    Parameters:   search_this:  ETB portion of the card's oracle text
                    card_type:  self explanatory, used to search for keyword 'Overload' which makes a spell a board wipe
    Returns:  list 'list(filter_list)' 
    """
    wipe = ""
    keywords = mtg_main.rebuild_list(keyword_list)
    regex_wipe_terms = ['destroy', 'exile', 'return', 'shuffle', 'sacrifice', 'damage' ]#,  'discard']  # or will these be searched and clasified under 'TARGET' and 'WIPE'
    # regex_etb_terms .extend(keyword_list)
    pattern = re.compile(regex_searchmode['wipe_filter'], re.IGNORECASE)    
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]        
        for terms in regex_wipe_terms:
            if terms in matchfound.lower(): wipe = wipe + terms.capitalize() + " "

    for wipes in regex_wipe_modes:
        # print (re.findall(regex_target_modes[filters], oracletext, re.IGNORECASE))
        if re.findall(regex_wipe_modes[wipes], search_this, re.IGNORECASE):
            # print ("  :found ", wipes)
            wipe = wipe + wipes.capitalize() + " "

    if 'overload' in keywords.lower(): wipe = wipe + "Overload "
    if 'radiance' in keywords.lower(): wipe = wipe + "Radiance "
    if wipe == "":
        if re.findall(regex_searchmode['changeling'], search_this, re.IGNORECASE): wipe = "Changeling"
        # This will get removed anyway, may as well use the same name
        if re.findall(regex_searchmode['board_wipe_dud'], search_this, re.IGNORECASE): wipe = "Changeling"
        
    if wipe == "": wipe = "Other"
    final_wipe = set(wipe.split(" "))
    filter_list = filter(lambda x: x != "", final_wipe)
    return list(filter_list)

def regex_get_ramp(search_this, card_type):
    """Called from Ramp_Search() - Looking for ramp terminology on the card
    Does some Regex searches to try and isolate in what way it ramps, whether adding a land from your deck or hand or using a mana rock
    Parameters:   search_this:  ETB portion of the card's oracle text
                    card_type:  used with regex_etb_modes['dork_rock'] , like in regex_deeper_ETB()
    Returns:  String 'ramp'  
    """
    ramp = ""
    for ramps in regex_ramp_modes:
        if re.findall(regex_ramp_modes[ramps], search_this, re.IGNORECASE):
            # print ("  :found ", ramps)
            if ramps == 'dork_rock':
                if "artifact" in card_type.lower() and "creature" not in card_type.lower(): ramp = ramp + "Mana_Rock "
                if "creature" in card_type.lower(): ramp = ramp + "Mana_Dork "
            else:
                ramp = ramp + ramps.capitalize() + " "
            
    if ramp == "": ramp = "Other"
    if ramp == "Other" and "landfall" in search_this: ramp = ""
    """If the type of ramp hasn't been isolated, it is set to 'Other' since it still had some typical ramp talk in the oracle text
    cards with the landfall trigger have 'when a land enters the battlefield' in the text, which is the only reason they got this far"""

    return ramp

def regex_get_draw(search_this):
    """Regex search through oracle text and determine the most number of cards that this can draw
    Parameters:   search_this:  ETB portion of the card's oracle text
    Returns: String  'best_yet'
    """
    draw = ""
    best_yet = "0"
    x_found = False
    pattern = re.compile(regex_draw_modes['basic_draw_search'])    
    matches = pattern.finditer(search_this)
    for match in matches:
        startgrab = min(match.span())
        endgrab = max(match.span())
        matchfound = search_this[startgrab:endgrab]
        matchfound = matchfound.replace("draws","")
        matchfound = matchfound.replace("draw","")
        matchfound = matchfound.replace("cards","")
        matchfound = matchfound.replace("card","").strip()
        """I should update this so it isn't so clunky"""
        if matchfound == 'a':
            draw = '1'
        else:
            draw = mtg_main.convert_manawords.get(matchfound, 'Other')
            if draw == 'Other': 
                if 'x' in matchfound: draw = 'X'
                
        if draw == "X":
            x_found = True
        else:
            try:
                if int(draw) > int(best_yet): best_yet = draw    
            except Exception as e:
                # print ("exception encountered in regex_get_draw: ",e, " draw ", draw, type(draw), " best_yet ", best_yet, type(best_yet))
                best_yet = draw
    " Might not be concerned about the distinction with looting, rummaging and plain (no pun intended) drawing"
    # pattern = re.compile(regex_draw_modes['lootn_rummage_search'])  
    # matches = pattern.finditer(search_this)
    # for match in matches:
    #     startgrab = min(match.span())
    #     endgrab = max(match.span())

    pattern = re.compile(regex_draw_modes['draw_x_search'])
    matches = pattern.finditer(search_this)
    """Once you find 'X', there is no need to keep looking"""
    for match in matches:
        x_found = True
        break
    # if re.match(regex_draw_modes['draw_x_search'], search_this): x_found = True
        
    if best_yet == "": best_yet = 'Other'
    if x_found == True: best_yet = 'X'
    return best_yet

# def regex_get_target(search_this, card_type, keyword_list):  ## MOVED TO MTG_Main
def regex_get_triggered(search_this, keyword_list):
    """Called from Trigger_Search() - called if 'When/Whenever' found on the card
    Does some Regex searches to isolate when it triggers
    Parameters:   search_this:  ETB portion of the card's oracle text
                keyword_list:   to look for keyword triggered abilities, like Landfall and Heroic    
    Returns:  List 'list(filter_list)'  
    """
    trigger = ""
    triggered_keywords = {'landfall', 'persist', 'enrage', 'heroic', 'inspired', }
    keywords = mtg_main.rebuild_list(keyword_list)    
    for triggers in regex_triggered_modes:
        if re.findall(regex_triggered_modes[triggers], search_this, re.IGNORECASE):
            # print ("  :found ", triggers)
            trigger = trigger + triggers.capitalize() + " "
            
    for triggers in triggered_keywords:
        if triggers in keywords.lower(): trigger = trigger + triggers.capitalize() + " "
    if trigger == "": trigger = "Other"
    
    if trigger == "Other":
        if re.findall(regex_searchmode['cast'], search_this, re.IGNORECASE): trigger = "Cast "
    
    # print ("trigger your jigger?: ", trigger)
    return trigger

def regex_get_activated(search_this, keyword_list):
    """Called from Trigger_Search() - called if 'When/Whenever' found on the card
    Does some Regex searches to isolate when it triggers
    Parameters:   search_this:  ETB portion of the card's oracle text
                keyword_list:   to look for keyword triggered abilities, like Landfall and Heroic    
    Returns:  List 'list(filter_list)'  
    """
    activated = ""
    activated_keywords = {'equip', 'madness', 'enrage', 'heroic', 'inspired', 'forecast' }
    keywords = mtg_main.rebuild_list(keyword_list)    
    for modes in regex_activated_modes:        
        try:
            if re.findall(regex_activated_modes[modes], search_this, re.IGNORECASE):
                # print ("  :found ", modes)
                activated = activated + modes.capitalize() + " "
        except Exception as e:
            print ("except occurred at regex_get_activated: ", e)
            
    for kw in activated_keywords:
        if kw in keywords.lower(): activated = activated + kw.capitalize() + " "
    if activated == "": activated = "Other"
    
    # print ("activated?: ", activated)
    return activated

# def main():
#     # DEBUG_PRINTER = "TRUE"
#     # regex_get_keywords(regex_searchmode['keywordsearch'],longstring)
#     regex_get_mana_symbols("{1}{B}{2}{B}{B}{3}{B}{B}{1}{B}{B}{3}{B}{B}{2}{W}{B}{B}{B}{W}{B}{1}{W}{B}{3}{B}{B}{1}{B}{3}{R}{W}{B}{R}{2}{W}{B}{1}{W}{B}{B}{W}{B}{5}{R}{W}{B}{3}{B}{B}{1}{R}{R}{3}{B}{B}{B}{1}{B}{B}{2}{R}{2}{B}{2}{B}{B}{2}{B}{B}{B}{1}{B}{R}{W}{B}{B}{1}{B}{B}{B}{2}{B}{B}{B}{4}{W}{B}{B}{4}{B}{R}{R}{W}{R}{W}{B}{1}{B}{R}{2}{W}{4}{B}{W}{B}{B}")
# 
#     
# 
# 
#     print ("Regex shit")
# 
# if __name__ == '__main__': main()