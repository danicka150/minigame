[app]

title = My Python Game
package.name = mygame
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = landscape
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
