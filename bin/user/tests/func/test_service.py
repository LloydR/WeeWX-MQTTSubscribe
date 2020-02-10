"""
An example/prototype of functional test.
Tests the driver, MQTTSubscribeDriver and the service, MQTTSubscribeService.
As close to an end to end test - but not called from WeeWX.
"""
# pylint: disable=wrong-import-order
# pylint: disable=missing-docstring

import unittest

import configobj
import json
import time

import paho.mqtt.client as mqtt

import utils

import weewx
from weewx.engine import StdEngine
from user.MQTTSubscribe import MQTTSubscribeService
class TestJsonPayload(unittest.TestCase):
    def on_connect2(self, client, userdata, flags, rc): # (match callback signature) pylint: disable=unused-argument
        # https://pypi.org/project/paho-mqtt/#on-connect
        # rc:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.
        for topic in userdata['topics']:
            (result, mid) = client.subscribe(topic) # (match callback signature) pylint: disable=unused-variable
            userdata['connected_flag'] = True

    def on_message2(self, client, userdata, msg): # (match callback signature) pylint: disable=unused-argument
        userdata['msg'] = True
        #print(msg.topic)
        #print(msg.payload)

    def service_test(self, testtype, testruns, config_dict):
        #sleep = 1

        cdict = config_dict['MQTTSubscribeService']
        message_callback_config = cdict.get('message_callback', None)
        message_callback_config['type'] = testtype

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

        client = mqtt.Client()
        client.connect(host, port, keepalive)
        client.loop_start()

        userdata = {
            'topics': cdict['topics'].sections,
            'connected_flag': False,
            'msg': False
        }
        client2 = mqtt.Client(userdata=userdata)
        client2.on_connect = self.on_connect2
        client2.on_message = self.on_message2
        client2.connect(host, port, keepalive)
        client2.loop_start()
        client2.connected_flag = False
        while not userdata['connected_flag']: #wait in loop
            #print("waiting to connect")
            time.sleep(1)

        for testrun in testruns:
            for topics in testrun['messages']:
                for topic in topics:
                    topic_info = topics[topic]
                    #print(topic_info)
                    utils.send_msg(utils.send_mqtt_msg, testtype, client.publish, topic, topic_info, userdata)

            time.sleep(1) # more fudge to allow it to get to the service
            #time.sleep(sleep)

            record = {}
            units = testrun['results']['units']
            interval = 300
            current_time = int(time.time() + 0.5)
            end_period_ts = (int(current_time / interval) + 1) * interval

            record['dateTime'] = end_period_ts
            record['usUnits'] = units
            new_loop_packet_event = weewx.Event(weewx.NEW_LOOP_PACKET, packet=record)
            service.new_loop_packet(new_loop_packet_event)
            #records.append(record)

            records = [record]
            utils.check(self, testtype, records, testrun['results']['records'])

        #print(records)
        service.shutDown()
        client.disconnect()
        client2.disconnect()

    #@unittest.skip("")
    def test_get_data_individual1(self):
        with open("bin/user/tests/func/data/first.json") as file_pointer:
            testx_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])
            for testtype in testx_data['types']:
                self.service_test(testtype, testx_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual2(self):
        with open("bin/user/tests/func/data/basic_withaccum.json") as file_pointer:
            testx_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])
            for testtype in testx_data['types']:
                self.service_test(testtype, testx_data['testruns'], config_dict)

    #@unittest.skip("")
    def test_get_data_individual3(self):
        with open("bin/user/tests/func/data/accumulatedrain_withaccum.json") as file_pointer:
            testx_data = json.load(file_pointer, object_hook=utils.byteify)
            config_dict = configobj.ConfigObj(testx_data['config'])
            for testtype in testx_data['types']:
                self.service_test(testtype, testx_data['testruns'], config_dict)

if __name__ == '__main__':
    unittest.main(exit=False)
