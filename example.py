#!/usr/bin/python
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

net = Containernet(controller=Controller)

#info('*** Adding controller\n')
#net.addController('c0')

info('*** Adding docker routers containers\n')

r1 = net.addDocker(
        'r1', ip='10.0.1.1/24',
        dimage="astra_linux_ce-frr:2.12",
        cap_add=["cap_net_admin","cap_net_raw","cap_sys_admin"],
        dcmd="sh -c '/usr/lib/frr/frrinit.sh start; bash'",
        network_mode="none",
        )

r2 = net.addDocker(
        'r2', ip='10.0.2.1/24',
        dimage="astra_linux_ce-frr:2.12",
        cap_add=["cap_net_admin","cap_net_raw","cap_sys_admin"],
        dcmd="sh -c '/usr/lib/frr/frrinit.sh start; bash'",
        network_mode="none",
        )

r3 = net.addDocker(
        'r3', ip='10.0.3.1/24',
        dimage="astra_linux_ce-frr:2.12",
        cap_add=["cap_net_admin","cap_net_raw","cap_sys_admin"],
        dcmd="sh -c '/usr/lib/frr/frrinit.sh start; bash'",
        network_mode="none",
        )



info('*** Adding docker arms containers\n')

a1 = net.addDocker(
        'a1', ip='10.0.1.100/24',
        dimage="ubuntu:trusty",
        network_mode="none",
        )

a2 = net.addDocker(
        'a2', ip='10.0.2.100/24',
        dimage="ubuntu:trusty",
        network_mode="none",
        )

a3 = net.addDocker(
        'a3', ip='10.0.3.100/24',
        dimage="ubuntu:trusty",
        network_mode="none",
        )

info('*** Creating links\n')
net.addLink(r1, a1)
net.addLink(r2, a2)
net.addLink(r3, a3)
net.addLink(r1, r2, intfName1='r1r2', intfName2='r2r1')
net.addLink(r1, r3, intfName1='r1r3', intfName2='r3r1')
net.addLink(r2, r3, intfName1='r2r3', intfName2='r3r2')

info('*** Additional commands\n')
a1net = net.get('a1')
a2net = net.get('a2')
a3net = net.get('a3')
a1net.cmd('sh -c "sleep 10; ip route add default via 10.0.1.1" &')
a2net.cmd('sh -c "sleep 10; ip route add default via 10.0.2.1" &')
a3net.cmd('sh -c "sleep 10; ip route add default via 10.0.3.1" &')

r1net = net.get('r1')
r2net = net.get('r2')
r3net = net.get('r3')
r1net.setIP('192.168.12.1/29', intf='r1r2')
r1net.setIP('192.168.13.1/29', intf='r1r3')
r2net.setIP('192.168.12.2/29', intf='r2r1')
r2net.setIP('192.168.23.2/29', intf='r2r3')
r3net.setIP('192.168.13.3/29', intf='r3r1')
r3net.setIP('192.168.23.3/29', intf='r3r2')

info('*** Starting network\n')
net.start()

info('*** Running CLI\n')
CLI(net)

info('*** Stopping network')
net.stop()

