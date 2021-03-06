import json 

from kazoo.client import KazooClient

from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaClient

# if zookeeper exits then get bootstrap list of borker else use default 
zookeeper_host_ip_port = '192.168.150.70:2181'

bootstrap_servers_list =[]

try : 
    #Connect to zk 
    zk = KazooClient(hosts= zookeeper_host_ip_port )
    zk.start()
    
    #Get list of borkers
    broker_ids_list = zk.get_children("/brokers/ids")
    
    for broker_id in broker_ids_list :
        print broker_id 
        broker_info = zk.get("/brokers/ids/" + broker_id ) 
        print broker_info 
        broker_ip   =  json.loads( broker_info[0] )['host']
        broker_port = json.loads( broker_info[0] )['port']
        bootstrap_servers_list.append(str(broker_ip) + ':' + str(broker_port) ) 

except : 
     print "zookeeper not found , using default "
     bootstrap_servers_list = ['192.168.150.80:9092']     


print "kafka bootstrap servers " , bootstrap_servers_list 
producer = KafkaProducer(bootstrap_servers= bootstrap_servers_list  )

topic_name = 'my-topic3'



#check if topic exists 
kafka_client = KafkaClient(bootstrap_servers_list)
server_topics = kafka_client.topic_partitions

if topic_name in server_topics:
   print "topic exits "
else :
   print "create topic "
   print "/opt/kafka/bin/kafka-topics.sh --create --zookeeper  192.168.150.70:2181  --replication-factor 2 --partitions 2 --topic " + topic_name 
   # os.system ("opt/kafka/bin/kafka-topics.sh --create --zookeeper  192.168.150.70:2181  --replication-factor 2 --partitions 2 --topic " + topic_name ) 



print server_topics 


list_of_messages = [
                   (topic_name, None,  None, '----------------------------------------'),
                   (topic_name, None,  None, 'msg 1 ---- partition - None / key - None'),
                   (topic_name, None,  None, 'msg 2 ---- partition - None / key - None'),
                   (topic_name, None,  None, 'msg 3 ---- partition - None / key - None'),
                   (topic_name, None,  None, 'msg 4 ---- partition - None / key - None'),
                   (topic_name, None,  None, 'msg 5 ---- partition - None / key - None'),
                   (topic_name, None,  None, '----------------------------------------'),
                   (topic_name, 0,     None, 'msg 1 ---- partition - 0    / key - None'),
                   (topic_name, 1,     None, 'msg 2 ---- partition - 1    / key - None'),
                   (topic_name, 0,     None, 'msg 3 ---- partition - 0    / key - None'),
                   (topic_name, 1,     None, 'msg 4 ---- partition - 1    / key - None'),
                   (topic_name, 0,     None, 'msg 5 ---- partition - 0    / key - None'),
                   (topic_name, None,  None, '----------------------------------------'),
                   (topic_name, None, 'foo', 'msg 1 ---- partition - None / key - foo' ),
                   (topic_name, None, 'foo', 'msg 2 ---- partition - None / key - foo' ),
                   (topic_name, None, 'foo', 'msg 3 ---- partition - None / key - foo' ),
                   (topic_name, None, 'foo', 'msg 4 ---- partition - None / key - foo' ),
                   (topic_name, None, 'foo', 'msg 5 ---- partition - None / key - foo' ),
                   (topic_name, None,  None, '----------------------------------------'),
                   (topic_name, 0,     'foo', 'msg 1 ---- partition - 0    / key - foo'),
                   (topic_name, 1,     'foo', 'msg 2 ---- partition - 1    / key - foo'),
                   (topic_name, 0,     'foo', 'msg 3 ---- partition - 0    / key - foo'),
                   (topic_name, 1,     'foo', 'msg 4 ---- partition - 1    / key - foo'),
                   (topic_name, 0,     'foo', 'msg 5 ---- partition - 0    / key - foo'),
		   (topic_name, None,  None, '----------------------------------------'),
                   ]

for (topic_name, partition_number, partition_key, message)  in list_of_messages :

    producer.send(topic_name, partition=partition_number, key=partition_key, value=message ) 
    
# block until all async messages are sent
producer.flush()



# nice way of getting kafka state info using zookeeper ( keep it for record ) 

class KafkaInfo(object):
    def __init__(self, hosts):
        self.zk = KazooClient(hosts)
        self.zk.start()

    def topics(self):
        return self.zk.get_children('/brokers/topics')

    def partitions(self, topic):
        strs = self.zk.get_children('/brokers/topics/%s/partitions' % topic)
        return map(int, strs)

    def consumers(self):
        return self.zk.get_children('/consumers')

    def topics_for_consumer(self, consumer):
        return self.zk.get_children('/consumers/%s/offsets' % consumer)

    def offset(self, topic, consumer, partition):
        (n, _) = self.zk.get('/consumers/%s/offsets/%s/%d' % (consumer, topic, partition))
        return int(n)



# get number of partition directly from kafka 
# client = KafkaClient('SERVER:PORT')
#topic_partition_ids = client.get_partition_ids_for_topic(b'TOPIC')
#len(topic_partition_ids)





'''

# Asynchronous by default
future = producer.send('my-topic3', b'raw_bytes to prod 1')

# Block for 'synchronous' sends
try:
    record_metadata = future.get(timeout=10)
except KafkaError:
    # Decide what to do if produce request failed...
    log.exception()
    pass

# Successful result returns assigned partition and offset
print (record_metadata.topic)
print "partition "+ str (record_metadata.partition)
print (record_metadata.offset)

# produce keyed messages to enable hashed partitioning


# encode objects via msgpack
##producer = KafkaProducer(value_serializer=msgpack.dumps)
##producer.send('msgpack-topic', {'key': 'value'})

# produce json messages
##producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'))
##producer.send('json-topic', {'key': 'value'})

# produce asynchronously
##for _ in range(100):
##    producer.send('my-topic3', b'msg')

# block until all async messages are sent
producer.flush()

# configure multiple retries
#producer = KafkaProducer(retries=5)
#################################
'''







