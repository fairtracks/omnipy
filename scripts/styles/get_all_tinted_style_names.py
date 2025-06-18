# import asyncio
from collections import defaultdict

from inflection import underscore

import omnipy as om
from omnipy.data._display.styles.dynamic_styles import (_create_base_16_class_name_from_theme_key,
                                                        fetch_base16_theme)

om.runtime.config.data.http.for_host['raw.githubusercontent.com'].requests_per_time_period = 600


async def get_github_repo_urls(owner: str, repo: str, branch: str, path: str,
                               file_suffix: str) -> om.HttpUrlDataset:

    api_url = om.HttpUrlModel('https://api.github.com')
    api_url.path // 'repos' // owner // repo // 'contents' // path
    api_url.query['ref'] = branch

    url_pre = om.HttpUrlModel('https://raw.githubusercontent.com')
    url_pre.path // owner // repo // 'refs' // 'heads' // branch // path

    json_data = om.JsonListOfDictsDataset()
    await json_data.load(api_url)

    FileSuffixMatches = om.MatchItemsModel.adjust(
        'FileSuffixMatches', match_functions=(lambda x: x.endswith(file_suffix),))
    filtered_names = FileSuffixMatches(el['name'] for el in json_data[0])
    return om.HttpUrlDataset({name: url_pre + f'/{name}' for name in filtered_names})


async def get_all_tinted_themes() -> defaultdict[tuple[bool, str], list[str]]:
    # `pip install color-contrast` to run
    from color_contrast import AccessibilityLevel, check_contrast

    all_theme_urls = await get_github_repo_urls('tinted-theming',
                                                'schemes',
                                                'spec-0.11',
                                                'base16',
                                                '.yaml')

    all_themes = {name: await fetch_base16_theme(str(url)) for name, url in all_theme_urls.items()}

    themes_per_variant = defaultdict(list)
    for name, theme in all_themes.items():
        high_contrast = check_contrast(
            theme.palette.base05, theme.palette.base00, level=AccessibilityLevel.AA)
        themes_per_variant[(high_contrast, theme.variant)].append(name)

    return themes_per_variant


