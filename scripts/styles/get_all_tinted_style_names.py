from collections import defaultdict
import re
from textwrap import dedent

from inflection import humanize

from omnipy import get_github_repo_urls
import omnipy as om
from omnipy.data._display.styles.dynamic_styles import (_create_base_16_class_name_from_theme_key,
                                                        fetch_base16_theme)
from omnipy.shared.constants import THEME_KEY_TINTED_BASE16_SUFFIX
from omnipy.util.literal_enum import LiteralEnumInnerTypes
from omnipy.util.literal_enum_generator import generate_literal_enum_code

om.runtime.config.data.http.for_host['raw.githubusercontent.com'].requests_per_time_period = 600

ThemesPerVariantType = dict[tuple[bool, str], list[tuple[str, str, str]]]


def get_all_tinted_themes() -> ThemesPerVariantType:
    # `pip install color-contrast` to run
    from color_contrast import AccessibilityLevel, check_contrast

    all_theme_urls = get_github_repo_urls.run('tinted-theming',
                                              'schemes',
                                              'spec-0.11',
                                              'base16',
                                              '.yaml')

    all_themes = {name: fetch_base16_theme(str(url)) for name, url in all_theme_urls.items()}

    themes_per_variant = defaultdict(list)
    for name, theme in all_themes.items():
        high_contrast = check_contrast(
            theme.palette.base05, theme.palette.base00, level=AccessibilityLevel.AA)
        themes_per_variant[(high_contrast, theme.variant)].append((name, theme.name, theme.author))

    return themes_per_variant


#
# themes_per_variant = get_all_tinted_themes()
#
# print(themes_per_variant)

