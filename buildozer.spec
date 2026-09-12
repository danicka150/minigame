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

android.api = 35
android.minapi = 21
android.ndk = 27c
android.archs = arm64-v8a,armeabi-v7a

android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk

icon.filename = %(source.dir)s/icon.png

[buildozer]

log_level = 2
warn_on_root = 1
