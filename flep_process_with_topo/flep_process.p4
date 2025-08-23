/* -*- P4_16 -*- */

#include <core.p4>
#include <tna.p4>

/*************************************************************************
 ************* C O N S T A N T S  A N D   T Y P E S  *******************
**************************************************************************/
// for flep
const bit<16> ETHERTYPE_FLEP = 0x1212; //an unused type, set for FLEP

// for typo
const bit<16> ETHERTYPE_FLEP_TOPO = 0x1145; //an unused type, set for FLEP
const bit<16> ETHERTYPE_FLEP_NEWGEN = 0x1919;
const bit<16> LOCAL_LABEL = 0x2501;

typedef bit<48> EthernetAddress;
typedef bit<16> label_t;
const bit<32> INVALID_KEY = 0xFFFFFFFF;
/* Table Sizes */
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
header Flep_h{
  bit<16> active_label; // 正在执行标签,这个多余吧
  bit<32> key;    // 验证密码
  bit<8>  key_index;   // 密钥编号
  bit<16> routing_type; // 被封装协议号(这个是16吧)
  bit<8>  label_depth;  // 剩余标签深度
  bit<8> flags;
}


header Flabel_h {
  bit<16> label;    //标签值
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


/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/
 
  /***********************  H E A D E R S  ************************/

struct my_ingress_headers_t{
  Ethernet_h ethernet;
  Fleptopo_h fleptopo;
  Topoinfo_h topoinfo;
  Flep_h flep;
  Flabel_h flabels;
}

struct my_ingress_metadata_t {
  bit<8> is_verify_start;
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
    meta.is_verify_start = 0;
    meta.portindex = 0;
    transition parse_ethernet;
  }
  
  state parse_ethernet {
    pkt.extract(hdr.ethernet);
    transition select(hdr.ethernet.ethernetType) {
      ETHERTYPE_FLEP: parse_flep;
      ETHERTYPE_FLEP_TOPO: parse_fleptopo;
      default:accept;
    }
  }

  state parse_fleptopo {
    pkt.extract(hdr.fleptopo);
    transition accept;
  }

  state parse_flep {
    pkt.extract(hdr.flep);
    transition select(hdr.flep.flags){
      0:parse_flabels;
      default:accept;
    }
  }

  state parse_flabels {
    // 只解析一个
    pkt.extract(hdr.flabels);
    transition accept;
  }
  
}

// Register for test
// index宽度，内部数据宽度
control PktCounter(in bit<8> index)(bit<32> num) {
    // 元素宽度，索引宽度
    Register<bit<32>, bit<8>>(num) bw_register;
    // 元素宽度，索引宽度，返回值
    RegisterAction<bit<32>, bit<8>, bit<16>>(bw_register) pkt_count = {
        void apply(inout bit<32> register_data) {
            register_data = register_data + 1;
        }
    };
    apply {
        pkt_count.execute(index);
    }
}

control keyDataCache(in Flep_h indata, 
                        in bit<8> index)(bit<32> num) {
    Register<bit<32>, bit<8>>(num) bw_register;

    RegisterAction<bit<32>, bit<8>, bit<32>>(bw_register) data_save = {
        void apply(inout bit<32> register_data) {
            register_data = indata.key;
        }
    };

    apply {
        data_save.execute(index);
    }
}

control keyindexDataCache(in Flep_h indata, 
                        in bit<8> index)(bit<32> num) {
    Register<bit<32>, bit<8>>(num) bw_register;

    RegisterAction<bit<32>, bit<8>, bit<32>>(bw_register) data_save = {
        void apply(inout bit<32> register_data) {
            register_data = (bit<32>)indata.key_index;
        }
    };

    apply {
        data_save.execute(index);
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
  // for test
  PktCounter(10) pkt_counter;
  keyDataCache(10) keydatacache;
  keyindexDataCache(10) keyindexdatacache;

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
    size = 256;
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

  action flep_send(bit<9> port) {
    ig_tm_md.ucast_egress_port = port;
  }   
  table flep_processing {
    key = {
      hdr.flabels.label: exact;
    }
    actions = {
      flep_send;
      NoAction;
    }

    size = 256;
    default_action = NoAction;
  }
  
  action flep_decapsulation() {
    hdr.ethernet.ethernetType = hdr.flep.routing_type;
    hdr.flep.setInvalid();
    hdr.flabels.setInvalid();
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
    size = 256;
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
    size = 256;
    default_action = drop;
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

  apply{
    // for test
    fwd_port.apply();

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

    // 验证是否开启服务
    if (hdr.flep.isValid()) {
      is_verify_tbl.apply();
    }
    // 代表开启了服务
     if (meta.is_verify_start == 1) {
        // 进�?�密码验证服�?
        // key_match_tbl.apply();
        if (key_match_tbl.apply().hit){
          pkt_counter.apply(0);
        } else {
          pkt_counter.apply(1);
          keydatacache.apply(hdr.flep, 1);
          keyindexdatacache.apply(hdr.flep,1);
        }
    }

    // 基于标签进行转发
    if (hdr.flabels.isValid()) {
      flep_processing.apply();
      // 最后对标签长度做处理
      hdr.flep.label_depth = hdr.flep.label_depth - 1;
      hdr.flabels.setInvalid();
      // 长度为0后解封装
      if (hdr.flep.label_depth == 0 ){
        flep_decapsulation();
      }
    }  
    hdr.ethernet.srcAddr = ig_prsr_md.global_tstamp;
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
    pkt.emit(hdr.flep);
    pkt.emit(hdr.flabels);
    
  }
}


/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

  /***********************  H E A D E R S  ************************/

struct my_egress_headers_t {
  Ethernet_h ethernet;
}

  /********  G L O B A L   E G R E S S   M E T A D A T A  *********/

struct my_egress_metadata_t {
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
    transition parse_ethernet;
    
  }

  state parse_ethernet {
    pkt.extract(hdr.ethernet);
    transition accept;
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
  apply {
    hdr.ethernet.dstAddr = eg_prsr_md.global_tstamp;
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
    pkt.emit(hdr);
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
