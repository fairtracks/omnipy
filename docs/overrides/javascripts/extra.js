// From https://github.com/opensafely/documentation/issues/1458#issuecomment-1997884145
// Modified from Github user [Jongmassey](https://github.com/Jongmassey),
// available under the GNU General Public License v3.0:
//
// OpenSAFELY Documentation
// Copyright (C) University of Oxford
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

document.addEventListener("DOMContentLoaded", function() {patchCopyCode();});

function patchCopyCode() {
  codeCopyButtons = document.querySelectorAll('button.md-clipboard');
  for (var btn of codeCopyButtons) {
    var codeText = getTextWithoutPromptAndOutput(btn.dataset.clipboardTarget);
    btn.dataset.clipboardText = codeText;
  }
}

function getTextWithoutPromptAndOutput(targetSelector) {
  var text = '';
  var targetElement = document.querySelector(targetSelector);
  const excludedClasses = ['gp', 'go'];
  for (const span of targetElement.childNodes) {
    for (const node of span.childNodes) {
      if (node.nodeType == Node.TEXT_NODE | (node.nodeType == Node.ELEMENT_NODE && !excludedClasses.includes(node.className))) {
        text += node.textContent;
      }
    }
  }
  return text;
}