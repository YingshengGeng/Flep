/* -*- P4_16 -*- */

#include <core.p4>
#include <tna.p4>

/*************************************************************************
 ************* C O N S T A N T S  A N D   T Y P E S  *******************
**************************************************************************/
const bit<16> ETHERTYPE_IPV4 = 0x0800;
const bit<16> ETHERTYPE_IPV6 = 0x86dd;
const bit<16> ETHERTYPE_FLEP = 0x1212; //an unused type, set for FLEP
const bit<16> ETHERTYPE_INSERT = 0x2424; //an unused type, set for insert
const bit<16> ETHERTYPE_INVALID = 0x1234; //an unused type, set for tempforward

// for typo
const bit<16> ETHERTYPE_FLEP_TOPO = 0x1145; //an unused type, set for FLEP
const bit<16> ETHERTYPE_FLEP_NEWGEN = 0x1919;
const bit<16> LOCAL_LABEL = 0x2501;


typedef bit<48> EthernetAddress;
typedef bit<32> IPv4Address;
typedef bit<128> IPv6Address;

typedef bit<16> label_t;
const bit<32> INVALID_KEY = 0xFFFFFFFF;
/* Table Sizes */
const int TABLE_SIZE = 256;

typedef bit<8> trans_protocol_t;
const trans_protocol_t TYPE_TCP = 0x06;
const trans_protocol_t TYPE_UDP = 0x11;

const bit<8> MAX_DEAL = 5;
#define MAX_HOPS 5
/*************************************************************************
 ***********************  H E A D E R S  *********************************
 *************************************************************************/

/*  Define all the headers the program will recognize       */
/*  The actual sets of headers processed by each gress can differ */

/* Standard ethernet header */
header Ethernet_h{
  EthernetAddress dstAddr;
  EthernetAddress srcAddr;
  bit<16> ethernetType;
}


//define flags to indentify the processing of encapsulating
//flags = 0 means the encapsulating accomplishment
header Felp_h{
  bit<16> active_label;
  bit<32> key;    // verify key
  bit<8>  key_index;   // key index 
  bit<16> routing_type; // original ethernet type
  bit<8>  label_depth;  // now labels num
  bit<8> flags;
}

//indicate the number of the unencapsulated label
header insert_h {
  bit<8> identify_index;
  bit<8> recir_count;
  bit<8> remain_labels_count;
}

//indicate the last recirculate forward
header TempForward_h {
  bit<16> temp_port; ///actually bit<9>
  bit<16> temp_routing_type;
}

header Flabel_h {
  bit<16> label;
}

header Fleptopo_h{
  bit<4> messagetype;//0 request; 1 answer
  bit<4> option; //4bit field to indicate some option. 1st (left side) bit 1 indicates that this packet is newly generated, rest 3bit unused.
  bit<16> sourcelabel;//the label of the source node which send this message
  bit<16> sourceport; //port number of the source node
  bit<16> replylabel;//label of the reply node
  bit<16> replyport;//port number of the reply node
  bit<48> sendtstamp;//timestamp when generate this packet
}

header Topoinfo_h{
  bit<16> label;
  bit<16> port;
  bit<32> latency;
}

header IPv4_h {
  bit<4> version;
  bit<4> ihl;
  bit<8> tos;
  bit<16> totallength;
  bit<16> identification;
  bit<3> flags;
  bit<13> fragmentoffset;
  bit<8> ttl;
  bit<8> protocol;
  bit<16> headerchecksum;
  IPv4Address srcAddr;
  IPv4Address dstAddr;
}

header IPv6_h {
  bit<4>    version;
  bit<8>    class;
  bit<20>   flowlabel;
  bit<16>   payloadlength;
  bit<8>    nextheader;
  bit<8>    hoplimit;
  IPv6Address srcAddr;
  IPv6Address dstAddr;
}


header UDP_h {
  bit<16> srcPort;
  bit<16> dstPort;
  bit<16> udplength;
  bit<16> checksum;
}

header TCP_h {
  bit<16> srcPort;
  bit<16> dstPort;
  bit<32> seqNo;
  bit<32> ackNo;
  bit<4>  dataOffset;
  bit<3>  res;
  bit<3>  ecn;
  bit<6>  ctrl;
  bit<16> window;
  bit<16> checksum;
  bit<16> urgentPtr;
}


/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/
 
  /***********************  H E A D E R S  ************************/

