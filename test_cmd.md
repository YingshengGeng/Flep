default_data = {
  "ipv4_src": "10.1.1.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "tcp",
  "tp_src": "2001",
  "tp_dst": "2002",
  "label_list": "0x2502, 0x2503, 0x2505"
}

{"label": 0x2502, "port": 2}
{"label": 0x2503, "port": 3}
{"label": 0x2505, "port": 5}

veth5

default_data = {
  "ipv4_src": "10.1.1.3/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "tcp",
  "tp_src": "2003",
  "tp_dst": "2002",
  "label_list": "0x2502, 0x2503, 0x2505"
}


{"label": 0x2502, "port": 2}
{"label": 0x2503, "port": 3}
{"label": 0x2505, "port": 5}


veth7