# Per Jul 17, 2025, the output of this script is:
themes_per_variant: ThemesPerVariantType = {
    (True, 'dark'): [
        ('0x96f.yaml', '0x96f', 'Filip Janevski (https://0x96f.dev/theme)'),
        ('3024.yaml', '3024', 'Jan T. Sott (http://github.com/idleberg)'),
        ('apathy.yaml', 'Apathy', 'Jannik Siebert (https://github.com/janniks)'),
        ('ashes.yaml', 'Ashes', 'Jannik Siebert (https://github.com/janniks)'),
        ('atelier-cave.yaml', 'Atelier Cave', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-dune.yaml', 'Atelier Dune', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-estuary.yaml', 'Atelier Estuary', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-forest.yaml', 'Atelier Forest', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-heath.yaml', 'Atelier Heath', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-lakeside.yaml', 'Atelier Lakeside', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-plateau.yaml', 'Atelier Plateau', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-savanna.yaml', 'Atelier Savanna', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-seaside.yaml', 'Atelier Seaside', 'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-sulphurpool.yaml',
         'Atelier Sulphurpool',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atlas.yaml', 'Atlas', 'Alex Lende (https://ajlende.com)'),
        ('ayu-dark.yaml', 'Ayu Dark', 'Khue Nguyen <Z5483Y@gmail.com>'),
        ('ayu-mirage.yaml', 'Ayu Mirage', 'Khue Nguyen <Z5483Y@gmail.com>'),
        ('aztec.yaml', 'Aztec', 'TheNeverMan (github.com/TheNeverMan)'),
        ('bespin.yaml', 'Bespin', 'Jan T. Sott'),
        ('black-metal-bathory.yaml',
         'Black Metal (Bathory)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-burzum.yaml',
         'Black Metal (Burzum)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-dark-funeral.yaml',
         'Black Metal (Dark Funeral)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-gorgoroth.yaml',
         'Black Metal (Gorgoroth)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-immortal.yaml',
         'Black Metal (Immortal)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-khold.yaml',
         'Black Metal (Khold)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-marduk.yaml',
         'Black Metal (Marduk)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-mayhem.yaml',
         'Black Metal (Mayhem)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-nile.yaml', 'Black Metal (Nile)', 'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal-venom.yaml',
         'Black Metal (Venom)',
         'metalelf0 (https://github.com/metalelf0)'),
        ('black-metal.yaml', 'Black Metal', 'metalelf0 (https://github.com/metalelf0)'),
        ('blueforest.yaml', 'Blue Forest', 'alonsodomin (https://github.com/alonsodomin)'),
        ('blueish.yaml', 'Blueish', 'Ben Mayoras'),
        ('brewer.yaml', 'Brewer', 'Timothée Poisot (http://github.com/tpoisot)'),
        ('bright.yaml', 'Bright', 'Chris Kempson (http://chriskempson.com)'),
        ('caroline.yaml', 'caroline', 'ed (https://codeberg.org/ed)'),
        ('catppuccin-frappe.yaml', 'Catppuccin Frappe', 'https://github.com/catppuccin/catppuccin'),
        ('catppuccin-macchiato.yaml',
         'Catppuccin Macchiato',
         'https://github.com/catppuccin/catppuccin'),
        ('catppuccin-mocha.yaml', 'Catppuccin Mocha', 'https://github.com/catppuccin/catppuccin'),
        ('chalk.yaml', 'Chalk', 'Chris Kempson (http://chriskempson.com)'),
        ('chicago-night.yaml', 'Chicago Night', 'Wendell, Ryan <ryanjwendell@gmail.com>'),
        ('circus.yaml',
         'Circus',
         'Stephan Boyer (https://github.com/stepchowfun) and Esther Wang '
         '(https://github.com/ewang12)'),
        ('classic-dark.yaml', 'Classic Dark', 'Jason Heeris (http://heeris.id.au)'),
        ('codeschool.yaml', 'Codeschool', 'blockloop'),
        ('colors.yaml', 'Colors', 'mrmrs (http://clrs.cc)'),
        ('da-one-black.yaml', 'Da One Black', 'NNB (https://github.com/NNBnh)'),
        ('da-one-gray.yaml', 'Da One Gray', 'NNB (https://github.com/NNBnh)'),
        ('da-one-ocean.yaml', 'Da One Ocean', 'NNB (https://github.com/NNBnh)'),
        ('da-one-sea.yaml', 'Da One Sea', 'NNB (https://github.com/NNBnh)'),
        ('danqing.yaml', 'DanQing', 'Wenhan Zhu (Cosmos) (zhuwenhan950913@gmail.com)'),
        ('darcula.yaml', 'Darcula', 'jetbrains'),
        ('darkmoss.yaml', 'darkmoss', 'Gabriel Avanzi (https://github.com/avanzzzi)'),
        ('darktooth.yaml', 'Darktooth', 'Jason Milkins (https://github.com/jasonm23)'),
        ('darkviolet.yaml',
         'Dark Violet',
         'ruler501 (https://github.com/ruler501/base16-darkviolet)'),
        ('decaf.yaml', 'Decaf', 'Alex Mirrington (https://github.com/alexmirrington)'),
        ('deep-oceanic-next.yaml', 'Deep Oceanic Next', 'spearkkk (https://github.com/spearkkk)'),
        ('default-dark.yaml', 'Default Dark', 'Chris Kempson (http://chriskempson.com)'),
        ('digital-rain.yaml', 'Digital Rain', 'Nathan Byrd (https://github.com/cognitivegears)'),
        ('dracula.yaml',
         'Dracula',
         'Jamy Golden (http://github.com/JamyGolden), based on Dracula Theme '
         '(http://github.com/dracula)'),
        ('edge-dark.yaml', 'Edge Dark', 'cjayross (https://github.com/cjayross)'),
        ('eighties.yaml', 'Eighties', 'Chris Kempson (http://chriskempson.com)'),
        ('embers.yaml', 'Embers', 'Jannik Siebert (https://github.com/janniks)'),
        ('equilibrium-dark.yaml', 'Equilibrium Dark', 'Carlo Abelli'),
        ('equilibrium-gray-dark.yaml', 'Equilibrium Gray Dark', 'Carlo Abelli'),
        ('espresso.yaml',
         'Espresso',
         'Unknown. Maintained by Alex Mirrington (https://github.com/alexmirrington)'),
        ('evenok-dark.yaml', 'Evenok Dark', 'Mekeor Melire'),
        ('everforest-dark-hard.yaml',
         'Everforest Dark Hard',
         'Sainnhe Park (https://github.com/sainnhe)'),
        ('everforest-dark-soft.yaml',
         'Everforest Dark Soft',
         'Sainnhe Park (https://github.com/sainnhe)'),
        ('everforest.yaml', 'Everforest', 'Sainnhe Park (https://github.com/sainnhe)'),
        ('flat.yaml', 'Flat', 'Chris Kempson (http://chriskempson.com)'),
        ('framer.yaml', 'Framer', 'Framer (Maintained by Jesse Hoyos)'),
        ('gigavolt.yaml', 'Gigavolt', 'Aidan Swope (http://github.com/Whillikers)'),
        ('github-dark.yaml', 'Github Dark', 'Tinted Theming (https://github.com/tinted-theming)'),
        ('google-dark.yaml', 'Google Dark', 'Seth Wright (http://sethawright.com)'),
        ('gotham.yaml', 'Gotham', 'Andrea Leopardi (arranged by Brett Jones)'),
        ('grayscale-dark.yaml', 'Grayscale Dark', 'Alexandre Gavioli (https://github.com/Alexx2/)'),
        ('greenscreen.yaml', 'Green Screen', 'Chris Kempson (http://chriskempson.com)'),
        ('gruber.yaml',
         'Gruber',
         'Patel, Nimai <nimai.m.patel@gmail.com>, colors from '
         'www.github.com/rexim/gruber-darker-theme'),
        ('gruvbox-dark-hard.yaml',
         'Gruvbox dark, hard',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-dark-medium.yaml',
         'Gruvbox dark, medium',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-dark-pale.yaml',
         'Gruvbox dark, pale',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-dark-soft.yaml',
         'Gruvbox dark, soft',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-dark.yaml',
         'Gruvbox dark',
         'Tinted Theming (https://github.com/tinted-theming), morhetz '
         '(https://github.com/morhetz/gruvbox)'),
        ('gruvbox-material-dark-hard.yaml',
         'Gruvbox Material Dark, Hard',
         'Mayush Kumar (https://github.com/MayushKumar), sainnhe '
         '(https://github.com/sainnhe/gruvbox-material-vscode)'),
        ('gruvbox-material-dark-medium.yaml',
         'Gruvbox Material Dark, Medium',
         'Mayush Kumar (https://github.com/MayushKumar), sainnhe '
         '(https://github.com/sainnhe/gruvbox-material-vscode)'),
        ('gruvbox-material-dark-soft.yaml',
         'Gruvbox Material Dark, Soft',
         'Mayush Kumar (https://github.com/MayushKumar), sainnhe '
         '(https://github.com/sainnhe/gruvbox-material-vscode)'),
        ('hardcore.yaml', 'Hardcore', 'Chris Caller'),
        ('harmonic16-dark.yaml', 'Harmonic16 Dark', 'Jannik Siebert (https://github.com/janniks)'),
        ('heetch.yaml', 'Heetch Dark', 'Geoffrey Teale (tealeg@gmail.com)'),
        ('helios.yaml', 'Helios', 'Alex Meyer (https://github.com/reyemxela)'),
        ('hopscotch.yaml', 'Hopscotch', 'Jan T. Sott'),
        ('horizon-dark.yaml', 'Horizon Dark', 'Michaël Ball (http://github.com/michael-ball/)'),
        ('horizon-terminal-dark.yaml',
         'Horizon Terminal Dark',
         'Michaël Ball (http://github.com/michael-ball/)'),
        ('humanoid-dark.yaml', 'Humanoid dark', 'Thomas (tasmo) Friese'),
        ('ia-dark.yaml', 'iA Dark', 'iA Inc. (modified by aramisgithub)'),
        ('irblack.yaml', 'IR Black', 'Timothée Poisot (http://timotheepoisot.fr)'),
        ('isotope.yaml', 'Isotope', 'Jan T. Sott'),
        ('jabuti.yaml', 'Jabuti', 'https://github.com/notusknot'),
        ('kanagawa-dragon.yaml', 'Kanagawa Dragon',
         'Tommaso Laurenzi (https://github.com/rebelot)'),
        ('kanagawa.yaml', 'Kanagawa', 'Tommaso Laurenzi (https://github.com/rebelot)'),
        ('katy.yaml', 'Katy', 'George Essig (https://github.com/gessig)'),
        ('kimber.yaml', 'Kimber', 'Mishka Nguyen (https://github.com/akhsiM)'),
        ('macintosh.yaml', 'Macintosh', 'Rebecca Bettencourt (http://www.kreativekorp.com)'),
        ('marrakesh.yaml', 'Marrakesh', 'Alexandre Gavioli (http://github.com/Alexx2/)'),
        ('materia.yaml', 'Materia', 'Defman21'),
        ('material-darker.yaml', 'Material Darker', 'Nate Peterson'),
        ('material-palenight.yaml', 'Material Palenight', 'Nate Peterson'),
        ('material.yaml', 'Material', 'Nate Peterson'),
        ('measured-dark.yaml', 'Measured Dark', 'Measured (https://measured.co)'),
        ('mellow-purple.yaml', 'Mellow Purple', 'gidsi'),
        ('mocha.yaml', 'Mocha', 'Chris Kempson (http://chriskempson.com)'),
        ('monokai.yaml', 'Monokai', 'Wimer Hazenberg (http://www.monokai.nl)'),
        ('moonlight.yaml', 'Moonlight', 'Jeremy Swinarton (https://github.com/jswinarton)'),
        ('mountain.yaml', 'Mountain', 'gnsfujiwara (https://github.com/gnsfujiwara)'),
        ('nebula.yaml', 'Nebula', 'Gabriel Fontes (https://github.com/Misterio77)'),
        ('nord.yaml', 'Nord', 'arcticicestudio'),
        ('nova.yaml',
         'Nova',
         'George Essig (https://github.com/gessig), Trevor D. Miller (https://trevordmiller.com)'),
        ('ocean.yaml', 'Ocean', 'Chris Kempson (http://chriskempson.com)'),
        ('oceanicnext.yaml',
         'OceanicNext',
         'https://github.com/voronianski/oceanic-next-color-scheme'),
        ('onedark-dark.yaml', 'OneDark Dark', 'olimorris (https://github.com/olimorris)'),
        ('onedark.yaml', 'OneDark', 'Lalit Magant (http://github.com/tilal6991)'),
        ('outrun-dark.yaml', 'Outrun Dark', 'Hugo Delahousse (http://github.com/hugodelahousse/)'),
        ('oxocarbon-dark.yaml', 'Oxocarbon Dark', 'shaunsingh/IBM'),
        ('pandora.yaml', 'pandora', 'Cassandra Fox'),
        ('paraiso.yaml', 'Paraiso', 'Jan T. Sott'),
        ('pasque.yaml', 'Pasque', 'Gabriel Fontes (https://github.com/Misterio77)'),
        ('penumbra-dark-contrast-plus-plus.yaml',
         'Penumbra Dark Contrast Plus Plus',
         'Zachary Weiss (https://github.com/zacharyweiss)'),
        ('penumbra-dark-contrast-plus.yaml',
         'Penumbra Dark Contrast Plus',
         'Zachary Weiss (https://github.com/zacharyweiss)'),
        ('penumbra-dark.yaml', 'Penumbra Dark', 'Zachary Weiss (https://github.com/zacharyweiss)'),
        ('phd.yaml', 'PhD', 'Hennig Hasemann (http://leetless.de/vim.html)'),
        ('pinky.yaml', 'pinky', 'Benjamin (https://github.com/b3nj5m1n)'),
        ('pop.yaml', 'Pop', 'Chris Kempson (http://chriskempson.com)'),
        ('porple.yaml', 'Porple', 'Niek den Breeje (https://github.com/AuditeMarlow)'),
        ('precious-dark-eleven.yaml', 'Precious Dark Eleven', '4lex4 <4lex49@zoho.com>'),
        ('precious-dark-fifteen.yaml', 'Precious Dark Fifteen', '4lex4 <4lex49@zoho.com>'),
        ('primer-dark-dimmed.yaml', 'Primer Dark Dimmed', 'Jimmy Lin'),
        ('primer-dark.yaml', 'Primer Dark', 'Jimmy Lin'),
        ('purpledream.yaml', 'Purpledream', 'malet'),
        ('qualia.yaml', 'Qualia', 'isaacwhanson'),
        ('railscasts.yaml', 'Railscasts', 'Ryan Bates (http://railscasts.com)'),
        ('rebecca.yaml',
         'Rebecca',
         'Victor Borja (http://github.com/vic) based on Rebecca Theme '
         '(http://github.com/vic/rebecca-theme)'),
        ('rose-pine-moon.yaml', 'Rosé Pine Moon', 'Emilia Dunfelt <edun@dunfelt.se>'),
        ('rose-pine.yaml', 'Rosé Pine', 'Emilia Dunfelt <edun@dunfelt.se>'),
        ('saga.yaml', 'SAGA', 'https://github.com/SAGAtheme/SAGA'),
        ('sandcastle.yaml', 'Sandcastle', 'George Essig (https://github.com/gessig)'),
        ('selenized-black.yaml',
         'selenized-black',
         'Jan Warchol (https://github.com/jan-warchol/selenized) / adapted to base16 by ali'),
        ('selenized-dark.yaml',
         'selenized-dark',
         'Jan Warchol (https://github.com/jan-warchol/selenized) / adapted to base16 by ali'),
        ('seti.yaml', 'Seti UI', ''),
        ('shades-of-purple.yaml',
         'Shades of Purple',
         'Iolar Demartini Junior (http://github.com/demartini), based on Shades of Purple Theme '
         '(https://github.com/ahmadawais/shades-of-purple-vscode)'),
        ('shadesmear-dark.yaml', 'ShadeSmear Dark', 'Kyle Giammarco (http://kyle.giammar.co)'),
        ('silk-dark.yaml', 'Silk Dark', 'Gabriel Fontes (https://github.com/Misterio77)'),
        ('snazzy.yaml',
         'Snazzy',
         'Chawye Hsu (https://github.com/chawyehsu), based on Hyper Snazzy Theme '
         '(https://github.com/sindresorhus/hyper-snazzy)'),
        ('solarflare.yaml', 'Solar Flare', 'Chuck Harmston (https://chuck.harmston.ch)'),
        ('solarized-dark.yaml', 'Solarized Dark', 'Ethan Schoonover (modified by aramisgithub)'),
        ('spaceduck.yaml',
         'Spaceduck',
         'Guillermo Rodriguez (https://github.com/pineapplegiant), packaged by Gabriel Fontes '
         '(https://github.com/Misterio77)'),
        ('spacemacs.yaml',
         'Spacemacs',
         'Nasser Alshammari (https://github.com/nashamri/spacemacs-theme)'),
        ('sparky.yaml', 'Sparky', 'Leila Sother (https://github.com/mixcoac)'),
        ('standardized-dark.yaml',
         'standardized-dark',
         'ali (https://github.com/ali-githb/base16-standardized-scheme)'),
        ('stella.yaml', 'Stella', 'Shrimpram'),
        ('summerfruit-dark.yaml', 'Summerfruit Dark', 'Christopher Corley (http://christop.club/)'),
        ('synth-midnight-dark.yaml',
         'Synth Midnight Terminal Dark',
         'Michaël Ball (http://github.com/michael-ball/)'),
        ('tango.yaml', 'Tango', '@Schnouki, based on the Tango Desktop Project'),
        ('tender.yaml', 'tender', 'Jacobo Tabernero (https://github/com/jacoborus/tender.vim)'),
        ('terracotta-dark.yaml',
         'Terracotta Dark',
         'Alexander Rossell Hayes (https://github.com/rossellhayes)'),
        ('tokyo-city-dark.yaml', 'Tokyo City Dark', 'Michaël Ball'),
        ('tokyo-city-terminal-dark.yaml', 'Tokyo City Terminal Dark', 'Michaël Ball'),
        ('tokyo-night-dark.yaml', 'Tokyo Night Dark', 'Michaël Ball'),
        ('tokyo-night-storm.yaml', 'Tokyo Night Storm', 'Michaël Ball'),
        ('tokyodark-terminal.yaml', 'Tokyodark Terminal',
         'Tiagovla (https://github.com/tiagovla/)'),
        ('tokyodark.yaml',
         'Tokyodark',
         'Jamy Golden (https://github.com/JamyGolden), Based on Tokyodark.nvim '
         '(https://github.com/tiagovla/tokyodark.nvim)'),
        ('tomorrow-night-eighties.yaml',
         'Tomorrow Night Eighties',
         'Chris Kempson (http://chriskempson.com)'),
        ('tomorrow-night.yaml', 'Tomorrow Night', 'Chris Kempson (http://chriskempson.com)'),
        ('tube.yaml', 'London Tube', 'Jan T. Sott'),
        ('twilight.yaml', 'Twilight', 'David Hart (https://github.com/hartbit)'),
        ('unikitty-dark.yaml', 'Unikitty Dark', 'Josh W Lewis (@joshwlewis)'),
        ('unikitty-reversible.yaml', 'Unikitty Reversible', 'Josh W Lewis (@joshwlewis)'),
        ('uwunicorn.yaml',
         'UwUnicorn',
         'Fernando Marques (https://github.com/RakkiUwU) and Gabriel Fontes '
         '(https://github.com/Misterio77)'),
        ('valua.yaml', 'Valua', 'Nonetrix (https://github.com/nonetrix)'),
        ('vesper.yaml', 'Vesper', 'FormalSnake (https://github.com/formalsnake)'),
        ('vice.yaml', 'vice', 'Thomas Leon Highbaugh thighbaugh@zoho.com'),
        ('windows-10.yaml', 'Windows 10', 'Fergus Collins (https://github.com/ferguscollins)'),
        ('windows-95.yaml', 'Windows 95', 'Fergus Collins (https://github.com/ferguscollins)'),
        ('windows-highcontrast.yaml',
         'Windows High Contrast',
         'Fergus Collins (https://github.com/ferguscollins)'),
        ('windows-nt.yaml', 'Windows NT', 'Fergus Collins (https://github.com/ferguscollins)'),
        ('woodland.yaml', 'Woodland', 'Jay Cornwall (https://jcornwall.com)'),
        ('xcode-dusk.yaml', 'XCode Dusk', 'Elsa Gonsiorowski (https://github.com/gonsie)'),
        ('zenbones.yaml', 'Zenbones', 'mcchrish'),
        ('zenburn.yaml', 'Zenburn', 'elnawe'),
    ], (False, 'dark'): [
        ('apprentice.yaml', 'Apprentice', 'romainl'),
        ('brogrammer.yaml', 'Brogrammer', 'Vik Ramanujam (http://github.com/piggyslasher)'),
        ('brushtrees-dark.yaml', 'Brush Trees Dark', 'Abraham White <abelincoln.white@gmail.com>'),
        ('eris.yaml', 'eris', 'ed (https://codeberg.org/ed)'),
        ('eva-dim.yaml', 'Eva Dim', 'kjakapat (https://github.com/kjakapat)'),
        ('eva.yaml', 'Eva', 'kjakapat (https://github.com/kjakapat)'),
        ('icy.yaml', 'Icy Dark', 'icyphox (https://icyphox.ga)'),
        ('lime.yaml', 'lime', 'limelier'),
        ('material-vivid.yaml', 'Material Vivid', 'joshyrobot'),
        ('papercolor-dark.yaml',
         'PaperColor Dark',
         'Jon Leopard (http://github.com/jonleopard), based on PaperColor Theme '
         '(https://github.com/NLKNguyen/papercolor-theme)'),
        ('pico.yaml', 'Pico', 'PICO-8 (http://www.lexaloffle.com/pico-8.php)'),
        ('summercamp.yaml', 'summercamp', 'zoe firi (zoefiri.github.io)'),
        ('tarot.yaml', 'tarot', 'ed (https://codeberg.org/ed)'),
        ('tokyo-night-moon.yaml', 'Tokyo Night Moon', 'Ólafur Bjarki Bogason'),
        ('tokyo-night-terminal-dark.yaml', 'Tokyo Night Terminal Dark', 'Michaël Ball'),
        ('tokyo-night-terminal-storm.yaml', 'Tokyo Night Terminal Storm', 'Michaël Ball'),
        ('vulcan.yaml', 'vulcan', 'Andrey Varfolomeev'),
    ], (True, 'light'): [
        ('atelier-cave-light.yaml',
         'Atelier Cave Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-dune-light.yaml',
         'Atelier Dune Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-estuary-light.yaml',
         'Atelier Estuary Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-forest-light.yaml',
         'Atelier Forest Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-heath-light.yaml',
         'Atelier Heath Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-lakeside-light.yaml',
         'Atelier Lakeside Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-plateau-light.yaml',
         'Atelier Plateau Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-savanna-light.yaml',
         'Atelier Savanna Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-seaside-light.yaml',
         'Atelier Seaside Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('atelier-sulphurpool-light.yaml',
         'Atelier Sulphurpool Light',
         'Bram de Haan (http://atelierbramdehaan.nl)'),
        ('ayu-light.yaml', 'Ayu Light', 'Khue Nguyen <Z5483Y@gmail.com>'),
        ('catppuccin-latte.yaml', 'Catppuccin Latte', 'https://github.com/catppuccin/catppuccin'),
        ('chicago-day.yaml', 'Chicago Day', 'Wendell, Ryan <ryanjwendell@gmail.com>'),
        ('classic-light.yaml', 'Classic Light', 'Jason Heeris (http://heeris.id.au)'),
        ('cupertino.yaml', 'Cupertino', 'Defman21'),
        ('da-one-paper.yaml', 'Da One Paper', 'NNB (https://github.com/NNBnh)'),
        ('da-one-white.yaml', 'Da One White', 'NNB (https://github.com/NNBnh)'),
        ('danqing-light.yaml', 'DanQing Light', 'Wenhan Zhu (Cosmos) (zhuwenhan950913@gmail.com)'),
        ('default-light.yaml', 'Default Light', 'Chris Kempson (http://chriskempson.com)'),
        ('dirtysea.yaml', 'dirtysea', 'Kahlil (Kal) Hodgson'),
        ('edge-light.yaml', 'Edge Light', 'cjayross (https://github.com/cjayross)'),
        ('embers-light.yaml', 'Embers Light', 'Jannik Siebert (https://github.com/janniks)'),
        ('emil.yaml', 'emil', 'limelier'),
        ('equilibrium-gray-light.yaml', 'Equilibrium Gray Light', 'Carlo Abelli'),
        ('equilibrium-light.yaml', 'Equilibrium Light', 'Carlo Abelli'),
        ('fruit-soda.yaml', 'Fruit Soda', 'jozip'),
        ('github.yaml', 'Github', 'Tinted Theming (https://github.com/tinted-theming)'),
        ('google-light.yaml', 'Google Light', 'Seth Wright (http://sethawright.com)'),
        ('grayscale-light.yaml',
         'Grayscale Light',
         'Alexandre Gavioli (https://github.com/Alexx2/)'),
        ('gruvbox-light-hard.yaml',
         'Gruvbox light, hard',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-light-medium.yaml',
         'Gruvbox light, medium',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-light-soft.yaml',
         'Gruvbox light, soft',
         'Dawid Kurek (dawikur@gmail.com), morhetz (https://github.com/morhetz/gruvbox)'),
        ('gruvbox-light.yaml',
         'Gruvbox Light',
         'Tinted Theming (https://github.com/tinted-theming), morhetz '
         '(https://github.com/morhetz/gruvbox)'),
        ('gruvbox-material-light-hard.yaml',
         'Gruvbox Material Light, Hard',
         'Mayush Kumar (https://github.com/MayushKumar), sainnhe '
         '(https://github.com/sainnhe/gruvbox-material-vscode)'),
        ('gruvbox-material-light-medium.yaml',
         'Gruvbox Material Light, Medium',
         'Mayush Kumar (https://github.com/MayushKumar), sainnhe '
         '(https://github.com/sainnhe/gruvbox-material-vscode)'),
        ('gruvbox-material-light-soft.yaml',
         'Gruvbox Material Light, Soft',
         'Mayush Kumar (https://github.com/MayushKumar), sainnhe '
         '(https://github.com/sainnhe/gruvbox-material-vscode)'),
        ('harmonic16-light.yaml', 'Harmonic16 Light',
         'Jannik Siebert (https://github.com/janniks)'),
        ('heetch-light.yaml', 'Heetch Light', 'Geoffrey Teale (tealeg@gmail.com)'),
        ('horizon-light.yaml', 'Horizon Light', 'Michaël Ball (http://github.com/michael-ball/)'),
        ('horizon-terminal-light.yaml',
         'Horizon Terminal Light',
         'Michaël Ball (http://github.com/michael-ball/)'),
        ('humanoid-light.yaml', 'Humanoid light', 'Thomas (tasmo) Friese'),
        ('ia-light.yaml', 'iA Light', 'iA Inc. (modified by aramisgithub)'),
        ('measured-light.yaml', 'Measured Light', 'Measured (https://measured.co)'),
        ('mexico-light.yaml', 'Mexico Light', 'Sheldon Johnson'),
        ('nord-light.yaml',
         'Nord Light',
         "threddast, based on fuxialexander's doom-nord-light-theme (Doom Emacs)"),
        ('one-light.yaml', 'One Light', 'Daniel Pfeifer (http://github.com/purpleKarrot)'),
        ('oxocarbon-light.yaml', 'Oxocarbon Light', 'shaunsingh/IBM'),
        ('papercolor-light.yaml',
         'PaperColor Light',
         'Jon Leopard (http://github.com/jonleopard), based on PaperColor Theme '
         '(https://github.com/NLKNguyen/papercolor-theme)'),
        ('penumbra-light-contrast-plus-plus.yaml',
         'Penumbra Light Contrast Plus Plus',
         'Zachary Weiss (https://github.com/zacharyweiss)'),
        ('penumbra-light-contrast-plus.yaml',
         'Penumbra Light Contrast Plus',
         'Zachary Weiss (https://github.com/zacharyweiss)'),
        ('penumbra-light.yaml', 'Penumbra Light',
         'Zachary Weiss (https://github.com/zacharyweiss)'),
        ('precious-light-warm.yaml', 'Precious Light Warm', '4lex4 <4lex49@zoho.com>'),
        ('precious-light-white.yaml', 'Precious Light White', '4lex4 <4lex49@zoho.com>'),
        ('primer-light.yaml', 'Primer Light', 'Jimmy Lin'),
        ('rose-pine-dawn.yaml', 'Rosé Pine Dawn', 'Emilia Dunfelt <edun@dunfelt.se>'),
        ('sagelight.yaml', 'Sagelight', 'Carter Veldhuizen'),
        ('sakura.yaml', 'Sakura', 'Misterio77 (http://github.com/Misterio77)'),
        ('selenized-light.yaml',
         'selenized-light',
         'Jan Warchol (https://github.com/jan-warchol/selenized) / adapted to base16 by ali'),
        ('selenized-white.yaml',
         'selenized-white',
         'Jan Warchol (https://github.com/jan-warchol/selenized) / adapted to base16 by ali'),
        ('shadesmear-light.yaml', 'ShadeSmear Light', 'Kyle Giammarco (http://kyle.giammar.co)'),
        ('shapeshifter.yaml', 'Shapeshifter', 'Tyler Benziger (http://tybenz.com)'),
        ('silk-light.yaml', 'Silk Light', 'Gabriel Fontes (https://github.com/Misterio77)'),
        ('solarflare-light.yaml', 'Solar Flare Light',
         'Chuck Harmston (https://chuck.harmston.ch)'),
        ('solarized-light.yaml', 'Solarized Light', 'Ethan Schoonover (modified by aramisgithub)'),
        ('standardized-light.yaml',
         'standardized-light',
         'ali (https://github.com/ali-githb/base16-standardized-scheme)'),
        ('still-alive.yaml', 'Still Alive', 'Derrick McKee (derrick.mckee@gmail.com)'),
        ('summerfruit-light.yaml',
         'Summerfruit Light',
         'Christopher Corley (http://christop.club/)'),
        ('synth-midnight-light.yaml',
         'Synth Midnight Terminal Light',
         'Michaël Ball (http://github.com/michael-ball/)'),
        ('terracotta.yaml',
         'Terracotta',
         'Alexander Rossell Hayes (https://github.com/rossellhayes)'),
        ('tokyo-city-light.yaml', 'Tokyo City Light', 'Michaël Ball'),
        ('tokyo-city-terminal-light.yaml', 'Tokyo City Terminal Light', 'Michaël Ball'),
        ('tokyo-night-light.yaml', 'Tokyo Night Light', 'Michaël Ball'),
        ('tokyo-night-terminal-light.yaml', 'Tokyo Night Terminal Light', 'Michaël Ball'),
        ('tomorrow.yaml', 'Tomorrow', 'Chris Kempson (http://chriskempson.com)'),
        ('unikitty-light.yaml', 'Unikitty Light', 'Josh W Lewis (@joshwlewis)'),
        ('windows-95-light.yaml',
         'Windows 95 Light',
         'Fergus Collins (https://github.com/ferguscollins)'),
        ('windows-highcontrast-light.yaml',
         'Windows High Contrast Light',
         'Fergus Collins (https://github.com/ferguscollins)'),
    ], (False, 'light'): [
        ('brushtrees.yaml', 'Brush Trees', 'Abraham White <abelincoln.white@gmail.com>'),
        ('cupcake.yaml', 'Cupcake', 'Chris Kempson (http://chriskempson.com)'),
        ('material-lighter.yaml', 'Material Lighter', 'Nate Peterson'),
        ('windows-10-light.yaml',
         'Windows 10 Light',
         'Fergus Collins (https://github.com/ferguscollins)'),
        ('windows-nt-light.yaml',
         'Windows NT Light',
         'Fergus Collins (https://github.com/ferguscollins)'),
    ]
}


def create_pygments_theme_name(name: str) -> str:
    return f'{name}{THEME_KEY_TINTED_BASE16_SUFFIX}'.lower()


def create_literal_enum_class_name(high_contrast: bool, variant_name: str) -> str:
    contrast_part = 'High' if high_contrast else 'Low'
    return f'{humanize(variant_name)}{contrast_part}ContrastTintedThemingBase16ColorStyles'


AUTHOR_PATTERN = re.compile(r'\s*[<\(].*[>\)]|\S+@\S+\.\S+')


def generate_author_text(author: str) -> str:
    if author.startswith('http'):
        return ''
    return f''' by "{re.sub(AUTHOR_PATTERN, '', author).strip()}"'''


def create_pyproject_code_from_themes_per_variant(themes_per_variant: ThemesPerVariantType) -> str:

    pyproject_lines = []

    for key, value in themes_per_variant.items():
        for theme_name, _fullname, _author in value:
            assert theme_name.endswith('.yaml')
            name = theme_name[:-5]
            pygments_theme_name = create_pygments_theme_name(name)
            pyproject_lines.append(
                f'"{pygments_theme_name}"'
                f' = "omnipy.data._display.styles.dynamic_styles:'
                f'{_create_base_16_class_name_from_theme_key(pygments_theme_name)}"')

    return '\n'.join(sorted(pyproject_lines))


def create_literal_enum_from_variant_and_themes(
    first: bool,
    variant: tuple[bool, str],
    themes: list[tuple[str, str, str]],
) -> str:

    HIGH_LEVEL_TEXT = 'high-level contrast that conforms to'
    LOWER_LEVEL_TEXT = 'lower-level contrast that did not meet'
    DOCSTRING_TEMPLATE_1 = '{fullname}: Base-16 color style{author_text}.'
    DOCSTRING_TEMPLATE_2 = dedent("""\
        Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
        Automatically downloaded by Omnipy when needed (locally cached).""")
    DOCSTRING_TEMPLATE_3 = dedent("""\
        This style is a {variant} variant, with {contrast_text} the AA criteria of the
        Web Content Accessibility Guidelines (WCAG) 2.1 (https://www.w3.org/TR/WCAG21/).""")

    high_contrast: bool = variant[0]
    variant_name: str = variant[1]

    theme_names = []
    docstrings: dict[LiteralEnumInnerTypes, tuple[str, ...]] = {}

    for name, fullname, author in sorted(themes):
        assert name.endswith('.yaml')

        theme_name = create_pygments_theme_name(name[:-5])
        theme_names.append(theme_name)

        docstring_1 = DOCSTRING_TEMPLATE_1.format(
            fullname=fullname,
            author_text=generate_author_text(author),
        )
        docstring_3 = DOCSTRING_TEMPLATE_3.format(
            variant=variant_name,
            contrast_text=HIGH_LEVEL_TEXT if high_contrast else LOWER_LEVEL_TEXT,
        )
        docstrings[theme_name] = (docstring_1, DOCSTRING_TEMPLATE_2, docstring_3)

    class_name = create_literal_enum_class_name(high_contrast, variant_name)

    return generate_literal_enum_code(
        theme_names,
        docstrings=docstrings,
        include_imports=first,
        class_name=class_name,
    )


def generate_all_code(themes_per_variant: ThemesPerVariantType) -> None:
    print('AUTHORS CHECK')
    print('=============\n')
    for _, themes in themes_per_variant.items():
        for _, _, author in themes:
            print(generate_author_text(author))

    print('\n\n\nPYPROJECT CODE')
    print('==============\n')
    print(create_pyproject_code_from_themes_per_variant(themes_per_variant))

    print('\n\n\nLITERAL_ENUM CODE')
    print('=================\n')

    for i, (variant, themes) in enumerate(themes_per_variant.items()):
        print(create_literal_enum_from_variant_and_themes(i == 0, variant, themes))


generate_all_code(themes_per_variant)
