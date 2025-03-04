# WeeWX-MQTTSubscribe

A Weewx service and driver that receives data from multiple MQTT topics.

Currently MQTT payloads of json, keyword (field1=value, field2=value..),
and individual (each topic contains a single observation) are supported.

## Description

### **Driver**

The driver captures the MQTT payload in a separate thread.
Then in *genLoopPackets*, every element in the queue is turned into its own packet.

It is also possible to subscribe to a second topic. The MQTT payload from this topic is put into a separate queue.
This queue is processed by the *genArchiveRecords* to create archive records (simulating hardware generation).
With the combination of the two topics/queues,
one can have a WeeWX instance gather the data and publish loop and archive data for other instances to receive.

When generating loop packets and the queue becomes empty, the option, wait_before_retry,
controls how long before an attempt is made to get data from the queue.

### **Service**

The service can bind to either new loop packets or new archive records.
In both cases a separate thread captures the MQTT payload and puts it on a queue.
On new packets/records events, the main thread takes the elements from the queue and accumulates them into a single dictionary of data fields.
If necessary, the data is converted to the units of the packet/record. The packet/record is then updated with the data.

The elements that are processed from the queue can be controlled by various configuration options.
By default, if the MQTT datetime is less than the previous packet's datetime it is ignored.
This check can be ignored by setting ignore_start_time to True.
It can be controlled more granularly by setting adjust_start_time to the number of seconds prior to the previous packet's datetime is allowed.
Also by default, when the MQTT datetime is greater than the packet's datetime, the pocessing of the queue for this packet stops.
This check can be ignored by setting ignore_end_time to True.
It can be controlled more granularly by setting adjust_end_time to the number of seconds after the packet's datetime is allowed to be processed.

## Installation notes

**Note:** It is rare that MQTTSubscribe should be configured to run as both a `service` and `driver`.
If you are augmenting an existing driver's data, run MQTTSubscribe as a `service`. Otherwise, run it as a `driver`.

Because there are [multiple methods to install WeeWX](http://weewx.com/docs/usersguide.htm#installation_methods), location of files can vary.
See [where to find things](http://weewx.com/docs/usersguide.htm#Where_to_find_things)
in the WeeWX [User's Guide](http://weewx.com/docs/usersguide.htm") for the definitive information.
The following symbolic names are used to define the various locations:

* *$DOWNLOAD_ROOT* - The directory containing the downloaded *MQTTSubscribe* extension.
* *$CONFIG_ROOT* - The directory where the configuration (typically, weewx.conf) is located.

The notation vX.Y.Z designates the version being installed.
X.Y.Z is the release.

Prior to making any updates/changes, always make a backup.

## Preqrequisites

|WeeWX version   |Python version                               |
|----------------|---------------------------------------------|
|3.7.1 or greater|Python 2.7.x                                 |
|4.0.0 or greater|Python 2.7.x <br>or<br> Python 3.5 or greater|

See the [current MQTTSubscribe build/test matrix](https://ci.appveyor.com/project/bellrichm/weewx-mqttsubscribe)
for the current WeeWX and python versions being tested.

Install the Paho MQTT python client.

* For Debian based distributions (Ubuntu, Raspberry Pi OS, etc)

    For python 3: `sudo apt-get install python3-paho-mqtt`

    For python 2: `sudo apt-get install python-paho-mqtt`

* For other distributions or if the package install does not work

    For python 3: `pip3 install paho-mqtt`

    For python 2: `pip install paho-mqtt`

## Installation

1. Download MQTTSubscribe

    ```
    wget -P $DOWNLOAD_ROOT https://github.com/bellrichm/WeeWX-MQTTSubscribe/archive/vX.Y.Z.tar.gz
    ```

    All of the releases can be found [here](https://github.com/bellrichm/WeeWX-MQTTSubscribe/releases) and this is the [latest](https://github.com/bellrichm/WeeWX-MQTTSubscribe/releases/latest).

2. Install MQTTSubscribe
    * As a driver

        ```
        wee_extension --install=$DOWNLOAD_ROOT/vX.Y.Z.tar.gz
        wee_config --reconfig
        ```

        **Note:** By default when installing, the service is installed and configured, but not enabled.
        To not install and configure the service (only install the file(s)),
        set the environment variable MQTTSubscribe_install_type to DRIVER. For example,

        ```
        MQTTSubscribe_install_type=DRIVER wee_extension --install=$DOWNLOAD_ROOT/vX.Y.Z.tar.gz
        ```

        And then configure the driver.

        ```
        wee_config --reconfig
        ```

    * As a service

        ```
        wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
        ```

        **Note:** By default when installing, the service is installed and configured, but not enabled.
        To enable, set the environment variable MQTTSubscribe_install_type to SERVICE. For example,

        ```
        MQTTSubscribe_install_type=SERVICE wee_extension --install=$DOWNLOAD_DIR/vX.Y.Z.tar.gz
        ```

    In either case, **edit the [MQTTSubscribeDriver] or [MQTTSubscribeService] stanza as required**.
    At the very least the [\[topics\]] stanza must be configured to the topics to subscribe to.
    Other settings such as host and port may need to be changed.
    See, [configuring MQTTSubscribe](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Configuring).

    **Note:** For some WeeWX install types, the weew_extension and wee_config commands will neeed its path prepended to it.

3. Restart WeeWX

    ```
    sudo /etc/init.d/weewx restart
    ```

    or

    ```
    sudo sudo service restart weewx
    ```

    or

    ```
    sudo systemctl restart weewx
    ```

## Manual Installation

See, [manual installation](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Manual-installation).

## Debugging

See, [debugging](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Debugging).

## Getting Help

Feel free to [open an issue](https://github.com/bellrichm/WeeWX-MQTTSubscribe/issues/new),
[start a discussion in github](https://github.com/bellrichm/WeeWX-MQTTSubscribe/discussions/new),
or [post on WeeWX google group](https://groups.google.com/g/weewx-user).
When doing so, see [Help! Posting to weewx user](https://github.com/weewx/weewx/wiki/Help!-Posting-to-weewx-user)
for information on capturing the log.
And yes, **capturing the log from WeeWX startup** makes debugging much easeier.

[![Build status](https://ci.appveyor.com/api/projects/status/r0e08p7qt278thax?svg=true)](https://ci.appveyor.com/project/bellrichm/weewx-mqttsubscribe-master)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=alert_status)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=bugs)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=code_smells)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=coverage)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=duplicated_lines_density)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=ncloc)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=security_rating)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=sqale_index)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)

[![codecov](https://codecov.io/gh/bellrichm/WeeWX-MQTTSubscribe/branch/master/graph/badge.svg)](https://codecov.io/gh/bellrichm/WeeWX-MQTTSubscribe)

[![Coverage Status](https://coveralls.io/repos/github/bellrichm/WeeWX-MQTTSubscribe/badge.svg?branch=master&service=github)](https://coveralls.io/github/bellrichm/WeeWX-MQTTSubscribe?branch=master)
