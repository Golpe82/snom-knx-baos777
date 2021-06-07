#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd
from pyparsing import Word, hexnums, alphas, alphanums, Suppress, Combine, nums, string, Regex, pyparsing_common
import subprocess
import socket
import re
import getmac
import csv

CONF_FILE = '/etc/rsyslog.d/als_snom.conf'
SYSLOG_FILE = '/usr/local/gateway/snomsyslogknx/als_snom.log'
AMBIENTLIGHT_STATUS_FILE = "/usr/local/gateway/snomsyslogknx/AlsStatus.csv"
MSG_KEYS = ["timestamp", "ip address", "mac",
            "syslog class", "snom class", "content"]
BOOTSTRAP = {
    'success': 'alert-success',
    'info': 'alert-info',
    'warning': 'alert-warning',
    'danger': 'alert-danger',
    'primary': 'alert-primary',
    'secondary': 'alert-secondary',
    'light': 'alert-light',
    'dark': 'alert-dark'
}

def get_local_ip():
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        local_socket.connect(('10.255.255.255', 1))
        local_ip = local_socket.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        local_socket.close()
    return local_ip


def add_ip_client(ip_address):
    MAC = str(getmac.get_mac_address(ip=ip_address)).replace(":", '')
    TEMPLATE = (
        f'$template snom{MAC}, "{ SYSLOG_FILE }"\n'
        f':fromhost-ip, isequal, "{ ip_address }" -?snom{MAC}\n'
        f'& stop\n'
    )

    with open(CONF_FILE, 'a+') as als_log:
        content = als_log.readlines()

        if TEMPLATE not in content:
            als_log.write(TEMPLATE)

    subprocess.call(["systemctl", "restart", "rsyslog"])

def get_phones_info():
    IP = "\d+\.\d+\.\d+\.\d+"
    MAC = "00041[a-f0-9]+"
    phones = []
    PHONE_ITEM = {'IP': "no IP", 'MAC': "no MAC"}
    
    with open(CONF_FILE) as syslog_config:
        phone_item = PHONE_ITEM

        for line in syslog_config:
            match_ip = re.search(IP, line)
            match_mac = re.search(MAC, line)

            if match_ip:
                phone_item.update(IP=match_ip.group(0))

            if match_mac:
                mac = match_mac.group(0)

                if mac in phone_item.get("MAC"):
                    phones.append(phone_item)
                    phone_item = PHONE_ITEM

                else:
                    phone_item.update(MAC=mac)

    return phones

def assign_groupaddresses(phone_ip,ga_read, ga_write):
    for phone_info in get_phones_info():
        if phone_info.get("IP") == phone_ip:
            phone_info.update(GA_READ=ga_read, GA_WRITE=ga_write)

def save_als_value(als_value, als_row):
    PHONE = get_phones_info()[0]

    with open(AMBIENTLIGHT_STATUS_FILE, "w") as als_status:
        fieldnames = ["Phone MAC", "Phone IP", "ALS row value", "ALS value (Lux)"]
        writer = csv.DictWriter(als_status, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "Phone MAC": PHONE.get("MAC"),
                "Phone IP": PHONE.get("IP"),
                "ALS row value": als_row,
                "ALS value (Lux)": als_value
            },
        )

def get_als_value(mac):
    with open(AMBIENTLIGHT_STATUS_FILE) as als_status:
        fieldnames = ["Phone MAC", "Phone IP", "ALS row value", "ALS value (Lux)"]
        reader = csv.DictReader(als_status)
        for phone in reader:
            values = {field: value for (field, value) in fieldnames.items()}

    return values


def to_lux(raw_value):
    value = int(raw_value)*6.5/100

    return round(value, 2)


class RSyslogParser(object):
    """Class to parse snom desktop syslog files 
    e.g. 
    Feb 23 08:29:18.156 [DEBUG0] PHN: apply_value: hide_identity = 'false', set.need_apply: 0, finished: 1, need reboot to apply: 0

    Feb 24 16:20:08 10.110.16.59 000413A34795 [INFO  ] PHN: ALS_VALUE:180
    """

    def __init__(self):
        ints = Word(nums)

        # timestamp
        month = Word(string.ascii_uppercase, string.ascii_lowercase, exact=3)
        day = ints
        hour = Combine(ints + ":" + ints + ":" + ints)

        # still 3 fields in pattern
        timestamp = Combine(month + Regex("..") + day + " " + hour)

        ip_address = Combine(ints + "." + ints + "." + ints + "." + ints)

        # phone mac
        mac = Word(hexnums, exact=12)

        # syslog class
        syslog_class = Combine("[" + Word(alphanums) + Regex(".*]"))

        # snom class
        snom_class = Combine(Word(string.ascii_uppercase, exact=3) + ":")

        # message still has ending ']'
        message = Combine(Regex(".*"))
        #message = Regex(".*")

        # pattern build
        self.__pattern = timestamp + ip_address + \
            mac + syslog_class + snom_class + message
        # print(self.__pattern)

    def tail(self, f, n, offset=0):
        # when tail fails, log file not existing we return an empty list
        lines = []
        with subprocess.Popen(['tail', '-n', '%s' % (n + offset), f], stdout=subprocess.PIPE, encoding='utf-8') as proc:
            lines = proc.stdout.readlines()
            proc.wait()

        return lines

    def get_message(self, message, content):
        message_dict = self.to_dict(message)
        message_dict.update({'bootstrap': BOOTSTRAP.get('info')})
        content_value = self.get_content_value(message_dict)

        return self.update_message(message_dict, content_value)

    def to_dict(self, message):
        msg_values = self.__pattern.parseString(message)

        return dict(zip(MSG_KEYS, msg_values))

    def get_content_value(self, message):
        DIGITS = "\d+"
        CONTENT = message.get(MSG_KEYS[5])

        match = re.search(DIGITS, CONTENT)

        return match.group(0)

    def update_message(self, message, value):
        message.update(
            {'bootstrap': BOOTSTRAP.get('success'), 'value': value})

        return message