# themes_per_variant = asyncio.run(get_all_tinted_themes())
#
# print(themes_per_variant)
# Per Feb 23, 2025, the output of this script is:
themes_per_variant = {
    (True, 'dark'): [
        '3024.yaml',
        'apathy.yaml',
        'ashes.yaml',
        'atelier-cave.yaml',
        'atelier-dune.yaml',
        'atelier-estuary.yaml',
        'atelier-forest.yaml',
        'atelier-heath.yaml',
        'atelier-lakeside.yaml',
        'atelier-plateau.yaml',
        'atelier-savanna.yaml',
        'atelier-seaside.yaml',
        'atelier-sulphurpool.yaml',
        'atlas.yaml',
        'ayu-dark.yaml',
        'ayu-mirage.yaml',
        'aztec.yaml',
        'bespin.yaml',
        'black-metal-bathory.yaml',
        'black-metal-burzum.yaml',
        'black-metal-dark-funeral.yaml',
        'black-metal-gorgoroth.yaml',
        'black-metal-immortal.yaml',
        'black-metal-khold.yaml',
        'black-metal-marduk.yaml',
        'black-metal-mayhem.yaml',
        'black-metal-nile.yaml',
        'black-metal-venom.yaml',
        'black-metal.yaml',
        'blueforest.yaml',
        'blueish.yaml',
        'brewer.yaml',
        'bright.yaml',
        'caroline.yaml',
        'catppuccin-frappe.yaml',
        'catppuccin-macchiato.yaml',
        'catppuccin-mocha.yaml',
        'chalk.yaml',
        'circus.yaml',
        'classic-dark.yaml',
        'codeschool.yaml',
        'colors.yaml',
        'da-one-black.yaml',
        'da-one-gray.yaml',
        'da-one-ocean.yaml',
        'da-one-sea.yaml',
        'danqing.yaml',
        'darcula.yaml',
        'darkmoss.yaml',
        'darktooth.yaml',
        'darkviolet.yaml',
        'decaf.yaml',
        'deep-oceanic-next.yaml',
        'default-dark.yaml',
        'dracula.yaml',
        'edge-dark.yaml',
        'eighties.yaml',
        'embers.yaml',
        'equilibrium-dark.yaml',
        'equilibrium-gray-dark.yaml',
        'espresso.yaml',
        'evenok-dark.yaml',
        'everforest-dark-hard.yaml',
        'everforest.yaml',
        'flat.yaml',
        'framer.yaml',
        'gigavolt.yaml',
        'google-dark.yaml',
        'gotham.yaml',
        'grayscale-dark.yaml',
        'greenscreen.yaml',
        'gruber.yaml',
        'gruvbox-dark-hard.yaml',
        'gruvbox-dark-medium.yaml',
        'gruvbox-dark-pale.yaml',
        'gruvbox-dark-soft.yaml',
        'gruvbox-material-dark-hard.yaml',
        'gruvbox-material-dark-medium.yaml',
        'gruvbox-material-dark-soft.yaml',
        'hardcore.yaml',
        'harmonic16-dark.yaml',
        'heetch.yaml',
        'helios.yaml',
        'hopscotch.yaml',
        'horizon-dark.yaml',
        'horizon-terminal-dark.yaml',
        'humanoid-dark.yaml',
        'ia-dark.yaml',
        'irblack.yaml',
        'isotope.yaml',
        'jabuti.yaml',
        'kanagawa.yaml',
        'katy.yaml',
        'kimber.yaml',
        'macintosh.yaml',
        'marrakesh.yaml',
        'materia.yaml',
        'material-darker.yaml',
        'material-palenight.yaml',
        'material.yaml',
        'measured-dark.yaml',
        'mellow-purple.yaml',
        'mocha.yaml',
        'monokai.yaml',
        'moonlight.yaml',
        'mountain.yaml',
        'nebula.yaml',
        'nord.yaml',
        'nova.yaml',
        'ocean.yaml',
        'oceanicnext.yaml',
        'onedark-dark.yaml',
        'onedark.yaml',
        'outrun-dark.yaml',
        'oxocarbon-dark.yaml',
        'pandora.yaml',
        'paraiso.yaml',
        'pasque.yaml',
        'phd.yaml',
        'pinky.yaml',
        'pop.yaml',
        'porple.yaml',
        'precious-dark-eleven.yaml',
        'precious-dark-fifteen.yaml',
        'primer-dark-dimmed.yaml',
        'primer-dark.yaml',
        'purpledream.yaml',
        'qualia.yaml',
        'railscasts.yaml',
        'rebecca.yaml',
        'rose-pine-moon.yaml',
        'rose-pine.yaml',
        'saga.yaml',
        'sandcastle.yaml',
        'selenized-black.yaml',
        'selenized-dark.yaml',
        'seti.yaml',
        'shades-of-purple.yaml',
        'shadesmear-dark.yaml',
        'silk-dark.yaml',
        'snazzy.yaml',
        'solarflare.yaml',
        'solarized-dark.yaml',
        'spaceduck.yaml',
        'spacemacs.yaml',
        'sparky.yaml',
        'standardized-dark.yaml',
        'stella.yaml',
        'summerfruit-dark.yaml',
        'synth-midnight-dark.yaml',
        'tango.yaml',
        'tender.yaml',
        'terracotta-dark.yaml',
        'tokyo-city-dark.yaml',
        'tokyo-city-terminal-dark.yaml',
        'tokyo-night-dark.yaml',
        'tokyo-night-storm.yaml',
        'tokyodark-terminal.yaml',
        'tokyodark.yaml',
        'tomorrow-night-eighties.yaml',
        'tomorrow-night.yaml',
        'tube.yaml',
        'twilight.yaml',
        'unikitty-dark.yaml',
        'unikitty-reversible.yaml',
        'uwunicorn.yaml',
        'vesper.yaml',
        'vice.yaml',
        'windows-10.yaml',
        'windows-95.yaml',
        'windows-highcontrast.yaml',
        'windows-nt.yaml',
        'woodland.yaml',
        'xcode-dusk.yaml',
        'zenbones.yaml',
        'zenburn.yaml'
    ], (False, 'dark'): [
        'apprentice.yaml',
        'brogrammer.yaml',
        'brushtrees-dark.yaml',
        'eris.yaml',
        'eva-dim.yaml',
        'eva.yaml',
        'icy.yaml',
        'lime.yaml',
        'material-vivid.yaml',
        'papercolor-dark.yaml',
        'pico.yaml',
        'summercamp.yaml',
        'tarot.yaml',
        'tokyo-night-moon.yaml',
        'tokyo-night-terminal-dark.yaml',
        'tokyo-night-terminal-storm.yaml',
        'vulcan.yaml'
    ], (True, 'light'): [
        'atelier-cave-light.yaml',
        'atelier-dune-light.yaml',
        'atelier-estuary-light.yaml',
        'atelier-forest-light.yaml',
        'atelier-heath-light.yaml',
        'atelier-lakeside-light.yaml',
        'atelier-plateau-light.yaml',
        'atelier-savanna-light.yaml',
        'atelier-seaside-light.yaml',
        'atelier-sulphurpool-light.yaml',
        'ayu-light.yaml',
        'catppuccin-latte.yaml',
        'classic-light.yaml',
        'cupertino.yaml',
        'da-one-paper.yaml',
        'da-one-white.yaml',
        'danqing-light.yaml',
        'default-light.yaml',
        'dirtysea.yaml',
        'edge-light.yaml',
        'embers-light.yaml',
        'emil.yaml',
        'equilibrium-gray-light.yaml',
        'equilibrium-light.yaml',
        'fruit-soda.yaml',
        'github.yaml',
        'google-light.yaml',
        'grayscale-light.yaml',
        'gruvbox-light-hard.yaml',
        'gruvbox-light-medium.yaml',
        'gruvbox-light-soft.yaml',
        'gruvbox-material-light-hard.yaml',
        'gruvbox-material-light-medium.yaml',
        'gruvbox-material-light-soft.yaml',
        'harmonic16-light.yaml',
        'heetch-light.yaml',
        'horizon-light.yaml',
        'horizon-terminal-light.yaml',
        'humanoid-light.yaml',
        'ia-light.yaml',
        'measured-light.yaml',
        'mexico-light.yaml',
        'nord-light.yaml',
        'one-light.yaml',
        'oxocarbon-light.yaml',
        'papercolor-light.yaml',
        'precious-light-warm.yaml',
        'precious-light-white.yaml',
        'primer-light.yaml',
        'rose-pine-dawn.yaml',
        'sagelight.yaml',
        'sakura.yaml',
        'selenized-light.yaml',
        'selenized-white.yaml',
        'shadesmear-light.yaml',
        'shapeshifter.yaml',
        'silk-light.yaml',
        'solarflare-light.yaml',
        'solarized-light.yaml',
        'standardized-light.yaml',
        'still-alive.yaml',
        'summerfruit-light.yaml',
        'synth-midnight-light.yaml',
        'terracotta.yaml',
        'tokyo-city-light.yaml',
        'tokyo-city-terminal-light.yaml',
        'tokyo-night-light.yaml',
        'tokyo-night-terminal-light.yaml',
        'tomorrow.yaml',
        'unikitty-light.yaml',
        'windows-95-light.yaml',
        'windows-highcontrast-light.yaml'
    ], (False, 'light'): [
        'brushtrees.yaml',
        'cupcake.yaml',
        'material-lighter.yaml',
        'windows-10-light.yaml',
        'windows-nt-light.yaml'
    ]
}

pyproject_lines = []

for key, value in themes_per_variant.items():
    print(key)
    for theme_name in value:
        assert theme_name.endswith('.yaml')
        name = theme_name[:-5]
        pygments_theme_name = f'tb16-{name}'
        enum_constant = f'TB16_{underscore(name).upper()}'
        print(f"{enum_constant} = '{pygments_theme_name}'")
        pyproject_lines.append(f'"{pygments_theme_name}"'
                               f' = "omnipy.data._display.styles.dynamic_styles:'
                               f'{_create_base_16_class_name_from_theme_key(pygments_theme_name)}"')

for line in sorted(pyproject_lines):
    print(line)