struct my_ingress_headers_t{
  Ethernet_h ethernet;
  Fleptopo_h fleptopo;
  Topoinfo_h topoinfo;
  TempForward_h tempforward;
  insert_h insert;
  Felp_h flep;
  IPv4_h ipv4;
  IPv6_h ipv6;
  UDP_h udp;
  TCP_h tcp;
}

struct my_ingress_metadata_t {
  bit<8> identify_index;
  bit<8> portindex;
}

  /******  G L O B A L   I N G R E S S   M E T A D A T A  *********/



  /***********************  P A R S E R  **************************/
parser IngressParser(packet_in    pkt,
  /* User */  
  out my_ingress_headers_t      hdr,
  out my_ingress_metadata_t     meta,
  /* Intrinsic */
  out ingress_intrinsic_metadata_t  ig_intr_md)
{


  /* This is a mandatory state, required by Tofino Architecture */
  state start {
    pkt.extract(ig_intr_md);
    pkt.advance(PORT_METADATA_SIZE);
    transition meta_init;
  }
  
  state meta_init {
    meta.identify_index = 0;
    meta.portindex = 0;
    transition parse_ethernet;
  }

  state parse_ethernet {
    pkt.extract(hdr.ethernet);
    transition select(hdr.ethernet.ethernetType) {
      ETHERTYPE_IPV4: parse_ipv4;
      ETHERTYPE_IPV6 : parse_ipv6;
      ETHERTYPE_INVALID: parse_tempforward;
      ETHERTYPE_FLEP_TOPO: parse_fleptopo;
      default:accept;
    }
  }

  state parse_fleptopo {
    pkt.extract(hdr.fleptopo);
    transition accept;
  }

  state parse_tempforward{
    pkt.extract(hdr.tempforward);
    transition accept;
  }

  state parse_ipv4 {
    pkt.extract(hdr.ipv4);
    transition select(hdr.ipv4.protocol) {
      TYPE_UDP : parse_udp;
      TYPE_TCP : parse_tcp;
      default : accept;
    }
  }

  state parse_ipv6 {
    pkt.extract(hdr.ipv6);
    transition select(hdr.ipv6.nextheader) {
      TYPE_UDP : parse_udp;
      TYPE_TCP : parse_tcp;
      default : accept;
    }
  }

  state parse_udp {
    pkt.extract(hdr.udp);
    transition accept;
  }

   state parse_tcp {
    pkt.extract(hdr.tcp);
    transition accept;
  }
}

control LabelDataCache(in Topoinfo_h indata, 
                        in bit<8> index)(bit<32> num) {
    Register<bit<16>, bit<8>>(num) bw_register;

    RegisterAction<bit<16>, bit<8>, bit<16>>(bw_register) data_save = {
        void apply(inout bit<16> register_data) {
            register_data = indata.label;
        }
    };

    apply {
        data_save.execute(index);
    }
}

control PortDataCache(in Topoinfo_h indata, 
                        in bit<8> index)(bit<32> num) {
    Register<bit<16>, bit<8>>(num) bw_register;

    RegisterAction<bit<16>, bit<8>, bit<16>>(bw_register) data_save = {
        void apply(inout bit<16> register_data) {
            register_data = indata.port;
        }
    };

    apply {
        data_save.execute(index);
    }
}

control latencyDataCache(in Topoinfo_h indata, 
                        in bit<8> index)(bit<32> num) {
    Register<bit<32>, bit<8>>(num) bw_register;

    RegisterAction<bit<32>, bit<8>, bit<32>>(bw_register) data_save = {
        void apply(inout bit<32> register_data) {
            register_data = indata.latency;
        }
    };

    apply {
        data_save.execute(index);
    }
}
/***************** M A T C H - A C T I O N  *********************/

