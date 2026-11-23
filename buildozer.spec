[app]
title = Jarvis Assistant
package.name = jarvisassistant
package.domain = org.rajgupta.jarvis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy,urllib3,requests
orientation = portrait
android.permissions = RECORD_AUDIO,INTERNET,ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
