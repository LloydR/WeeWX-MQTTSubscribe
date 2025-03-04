#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-docstring
# pylint: disable=wrong-import-order
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from __future__ import print_function

import json
import time
import unittest
import configobj
import paho.mqtt.client as mqtt

import utils

import weewx
from weewx.engine import StdEngine
from user.MQTTSubscribe import setup_logging
from user.MQTTSubscribe import MQTTSubscribeService

class TestService(unittest.TestCase):
    def runit(self, payload, file_pointer, check_results=True):
        test_data = json.load(file_pointer, object_hook=utils.byteify)
        config_dict = configobj.ConfigObj(test_data['config'])
        testruns = test_data['testruns']

        cdict = config_dict['MQTTSubscribeService']
        if not 'message_callback' in config_dict['MQTTSubscribeService']:
            config_dict['MQTTSubscribeService']['message_callback'] = {}
        config_dict['MQTTSubscribeService']['message_callback']['type'] = payload

        unit_system_name = cdict['topics'].get('unit_system', 'US').strip().upper()
        if unit_system_name not in weewx.units.unit_constants:
            raise ValueError("MQTTSubscribe: Unknown unit system: %s" % unit_system_name)
        unit_system = weewx.units.unit_constants[unit_system_name]

        min_config_dict = {
            'Station': {
                'altitude': [0, 'foot'],
                'latitude': 0,
                'station_type': 'Simulator',
                'longitude': 0
            },
            'Simulator': {
                'driver': 'weewx.drivers.simulator',
            },
            'Engine': {
                'Services': {}
            }
        }

        engine = StdEngine(min_config_dict)
        service = MQTTSubscribeService(engine, config_dict)

        host = 'localhost'
        port = 1883
        keepalive = 60

        userdata = {
            'topics': [],
            'connected_flag': False,
        }
        client = mqtt.Client(userdata=userdata)
        client.on_connect = utils.on_connect
        client.connect(host, port, keepalive)
        client.loop_start()

        max_connect_wait = 1 # ToDo - configure
        i = 1
        while not userdata['connected_flag']:
            if i > max_connect_wait:
                self.fail("Timed out waiting for connections.")
            time.sleep(1)
            i += 1

        userdata2 = {
            'topics': cdict['topics'].sections,
            'connected_flag': False,
            'msg': False,
            'max_msg_wait': 1 #ToDo - configure
        }
        client2 = mqtt.Client(userdata=userdata2)
        client2.on_connect = utils.on_connect
        client2.on_message = utils.on_message
        client2.connect(host, port, keepalive)
        client2.loop_start()
        max_connect2_wait = 1 # ToDo - configure
        i = 1
        while not userdata2['connected_flag']:
            if i > max_connect2_wait:
                self.fail("Timed out waiting for connection 2.")
            time.sleep(1)
            i += 1

        max_waits = 10
        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    msg_count = utils.send_msg(utils.send_mqtt_msg, payload, client.publish, topic, topic_info, userdata2, self)
                    utils.wait_on_queue(service, msg_count, max_waits, 1)

            record = {}
            interval = 300
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval

            record['dateTime'] = end_period_ts
            record['usUnits'] = unit_system
            new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
            service.new_loop_packet(new_loop_packet_event)

            records = [record]

            if check_results:
                results = testrun['results']
                result = {}
                found = False
                for result in results:
                    if 'service' in result['test']:
                        if payload in result['payloads']:
                            found = True
                            break
                self.assertTrue(found, "No results for %s" %payload)

                utils.check(self, payload, records, result['records'])
            else:
                for record in records:
                    print(record)

        service.shutDown()
        client.disconnect()
        client2.disconnect()

class TestAccumulatedRain(TestService):
    #@unittest.skip("")
    def test_accumulatedrain_individual(self):
        # At WeeWX 4.6.1, the handling of 'sum' accumulators changed.
        # In prior versions if there was no data a 0 was returned. Now None isvreturned.
        # Only two old WeeWX versions sre tested. We just won't tests against these
        if weewx.__version__ == '3.7.1' or weewx.__version__ == '3.9.0':
            return
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_accumulatedrain_json(self):
        if weewx.__version__ == '3.7.1' or weewx.__version__ == '3.9.0':
            return
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_accumulatedrain_keyword(self):
        if weewx.__version__ == '3.7.1' or weewx.__version__ == '3.9.0':
            return
        with open("bin/user/tests/integ/data/accumulatedrain.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestBasic(TestService):
    #@unittest.skip("")
    def test_basic_individual(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_basic_json(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_basic_keyword(self):
        with open("bin/user/tests/integ/data/basic.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestEmpty(TestService):
    #@unittest.skip("")
    def test_empty_individual(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_empty_json(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_empty_keyword(self):
        with open("bin/user/tests/integ/data/empty.json") as file_pointer:
            self.runit('keyword', file_pointer)

class TestWindIndividualTopics(TestService):
    #@unittest.skip("")
    def test_wind_individual_topic(self):
        with open("bin/user/tests/integ/data/wind-individual.json") as file_pointer:
            self.runit('individual', file_pointer)

class TestWind(TestService):
    #@unittest.skip("")
    def test_wind_individual(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('individual', file_pointer)

    #@unittest.skip("")
    def test_wind_json(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('json', file_pointer)

    #@unittest.skip("")
    def test_wind_keyword(self):
        with open("bin/user/tests/integ/data/wind.json") as file_pointer:
            self.runit('keyword', file_pointer)

if __name__ == '__main__':
    setup_logging(1, {})
    unittest.main(exit=False, failfast=True)
