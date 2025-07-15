import os
from textwrap import dedent
from typing import Iterable
import webbrowser

# Adapted from https://github.com/python/cpython/pull/130535, dual licensed under the PSF
# License Version 2 and the Zero-Clause BSD license.


class OmnipyMacOSXOSAScript(webbrowser.BaseBrowser):
    def __init__(self, name='default'):
        super().__init__(name)

    _OSASCRIPT_TEMPLATE = dedent("""
        tell application "System Events"
            if not (get name of every process) contains "{browser}" then
                do shell script "open -a \\"{browser}\\""
                with timeout of 10 seconds
                    repeat until exists (first process whose name contains "{browser}")
                        delay 0.1
                    end repeat
                end timeout
                tell {type} "{browser}"
                    activate
                    {open_url_cmds}
                end tell
            else
                tell {type} "{browser}"
                    activate
                    {pre_cmd_1}
                    {pre_cmd_2}
                    {open_url_cmds}
                end tell
            end if
            if not (process "{browser}" is frontmost) then
                do shell script "open -a \\"{browser}\\""
                -- with timeout of 10 seconds
                    repeat until process "{browser}" is frontmost
                        delay 0.1
                    end repeat
                -- end timeout
            end if
        end tell
    """)

    @classmethod
    def _handle_url(cls, url: str | Iterable[str]) -> str:

        if isinstance(url, str):
            urls = [url]
        else:
            urls = list(url)

        cmds = []
        for url in urls:
            url = url.replace('"', '%22')
            cmds.append(f'open location "{url}"')

        return '\n'.join(cmds)

    @classmethod
    def _safari_script(cls, url: str, new: int = 0) -> str:
        return cls._OSASCRIPT_TEMPLATE.format(
            type='application',
            browser='Safari',
            pre_cmd_1=('make new document'
                       if new == 1 else 'tell front window to set current tab to (make new tab)'),
            pre_cmd_2='',
            open_url_cmds=cls._handle_url(url),
        )

    @classmethod
    def _chrome_script(cls, url: str, new: int = 0) -> str:
        return cls._OSASCRIPT_TEMPLATE.format(
            type='application',
            browser='Google Chrome',
            pre_cmd_1='make new window' if new == 1 else '',
            pre_cmd_2='',
            open_url_cmds=cls._handle_url(url),
        )

    @classmethod
    def _brave_script(cls, url: str, new: int = 0) -> str:
        return cls._OSASCRIPT_TEMPLATE.format(
            type='application',
            browser='Brave Browser',
            pre_cmd_1='make new window' if new == 1 else '',
            pre_cmd_2='',
            open_url_cmds=cls._handle_url(url),
        )

    @classmethod
    def _edge_script(cls, url: str, new: int = 0) -> str:
        return cls._OSASCRIPT_TEMPLATE.format(
            type='application',
            browser='Microsoft Edge',
            pre_cmd_1='make new window' if new == 1 else '',
            pre_cmd_2='',
            open_url_cmds=cls._handle_url(url),
        )

    @classmethod
    def _firefox_script(cls, url: str, new: int = 0) -> str:
        return cls._OSASCRIPT_TEMPLATE.format(
            type='process',
            browser='Firefox',
            pre_cmd_1=('click menu item "New Window" of menu "File" of menu bar 1'
                       if new == 1 else ''),
            pre_cmd_2='delay 1' if new == 1 else '',
            open_url_cmds=cls._handle_url(url),
        )

    @classmethod
    def _librewolf_script(cls, url: str, new: int = 0) -> str:
        return cls._OSASCRIPT_TEMPLATE.format(
            type='process',
            browser='LibreWolf',
            pre_cmd_1=('click menu item "New Window" of menu "File" of menu bar 1'
                       if new == 1 else ''),
            pre_cmd_2='delay 1' if new == 1 else '',
            open_url_cmds=cls._handle_url(url),
        )

    def open(self, url, new=0, autoraise=True):
        match self.name:
            case 'default':
                # Need to lookup what is configured as the default browser
                script = dedent(f"""\
                    use framework "AppKit"
                    use AppleScript version "2.4"
                    use scripting additions

                    property NSWorkspace : a reference to current application's NSWorkspace
                    property NSURL : a reference to current application's NSURL

                    set http_url to NSURL's URLWithString:"https://python.org"
                    set browser_url to (NSWorkspace's sharedWorkspace)'s ¬
                        URLForApplicationToOpenURL:http_url
                    set app_path to browser_url's relativePath as text

                    set {{TID, text item delimiters}} to {{text item delimiters, "/"}}
                    tell app_path to set basename to last text item
                    set text item delimiters to TID

                    if basename contains "safari" then
                        {self._safari_script(url=url, new=new)}
                    else if basename contains "chrome" then
                        {self._chrome_script(url=url, new=new)}
                    else if basename contains "brave" then
                        {self._brave_script(url=url, new=new)}
                    else if basename contains "edge" then
                        {self._edge_script(url=url, new=new)}
                    else if basename contains "firefox" then
                        {self._firefox_script(url=url, new=new)}
                    else if basename contains "librewolf" then
                        {self._librewolf_script(url=url, new=new)}
                    end if
                """)
            case 'safari':
                script = self._safari_script(url=url, new=new)
            case 'chrome':
                script = self._chrome_script(url=url, new=new)
            case 'brave':
                script = self._brave_script(url=url, new=new)
            case 'edge':
                script = self._edge_script(url=url, new=new)
            case 'firefox':
                script = self._firefox_script(url=url, new=new)
            case 'librewolf':
                script = self._librewolf_script(url=url, new=new)
            case _:
                raise ValueError(f'Unknown browser name: {self.name}')

        osapipe = os.popen('osascript', 'w')
        if osapipe is None:
            return False

        osapipe.write(script)
        rc = osapipe.close()
        return not rc


def setup_macosx_browser_integration():
    webbrowser._tryorder = []  # pyright: ignore [reportAttributeAccessIssue]
    webbrowser.register('MacOSX', None, OmnipyMacOSXOSAScript('default'), preferred=True)
    webbrowser.register('safari', None, OmnipyMacOSXOSAScript('safari'))
    webbrowser.register('chrome', None, OmnipyMacOSXOSAScript('chrome'))
    webbrowser.register('brave', None, OmnipyMacOSXOSAScript('brave'))
    webbrowser.register('edge', None, OmnipyMacOSXOSAScript('edge'))
    webbrowser.register('firefox', None, OmnipyMacOSXOSAScript('firefox'))
    webbrowser.register('librewolf', None, OmnipyMacOSXOSAScript('librewolf'))
