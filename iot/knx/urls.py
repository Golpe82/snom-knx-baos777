"""knx app URLs configuration"""
from django.urls import path

from knx import views


app_name = "knx"

urlpatterns = [
    path("", views.index, name="knx_home"),
    path("settings/", views.knx_settings, name="knx_settings"),
    path(
        "update_led_subscriptors/<int:main>/<int:midd>/<int:sub>/<str:status>",
        views.update_led_subscriptors,
        name="update_led_subscriptors",
    ),
    path(
        "addresses/<str:maingroup>/<str:subgroup>/", views.addresses, name="addresses"
    ),
    path("minibrowser/", views.minibrowser, name="minibrowser"),
    path(
        "minibrowser/subscription/<int:subscription_id>/<str:boolean>/",
        views.minibrowser_led_subscription,
        name="subscription_xml",
    ),
    path(
        "minibrowser/<str:mainaddress>/",
        views.minibrowser_middaddresses,
        name="mb_middaddresses",
    ),
    path(
        "minibrowser/<str:mainaddress>/<str:middaddress>/",
        views.minibrowser_subaddresses,
        name="mb_subaddresses",
    ),
    path(
        "minibrowser/<str:mainaddress>/<str:middaddress>/<str:subaddress>/",
        views.minibrowser_values,
        name="mb_values",
    ),
    path("subprocesses/start/<str:name>", views.start_subprocess, name="start_subprocess"),
    path("subprocesses/stop/<str:name>", views.stop_subprocess, name="stop_subprocess"),
    path("subprocesses/", views.subprocesses, name="subprocesses"),
    path("upload/", views.upload_file, name="upload_file"),
    path("groupaddresses/", views.render_groupaddresses, name="groupaddresses"),
    # REST API URLs
    path("read/<int:main>/<int:midd>/<int:sub>/", views.knx_read, name="knx_read"),
    path(
        "write/<int:main>/<int:midd>/<int:sub>/<str:dpt_name>/<str:value>",
        views.knx_write,
        name="knx_write",
    ),
    path(
        "<int:main>/<int:midd>/<int:sub>/start_blink/<int:sec_for_true>/<int:sec_for_false>",
        views.start_blink,
        name="start_blink",
    ),
    path(
        "<int:main>/<int:midd>/<int:sub>/stop_blink",
        views.stop_blink,
        name="stop_blink",
    ),
    path(
        "check_write/<int:main>/<int:midd>/<int:sub>/<str:value>/<str:code>",
        views.check_code,
        name="check_code",
    ),
    path(
        "relations/temperature/ips/",
        views.temperature_sensor_relations_ips,
        name="temp_relations_ips",
    ),
    path(
        "relations/temperature/<str:device_ip>/",
        views.temperature_sensor_relations,
        name="temp_relations",
    ),
    path(
        "relations/ambient_light/ips/",
        views.ambient_light_sensor_relations_ips,
        name="als_relations_ips",
    ),
    path(
        "relations/ambient_light/<str:device_ip>/",
        views.ambient_light_sensor_relations,
        name="als_relations",
    ),
]
