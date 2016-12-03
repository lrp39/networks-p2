import socket
import sys
import time

# Get list of target sites
with open("targets.txt") as file:
        targets = file.read().splitlines()

port =33434 # looked up and said this is usually used for traceroutes
init_ttl = 32  # the initial time to live so it won't get reset

#create a payload that is the maxium 1480 bits 
payload = "abcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyzabcdefghijklmnopqrstubwxyz"
payload = payload+ payload +'abcdefghijklmnoopqrstuvwxyz!!!!!!!!!!!!'
payload_size = sys.getsizeof(payload)

#try to a maximum of 3 times to get data back, break when gets it 
for target in targets:
        for j in range(0,3):
                #get the address of the target website
                target_ip = socket.gethostbyname(target)
 
                #create sockets
                in_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
                out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname("udp"))

                #set the tll of the socket
                out_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, init_ttl)

                #set the timeout for recieving socket to wait until it gives up
                in_socket.settimeout(4) 

                #start a timer for getting RTT
                start_time = time.time()

                #send the packet to the target
                out_socket.sendto(payload,(target_ip,port))

                #try to get response from the reciever
                try: 
                        #get the string and the ip_address of the sender. Buffer size = 3000
                        data, address = in_socket.recvfrom(3000)

                        #record the time recieved
                        end_time=time.time()

                        #close the sockets
                        out_socket.close()
                        in_socket.close()
                
                        #extract needed data from the recieved icmp
                        icmp_response_type = ord(data[20])  
                        icmp_response_code = ord(data[21])
                        icmp_response_ttl = ord(data[36])
                        
                        #get the addresses out of the icmp message so they can be checked to see if 
                        #its the right message[response source address, response dest addr, source addr, dest addr ]
                        response_addresses = [data[40:44],data [44:48],data[12:16],data[16:20]]
                        
                        #format into IP addresses
                        response_addresses_string=list()
                        for addr in response_addresses: 
                                response_addresses_string.append(str(ord(addr[0]))+'.' +str(ord(addr[1]))+'.' +str(ord(addr[2]))+'.' +str(ord(addr[3])))   
                        
                        #Make sure its the correct response
                        if(
                               icmp_response_type != 3 or icmp_response_code != 3 or
                               response_addresses_string[0] != '129.22.146.171'or #got number by running 'get addr show' in terminal and hard coding it in since testing is on the same vm
                               response_addresses_string[1] != target_ip or
                               response_addresses_string[2] != target_ip or
                               response_addresses_string[3] != '129.22.146.171'
                        ):
                                print "Did not recieve the correct message back in the socket" 
                                continue #try to get a response again
                        else:
                                hops = init_ttl - icmp_response_ttl
                                RTT = (end_time - start_time) * 1000 #convert time seconds to ms
                                bytes_left = len(data[28:])- 20  # the amount sent back - header amount          
                                print target + ' ' + target_ip + ':  '+ str(hops) +' Hops, '+ str(RTT) + ' RTT, ' + str(bytes_left) + ' bytes left of orginal ' + str(payload_size) +'  bytes sent.'  
                                break # have needed data, can stop trying

                except socket.error:
                        print "there was no response from %s." % (target)
                
