[app]

title = TacticalPad
package.name = tacticalpad
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,csv,json

version = 1.0.0

requirements = python3,kivy

orientation = landscape
fullscreen = 0

icon.filename = %(source.dir)s/field.png
presplash.filename = %(source.dir)s/field.png

[buildozer]
log_level = 2
warn_on_root = 1