control Ingress(
  /* User */
  inout my_ingress_headers_t             hdr,
  inout my_ingress_metadata_t            meta,
  /* Intrinsic */
  in  ingress_intrinsic_metadata_t         ig_intr_md,
  in  ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
  inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
  inout ingress_intrinsic_metadata_for_tm_t    ig_tm_md)
{   
  LabelDataCache(128) labeldatacache;
  PortDataCache(128) portdatacache;
  latencyDataCache(128) latencydatacache;

  action send(bit<9> port) {
    ig_tm_md.ucast_egress_port = port;
  }
  action drop() {
    ig_dprsr_md.drop_ctl = 1;
  }
  
  table fwd_port {
    key = {
      ig_intr_md.ingress_port : exact;
    }
    actions = {
      send;
      NoAction;
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  } 

  action multiportsend(MulticastGroupId_t groupid) {
    //MulticastGroupId_t bit<16>
    ig_tm_md.mcast_grp_a = groupid;
  }

  //multicast newly generated fleptopo probe packet
  table multicast_send_fleptopo {
    key = {
      hdr.fleptopo.messagetype : exact;
    }
    actions = {
      multiportsend();
      NoAction;
    }
    size = 8;
  }

  action setportindex(bit<8> index) {
    meta.portindex = index;
  }
  //get the index of ingress port, this index is also the index of register
  table get_port_index {
    key = {
      hdr.topoinfo.port : exact;
    }
    actions = {
      setportindex();
    }
    size = 256;
  }

  action create_flep(bit<8> label_depth, bit<8> identify_index) {
    hdr.flep.setValid();
    hdr.flep.active_label = 0; 
    hdr.flep.key = INVALID_KEY; // 未设定密码,默认是0xffffffff
    hdr.flep.key_index = 0; //默认是0
    hdr.flep.routing_type = hdr.ethernet.ethernetType;
    hdr.flep.label_depth = label_depth;
    hdr.flep.flags = 1;
    meta.identify_index = identify_index;

    hdr.ethernet.ethernetType = ETHERTYPE_FLEP;
  } 
  
  table flep_ipv4_classifier{
    // insert flep
    key = {
      hdr.ipv4.dstAddr: ternary;
      hdr.ipv4.srcAddr: ternary;
      hdr.ipv4.protocol: ternary;
      hdr.udp.srcPort : ternary;
      hdr.udp.dstPort : ternary;
      hdr.tcp.srcPort : ternary;
      hdr.tcp.dstPort : ternary;
    }
    actions = {
      create_flep;
      NoAction;
    }

    size = TABLE_SIZE;
    default_action = NoAction;
  }

  table ipv4_lpm {
    key = { 
      hdr.ipv4.dstAddr : lpm; 
    }
    actions = { 
      send; 
      NoAction; 
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }
  
  table ipv6_lpm {
    key = { 
      hdr.ipv6.dstAddr : lpm; 
    }
    actions = { 
      send; 
      NoAction; 
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }
  

  table flep_ipv6_classifier{
    // insert flep
    key = {
      hdr.ipv6.dstAddr: ternary;
      hdr.ipv6.srcAddr: ternary;
      hdr.ipv6.nextheader: ternary;
      hdr.udp.srcPort : ternary;
      hdr.udp.dstPort : ternary;
      hdr.tcp.srcPort : ternary;
      hdr.tcp.dstPort : ternary;
    }
    actions = {
      create_flep;
      NoAction;
    }

    size = TABLE_SIZE;
    default_action = NoAction;
  }

  action recirculate() {
    ig_tm_md.ucast_egress_port[6:0] = 7w68;
  }

  action setfleptopo() {
    //hdr.fleptopo.SetValid();

    hdr.fleptopo.messagetype = 0;
    hdr.fleptopo.option = 0;

    hdr.fleptopo.sourcelabel = LOCAL_LABEL;
    hdr.fleptopo.sourceport = 0xFFFF;

    hdr.fleptopo.replylabel = 0xFFFF;
    hdr.fleptopo.replyport = 0xFFFF;

    hdr.fleptopo.sendtstamp = ig_prsr_md.global_tstamp;

    hdr.ethernet.ethernetType = ETHERTYPE_FLEP_TOPO;
  }

  apply {
    // for test
    if (!fwd_port.apply().hit) {
      if (hdr.ipv4.isValid() || hdr.ipv6.isValid()) {
          hdr.ethernet.srcAddr = ig_prsr_md.global_tstamp;
      }
    }
    

    if (hdr.ethernet.ethernetType == ETHERTYPE_FLEP_NEWGEN) {
      hdr.fleptopo.setValid();
      hdr.fleptopo.messagetype = 0;
      hdr.fleptopo.option = 0b1000;

      hdr.fleptopo.sourcelabel = 0;
      hdr.fleptopo.sourceport = 0;
      hdr.fleptopo.replylabel = 0;
      hdr.fleptopo.replyport = 0;
      hdr.fleptopo.sendtstamp = 0;

      hdr.ethernet.ethernetType = ETHERTYPE_FLEP_TOPO;
    }

     //mutlicast send fleptopo
    if (hdr.fleptopo.isValid() && hdr.fleptopo.messagetype == 0 && hdr.fleptopo.option[3:3] == 1) {
      setfleptopo();
      multicast_send_fleptopo.apply();
    }
    //process received fleptopo request message
    else if (hdr.fleptopo.isValid() && hdr.fleptopo.messagetype == 0 && hdr.fleptopo.option[3:3] == 0) {
      hdr.fleptopo.messagetype = 1;
      hdr.fleptopo.replylabel = LOCAL_LABEL;
      hdr.fleptopo.replyport = (bit<16>) ig_intr_md.ingress_port;

      ig_tm_md.ucast_egress_port = ig_intr_md.ingress_port;
    }
    //process received fleptopo answer message
    //register requires a map for register index and its corresponding port number. e.g. setting register index 0 correpsonds to port 64(1/0)
    //the mapping relationship is set by the controller
    else if (hdr.fleptopo.isValid() && hdr.fleptopo.messagetype == 1 && hdr.fleptopo.option[3:3] == 0 && hdr.fleptopo.sourcelabel == LOCAL_LABEL) {
      hdr.topoinfo.setValid();
      
      hdr.topoinfo.label = hdr.fleptopo.replylabel;
      hdr.topoinfo.port = (bit<16>) ig_intr_md.ingress_port;
      hdr.topoinfo.latency = ig_prsr_md.global_tstamp[47:16] - hdr.fleptopo.sendtstamp[47:16];
      

      get_port_index.apply();
      labeldatacache.apply(hdr.topoinfo, meta.portindex);
      portdatacache.apply(hdr.topoinfo, meta.portindex);
      latencydatacache.apply(hdr.topoinfo, meta.portindex);
      drop();
    }

    //add flep header
    if (hdr.ipv4.isValid()) {
      flep_ipv4_classifier.apply();
      if (!hdr.flep.isValid()) {
        ipv4_lpm.apply();
      }
    } else if (hdr.ipv6.isValid()) {
      flep_ipv6_classifier.apply();
      if (!hdr.flep.isValid()) {
        ipv6_lpm.apply();
      }
    }

    // if haven't encp finished, temporarily add the insert header
    if (hdr.flep.isValid() && hdr.flep.flags != 0) {
      if (!hdr.insert.isValid()) {
        hdr.insert.setValid();
        hdr.insert.identify_index = meta.identify_index;
        hdr.insert.remain_labels_count = hdr.flep.label_depth;
        hdr.insert.recir_count = 0;
        hdr.ethernet.ethernetType = ETHERTYPE_INSERT;
      }
    }

    if (hdr.ethernet.ethernetType == ETHERTYPE_INSERT) {
      recirculate();
    }

    if (hdr.ethernet.ethernetType == ETHERTYPE_INVALID) {
      send(hdr.tempforward.temp_port[8:0]);
      hdr.ethernet.ethernetType = hdr.tempforward.temp_routing_type;
      hdr.tempforward.setInvalid();
    }
    if (hdr.flep.isValid()) {
        hdr.ethernet.dstAddr = ig_prsr_md.global_tstamp;
    }

  }
}

  /*********************  D E P A R S E R  ************************/

control IngressDeparser(packet_out pkt,
  /* User */
  inout my_ingress_headers_t             hdr,
  in  my_ingress_metadata_t            meta,
  /* Intrinsic */
  in  ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md)
{
  apply{
    pkt.emit(hdr.ethernet);
    pkt.emit(hdr.fleptopo);
    pkt.emit(hdr.insert);
    pkt.emit(hdr.flep);
    pkt.emit(hdr.ipv4);
    pkt.emit(hdr.ipv6);
    pkt.emit(hdr.tcp);
    pkt.emit(hdr.udp);
    
  }
}


/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

  /***********************  H E A D E R S  ************************/

struct my_egress_headers_t {
  Ethernet_h ethernet;
  TempForward_h tempforward;
  insert_h insert;
  Felp_h flep;
  Flabel_h[MAX_HOPS] flabels;
}

  /********  G L O B A L   E G R E S S   M E T A D A T A  *********/

struct my_egress_metadata_t {
  bit<8> is_verify_start;
  bit<9> forward_port;
}

  /***********************  P A R S E R  **************************/

parser EgressParser(packet_in    pkt,
  /* User */
  out my_egress_headers_t      hdr,
  out my_egress_metadata_t     meta,
  /* Intrinsic */
  out egress_intrinsic_metadata_t  eg_intr_md)
{
  /* This is a mandatory state, required by Tofino Architecture */
  state start {
    pkt.extract(eg_intr_md);
    meta.is_verify_start = 0;
    meta.forward_port = 0;
    transition parse_ethernet;
  }

  state parse_ethernet {
    pkt.extract(hdr.ethernet);
    transition select(hdr.ethernet.ethernetType) {
        ETHERTYPE_INSERT: parse_insert;
        default: accept;
    }
  }

  state parse_insert {
    pkt.extract(hdr.insert);
    transition parse_flep;
  }
  
  state parse_flep {
    pkt.extract(hdr.flep);
    transition select(hdr.flep.flags){
      default: accept;
    }
  }
}

  /***************** M A T C H - A C T I O N  *********************/

control Egress(
  /* User */
  inout my_egress_headers_t              hdr,
  inout my_egress_metadata_t             meta,
  /* Intrinsic */  
  in  egress_intrinsic_metadata_t          eg_intr_md,
  in  egress_intrinsic_metadata_from_parser_t    eg_prsr_md,
  inout egress_intrinsic_metadata_for_deparser_t   eg_dprsr_md,
  inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md)
{

  action drop() {
    eg_dprsr_md.drop_ctl = 1;
  }

  action flep_decapsulation() {
    hdr.ethernet.ethernetType = hdr.flep.routing_type;
    hdr.flep.setInvalid();
    hdr.flabels[0].setInvalid();
  }

  action flep_encap_1_label(label_t label1) {
    hdr.flabels[0].setValid();
    hdr.flabels[0].label = label1;
  }
  action flep_encap_2_label(label_t label1, label_t label2) {
    hdr.flabels[0].setValid();
    hdr.flabels[1].setValid();

    hdr.flabels[0].label = label1;
    hdr.flabels[1].label = label2;
  }
  action flep_encap_3_label(label_t label1, label_t label2, label_t label3) {
    hdr.flabels[0].setValid();
    hdr.flabels[1].setValid();
    hdr.flabels[2].setValid();

    hdr.flabels[0].label = label1;
    hdr.flabels[1].label = label2;
    hdr.flabels[2].label = label3;
  }
  action flep_encap_4_label(label_t label1, label_t label2, label_t label3, label_t label4) {
    hdr.flabels[0].setValid();
    hdr.flabels[1].setValid();
    hdr.flabels[2].setValid();
    hdr.flabels[3].setValid();

    hdr.flabels[0].label = label1;
    hdr.flabels[1].label = label2;
    hdr.flabels[2].label = label3;
    hdr.flabels[3].label = label4;
  }
  action flep_encap_5_label(label_t label1, label_t label2, label_t label3, label_t label4,label_t label5) {
    hdr.flabels[0].setValid();
    hdr.flabels[1].setValid();
    hdr.flabels[2].setValid();
    hdr.flabels[3].setValid();
    hdr.flabels[4].setValid();

    hdr.flabels[0].label = label1;
    hdr.flabels[1].label = label2;
    hdr.flabels[2].label = label3;
    hdr.flabels[3].label = label4;
    hdr.flabels[4].label = label5;
  }

  table insert_ipv4_label{
    key = {
      hdr.insert.identify_index: exact;
      hdr.insert.remain_labels_count:exact;
      hdr.insert.recir_count:exact;
    }
    actions = {
      flep_encap_1_label;
      flep_encap_2_label;
      flep_encap_3_label;
      flep_encap_4_label;
      flep_encap_5_label;
      NoAction;
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }

  table insert_ipv6_label{
    key = {
      hdr.insert.identify_index: exact;
      hdr.insert.remain_labels_count:exact;
      hdr.insert.recir_count:exact;
    }
    actions = {
      flep_encap_1_label;
      flep_encap_2_label;
      flep_encap_3_label;
      flep_encap_4_label;
      flep_encap_5_label;
      NoAction;
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }

  action start_verify() {
    meta.is_verify_start = 1;
  }

  table is_verify_tbl {
    actions = {
      start_verify;
      NoAction;
    }
    key = {
      hdr.flep.key:   ternary;
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }
  
  action insert_key(bit<8> key_index, bit<32> key) {
    hdr.flep.key = key; // 未设定密码,默认是0xfffffffff
    hdr.flep.key_index = key_index; //默认是0
  }

  table insert_past_key_tbl {
    actions = {
      insert_key;
      NoAction;
    }
    key = {
      hdr.insert.identify_index: ternary;
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }

  table insert_key_tbl {
    actions = {
      insert_key;
      NoAction;
    }
    key = {
      // 全匹配
      hdr.insert.identify_index: ternary;
    }
    size = TABLE_SIZE;
    default_action = NoAction;
  }

  table key_match_tbl {
    actions = {
      NoAction;
      drop;
    }
    key = {
      hdr.flep.key:   exact; //应该有一个默认的表项全1
      hdr.flep.key_index: exact;
    }
    size = TABLE_SIZE;
    default_action = drop;
  }

  action flep_send(bit<9> port) {
    meta.forward_port = port;
  }   

  table flep_processing {
    key = {
      hdr.flabels[0].label: exact;
    }
    actions = {
      flep_send;
      NoAction;
    }

    size = TABLE_SIZE;
    default_action = NoAction;
  }

  apply {
    
    // 验证是否开启服务
    if (hdr.flep.isValid()) {
      is_verify_tbl.apply();
    }
    // 代表开启了服务
    if (meta.is_verify_start == 1) {
      if (hdr.flep.flags == 0) {
        // 如果封�?�结束进行密码验证服�?
        key_match_tbl.apply();
      } else {
        // 没有封�?�结束则继续封�?�密�?
        if (!insert_key_tbl.apply().hit) {
          insert_past_key_tbl.apply();
        }
      }
    }
    // if haven't encp finished, encp labels
    if (hdr.flep.isValid() && hdr.flep.flags != 0) {
      // 插入本次循环应该插入的label
      if (hdr.flep.routing_type == ETHERTYPE_IPV4) {
        insert_ipv4_label.apply();
      }
      if(hdr.flep.routing_type == ETHERTYPE_IPV6) {
        insert_ipv6_label.apply();
      }
      // 数量大于5个继续循环，小于等于的话结束(但是最后也要循环一次，进行转发)
      if (hdr.insert.remain_labels_count > MAX_DEAL) {
        hdr.insert.remain_labels_count = hdr.insert.remain_labels_count - MAX_DEAL;
        hdr.insert.recir_count =  hdr.insert.recir_count + 1;    
      } else {
        hdr.insert.setInvalid();
        hdr.flep.flags = 0;
        hdr.ethernet.ethernetType = ETHERTYPE_FLEP;

        hdr.tempforward.setValid(); 
        // 基于标签进行转发
        flep_processing.apply();
        hdr.tempforward.temp_port = (bit<16>) meta.forward_port;
        hdr.tempforward.temp_routing_type = ETHERTYPE_FLEP;

        // 最后对标签长度做处理
        hdr.flep.label_depth = hdr.flep.label_depth - 1;
        hdr.flabels.pop_front(1);
        // 长度为0后解封装
        if (hdr.flep.label_depth == 0 ){
          flep_decapsulation();
          // 更新封装信息
          hdr.tempforward.temp_routing_type = hdr.ethernet.ethernetType;
        } 
        hdr.ethernet.ethernetType = ETHERTYPE_INVALID; 
      }
      // hdr.ethernet.dstAddr = eg_prsr_md.global_tstamp;
      // if (hdr.ethernet.ethernetType == ETHERTYPE_FLEP) {
      //   // 计算时延：当前出口时间 - 暂存在 srcAddr 中的入口时间 
        
      //   // 将时延结果写入 dstAddr，方便发包仪/Wireshark 读取
      //   // 比如读到目的MAC是 00:00:00:00:02:58，即为 600ns
      //   hdr.ethernet.dstAddr =  eg_prsr_md.global_tstamp;
      // }
    }
  }
}

  /*********************  D E P A R S E R  ************************/

control EgressDeparser(packet_out pkt,
  /* User */
  inout my_egress_headers_t             hdr,
  in  my_egress_metadata_t            meta,
  /* Intrinsic */
  in  egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md)
{
  apply {
    pkt.emit(hdr.ethernet);
    pkt.emit(hdr.tempforward);
    pkt.emit(hdr.insert);
    pkt.emit(hdr.flep);
    pkt.emit(hdr.flabels);
  }
}


/************ F I N A L   P A C K A G E ******************************/
Pipeline(
  IngressParser(),
  Ingress(),
  IngressDeparser(),
  EgressParser(),
  Egress(),
  EgressDeparser()
) pipe;

Switch(pipe) main;
