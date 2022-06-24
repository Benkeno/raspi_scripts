#!/usr/bin/python
'''PYTHON SCRIPT TO SUBSCRIBE TO A TOPIC AND INSERT INTO MYSQL DATABASE AS ANOTHER MQTT-CLIENT'''


import logging
import mysql.connector
import paho.mqtt.client as mqtt


#SQL CONNECTOR
mydb = mysql.connector.connect(
    host="192.168.178.208",         # DATABSE IP/HOSTNAME (localhost, remote) DEFAULT PORT 3306
    user="root",                    # CREATED USERNAME
    passwd="root",                  # CREATED PASSWORD
    database="barometer"            # CREATED DATABASE NAME
)

mycursor = mydb.cursor()

       #ON_CONNECT
def on_connect(mqttc, obj, flags, rc):
        print("rc: " + str(rc))

# ON_MESSAGE
# Example:
def on_message(mqttc, obj, msg):

            #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic == 'iot/barometer_1/temp':
        print(msg.payload.decode("utf-8") + " oki")

        temp = str(msg.payload.decode("utf-8"))
        sql = "INSERT INTO tbl_temp (temp_ID, timestamp,tempwert) VALUES (NULL,now(),'%s')" % (temp)
        val = (temp)
        print(type(temp))
        print("sql is ", sql)
        print("val is ", val)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "Datensätze wurden hinzugefügt.")

        if msg.topic == 'iot/barometer_1/humi':
            print(msg.payload.decode("utf-8") + " oki")

            humi = str(msg.payload.decode("utf-8"))
            sql = "INSERT INTO tbl_humi (humi_ID, timestamp,humiwert) VALUES (NULL,now(),'%s')" % (humi)
            val = (humi)
            (type(humi))
            print("sql = ", sql)
            print("val = ", val)
            mycursor.execute(sql, val)
            mydb.commit()
            print(mycursor.rowcount, "Datensätze wurden hinzugefügt.")

            if msg.topic == 'iot/barometer_1/hoeheDruck':
                print(msg.payload.decode("utf-8") + " oki")

                hpa = str(msg.payload.decode("utf-8"))
                sql = "INSERT INTO tbl_hpaNN (hpa_ID, timestamp,hpawert) VALUES (NULL,now(),'%s')" % (hpa)
                val = (hpa)
                print(type(hpa))
                print("sql is ", sql)
                print("val is ", val)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "Datensätze wurden hinzugefügt.")

            else:
                print("Fehler: " + msg.payload.decode("utf-8"))

#mycursor.close()


# ON_PUBLISH

def on_publish(mqttc, obj, mid):
            print("mid: " + str(mid))

#ON_ SUBSCRIBE

def on_subscribe(mqttc, obj, mid, granted_qos):
            print("Subscribed: " + str(mid) + " " + str(granted_qos))
#ON_LOG

def on_log(mqttc, obj, level, string):
            print("Log" + string)


# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client("sql-connector")            # MQTT CLIENT-ID
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect("192.168.178.32", 1883, 60)       # IP/HOSTNAME, PORT, KEEP-ALIVE OF BROKER
mqttc.subscribe("iot/barometer_1/#", 0)         # TOPICS TO SUBSCRIBE [("topic/subtopic/.., RETAIN")], [("bla/bla/bla, RETAIN")]

mqttc.loop_forever()
