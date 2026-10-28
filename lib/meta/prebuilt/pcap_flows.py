"""PCAP / PCAPNG packet decode L2-L4: IPs, conversations, flows, ports, protocol counts, byte totals (prebuilt,
SPECULATIVE -- no field here was ever GM-verified). Pure struct + stdlib ipaddress; the container walk (and the
gz/zstd/lz4/xz unwrap) follows prebuilt/pcap.py, but every record's BYTES are kept here.

Link layers (pcap network / pcapng IDB linktype, per interface):
  1 Ethernet (802.1Q 0x8100 / 802.1ad 0x88a8 / 0x9100 tags skipped, 802.3 length + LLC/SNAP), 0 NULL/BSD loopback
  (u32 AF in the WRITER's host order: read little-endian, swapped when > 0xffff, as Wireshark does), 108 LOOP (AF
  big-endian), 101/12/14/228/229 raw IP (version nibble), 113 Linux SLL (16 B, protocol @14), 276 SLL2 (20 B,
  protocol @0), 105 802.11 (data frames only: 24 B + addr4 when ToDS&FromDS + QoS 2 B + HTC 4 B when QoS&order;
  protected frames skipped; then LLC/SNAP aa aa 03), 127 radiotap (it_len u16 LE @2, then 802.11; FCS flag ignored).
  147-162 (USER0..15) and anything else: the packet counts toward packet/byte totals only.
  AF values: 2 = IPv4; 10, 24, 28, 30 = IPv6 (Linux / NetBSD-OpenBSD / FreeBSD / Darwin).
L3: IPv4 (IHL; L4 parsed only for the first fragment, offset 0), IPv6 (next-header chain 0/43/60/135/139/140 by
  hdr-ext-len, 44 fragment 8 B (offset != 0 -> no L4), 51 AH (len+2)*4; 59 stops). ARP = ethertype 0x0806 (no IPs).
L4: TCP (data offset; flags), UDP. ICMP = IP protocol 1 only (Wireshark's `icmp`); ICMPv6 (58) is its own count.

Field semantics (chosen to match tshark / capinfos, the fixture oracles):
  unique_ip_count = distinct IPv4+IPv6 addresses seen as src or dst (tshark -z endpoints,ip + endpoints,ipv6).
  unique_src_ips / unique_dst_ips (/ unique_ips) = JSON list, Python sorted() of the TEXT spellings (lexicographic:
    "10.0.0.10" before "10.0.0.2" -- what `sorted(set(...))` in a generator yields). IPv4 dotted quad, IPv6 RFC 5952
    lowercase compressed (ipaddress.compressed).
  top_talker_ip = the address in the most packets as src OR dst (tshark endpoints "Packets"); tie -> the lowest by
    (version, numeric value). top_source_ip / top_destination_ip: by src-only / dst-only counts, same tie rule.
  conversation_count = distinct unordered IP pairs (conv,ip + conv,ipv6). flow_count = distinct unordered 5-tuples
    over TCP and UDP only (conv,tcp + conv,udp; a reused port pair is ONE flow here).
  tcp/udp/icmp/icmpv6/arp/ipv6/ipv4 _packet_count = packets carrying that layer (tcp/udp: first fragment, header
    present). tcp_syn_count = SYN set and ACK clear (connection attempts; tcp_syn_flag_count = any SYN, synack
    separate).
  protocol_counts = JSON object {name: packets}, keys sorted: per packet its top decoded protocol among
    arp / tcp / udp / icmp / icmpv6 / igmp / gre / esp / ah / sctp / ospf, else "ip_<n>" for another IP protocol,
    else "other" (non-IP, non-ARP).
  dst_ports / src_ports (+ tcp_/udp_ variants) = sorted unique ints (TCP+UDP). most_common_dst_port: TCP+UDP dst
    port with the most packets, tie -> lowest.
  total_bytes = sum orig_len (capinfos "Data size", the on-wire length); captured_bytes = sum incl_len.
  capture_duration_seconds = max(ts) - min(ts) (capinfos "Capture duration"), the file's own resolution with
    trailing zeros dropped ("6.75", "3"); unique_*_count ints.
Not a capture (text, snoop, renamed impostor) -> "none"; a capture with no IP traffic -> 0 / [] / "none" for
top_talker_ip and most_common_dst_port."""
import collections
import ipaddress
import struct

_ALIASES = {
    "unique_ip_count": ["unique_ip_count", "unique_ips_count", "unique_ip_address_count", "distinct_ip_count",
                        "ip_address_count", "unique_address_count", "endpoint_count", "unique_endpoint_count",
                        "ip_count", "unique_host_count", "host_count"],
    "unique_ips": ["unique_ips", "unique_ip_addresses", "ip_addresses", "distinct_ips", "all_ips", "endpoints"],
    "unique_src_ips": ["unique_src_ips", "unique_source_ips", "src_ips", "source_ips", "source_ip_addresses",
                       "unique_src_ip_addresses", "distinct_src_ips"],
    "unique_dst_ips": ["unique_dst_ips", "unique_destination_ips", "dst_ips", "destination_ips",
                       "destination_ip_addresses", "unique_dst_ip_addresses", "distinct_dst_ips"],
    "unique_src_ip_count": ["unique_src_ip_count", "unique_source_ip_count", "src_ip_count", "source_ip_count"],
    "unique_dst_ip_count": ["unique_dst_ip_count", "unique_destination_ip_count", "dst_ip_count",
                            "destination_ip_count"],
    "top_talker_ip": ["top_talker_ip", "top_talker", "most_active_ip", "top_ip", "busiest_ip", "top_endpoint",
                      "most_frequent_ip", "most_common_ip"],
    "top_src_ip": ["top_source_ip", "top_src_ip", "most_common_src_ip", "most_common_source_ip",
                   "most_frequent_src_ip", "most_frequent_source_ip"],
    "top_dst_ip": ["top_destination_ip", "top_dst_ip", "most_common_dst_ip", "most_common_destination_ip",
                   "most_frequent_dst_ip", "most_frequent_destination_ip"],
    "conversation_count": ["conversation_count", "ip_conversation_count", "conversations", "unique_conversations",
                           "ip_pair_count", "unique_ip_pair_count", "conversations_count"],
    "flow_count": ["flow_count", "flows", "unique_flow_count", "five_tuple_count", "unique_5_tuple_count",
                   "connection_count", "tcp_udp_flow_count", "flows_count"],
    "tcp_packet_count": ["tcp_packet_count", "tcp_packets", "tcp_count", "num_tcp_packets", "tcp_frame_count"],
    "udp_packet_count": ["udp_packet_count", "udp_packets", "udp_count", "num_udp_packets", "udp_frame_count"],
    "icmp_packet_count": ["icmp_packet_count", "icmp_packets", "icmp_count", "num_icmp_packets"],
    "icmpv6_packet_count": ["icmpv6_packet_count", "icmpv6_packets", "icmpv6_count"],
    "arp_packet_count": ["arp_packet_count", "arp_packets", "arp_count", "num_arp_packets"],
    "ipv6_packet_count": ["ipv6_packet_count", "ipv6_packets", "ipv6_count", "num_ipv6_packets"],
    "ipv4_packet_count": ["ipv4_packet_count", "ipv4_packets", "ipv4_count", "ip_packet_count", "ip_packets"],
    "non_ip_packet_count": ["non_ip_packet_count", "non_ip_packets"],
    "protocol_counts": ["protocol_counts", "protocol_distribution", "protocol_histogram", "protocols_count",
                        "ip_protocol_counts", "protocol_hierarchy"],
    "dst_ports": ["dst_ports", "destination_ports", "unique_dst_ports", "unique_destination_ports", "dest_ports"],
    "src_ports": ["src_ports", "source_ports", "unique_src_ports", "unique_source_ports"],
    "tcp_dst_ports": ["tcp_dst_ports", "tcp_destination_ports", "tcp_ports"],
    "udp_dst_ports": ["udp_dst_ports", "udp_destination_ports", "udp_ports"],
    "dst_port_count": ["unique_dst_port_count", "dst_port_count", "unique_destination_port_count",
                       "destination_port_count"],
    "most_common_dst_port": ["most_common_dst_port", "most_common_destination_port", "top_dst_port",
                             "top_destination_port", "most_frequent_dst_port", "most_frequent_destination_port",
                             "most_common_port", "top_port"],
    "total_bytes": ["total_bytes", "total_byte_count", "total_packet_bytes", "data_size", "data_size_bytes",
                    "total_orig_len", "total_original_bytes", "total_wire_bytes", "total_length_bytes", "byte_count",
                    "bytes_total", "total_size_bytes"],
    "captured_bytes": ["captured_bytes", "total_captured_bytes", "captured_byte_count", "total_incl_len",
                       "total_caplen", "captured_data_size", "captured_size_bytes"],
    "tcp_syn_count": ["tcp_syn_count", "syn_count", "syn_packet_count", "tcp_syn_packets", "syn_packets",
                      "tcp_syn_packet_count"],
    "tcp_syn_flag_count": ["tcp_syn_flag_count", "syn_flag_count"],
    "tcp_synack_count": ["tcp_synack_count", "synack_count", "syn_ack_count", "tcp_syn_ack_count"],
    "tcp_rst_count": ["tcp_rst_count", "rst_count", "rst_packet_count"],
    "tcp_fin_count": ["tcp_fin_count", "fin_count", "fin_packet_count"],
    "duration": ["capture_duration_seconds", "capture_duration", "duration_seconds", "duration",
                 "capture_duration_secs", "time_span_seconds"],
}
# FIELDS must be a literal dict (ast-read): every _ALIASES name, for both fmts.
FIELDS = {
    ("pcap", "unique_ip_count"): "flow_value", ("pcapng", "unique_ip_count"): "flow_value",
    ("pcap", "unique_ips_count"): "flow_value", ("pcapng", "unique_ips_count"): "flow_value",
    ("pcap", "unique_ip_address_count"): "flow_value", ("pcapng", "unique_ip_address_count"): "flow_value",
    ("pcap", "distinct_ip_count"): "flow_value", ("pcapng", "distinct_ip_count"): "flow_value",
    ("pcap", "ip_address_count"): "flow_value", ("pcapng", "ip_address_count"): "flow_value",
    ("pcap", "unique_address_count"): "flow_value", ("pcapng", "unique_address_count"): "flow_value",
    ("pcap", "endpoint_count"): "flow_value", ("pcapng", "endpoint_count"): "flow_value",
    ("pcap", "unique_endpoint_count"): "flow_value", ("pcapng", "unique_endpoint_count"): "flow_value",
    ("pcap", "ip_count"): "flow_value", ("pcapng", "ip_count"): "flow_value",
    ("pcap", "unique_host_count"): "flow_value", ("pcapng", "unique_host_count"): "flow_value",
    ("pcap", "host_count"): "flow_value", ("pcapng", "host_count"): "flow_value",
    ("pcap", "unique_ips"): "flow_value", ("pcapng", "unique_ips"): "flow_value",
    ("pcap", "unique_ip_addresses"): "flow_value", ("pcapng", "unique_ip_addresses"): "flow_value",
    ("pcap", "ip_addresses"): "flow_value", ("pcapng", "ip_addresses"): "flow_value",
    ("pcap", "distinct_ips"): "flow_value", ("pcapng", "distinct_ips"): "flow_value",
    ("pcap", "all_ips"): "flow_value", ("pcapng", "all_ips"): "flow_value",
    ("pcap", "endpoints"): "flow_value", ("pcapng", "endpoints"): "flow_value",
    ("pcap", "unique_src_ips"): "flow_value", ("pcapng", "unique_src_ips"): "flow_value",
    ("pcap", "unique_source_ips"): "flow_value", ("pcapng", "unique_source_ips"): "flow_value",
    ("pcap", "src_ips"): "flow_value", ("pcapng", "src_ips"): "flow_value",
    ("pcap", "source_ips"): "flow_value", ("pcapng", "source_ips"): "flow_value",
    ("pcap", "source_ip_addresses"): "flow_value", ("pcapng", "source_ip_addresses"): "flow_value",
    ("pcap", "unique_src_ip_addresses"): "flow_value", ("pcapng", "unique_src_ip_addresses"): "flow_value",
    ("pcap", "distinct_src_ips"): "flow_value", ("pcapng", "distinct_src_ips"): "flow_value",
    ("pcap", "unique_dst_ips"): "flow_value", ("pcapng", "unique_dst_ips"): "flow_value",
    ("pcap", "unique_destination_ips"): "flow_value", ("pcapng", "unique_destination_ips"): "flow_value",
    ("pcap", "dst_ips"): "flow_value", ("pcapng", "dst_ips"): "flow_value",
    ("pcap", "destination_ips"): "flow_value", ("pcapng", "destination_ips"): "flow_value",
    ("pcap", "destination_ip_addresses"): "flow_value", ("pcapng", "destination_ip_addresses"): "flow_value",
    ("pcap", "unique_dst_ip_addresses"): "flow_value", ("pcapng", "unique_dst_ip_addresses"): "flow_value",
    ("pcap", "distinct_dst_ips"): "flow_value", ("pcapng", "distinct_dst_ips"): "flow_value",
    ("pcap", "unique_src_ip_count"): "flow_value", ("pcapng", "unique_src_ip_count"): "flow_value",
    ("pcap", "unique_source_ip_count"): "flow_value", ("pcapng", "unique_source_ip_count"): "flow_value",
    ("pcap", "src_ip_count"): "flow_value", ("pcapng", "src_ip_count"): "flow_value",
    ("pcap", "source_ip_count"): "flow_value", ("pcapng", "source_ip_count"): "flow_value",
    ("pcap", "unique_dst_ip_count"): "flow_value", ("pcapng", "unique_dst_ip_count"): "flow_value",
    ("pcap", "unique_destination_ip_count"): "flow_value", ("pcapng", "unique_destination_ip_count"): "flow_value",
    ("pcap", "dst_ip_count"): "flow_value", ("pcapng", "dst_ip_count"): "flow_value",
    ("pcap", "destination_ip_count"): "flow_value", ("pcapng", "destination_ip_count"): "flow_value",
    ("pcap", "top_talker_ip"): "flow_value", ("pcapng", "top_talker_ip"): "flow_value",
    ("pcap", "top_talker"): "flow_value", ("pcapng", "top_talker"): "flow_value",
    ("pcap", "most_active_ip"): "flow_value", ("pcapng", "most_active_ip"): "flow_value",
    ("pcap", "top_ip"): "flow_value", ("pcapng", "top_ip"): "flow_value",
    ("pcap", "busiest_ip"): "flow_value", ("pcapng", "busiest_ip"): "flow_value",
    ("pcap", "top_endpoint"): "flow_value", ("pcapng", "top_endpoint"): "flow_value",
    ("pcap", "most_frequent_ip"): "flow_value", ("pcapng", "most_frequent_ip"): "flow_value",
    ("pcap", "most_common_ip"): "flow_value", ("pcapng", "most_common_ip"): "flow_value",
    ("pcap", "top_source_ip"): "flow_value", ("pcapng", "top_source_ip"): "flow_value",
    ("pcap", "top_src_ip"): "flow_value", ("pcapng", "top_src_ip"): "flow_value",
    ("pcap", "most_common_src_ip"): "flow_value", ("pcapng", "most_common_src_ip"): "flow_value",
    ("pcap", "most_common_source_ip"): "flow_value", ("pcapng", "most_common_source_ip"): "flow_value",
    ("pcap", "most_frequent_src_ip"): "flow_value", ("pcapng", "most_frequent_src_ip"): "flow_value",
    ("pcap", "most_frequent_source_ip"): "flow_value", ("pcapng", "most_frequent_source_ip"): "flow_value",
    ("pcap", "top_destination_ip"): "flow_value", ("pcapng", "top_destination_ip"): "flow_value",
    ("pcap", "top_dst_ip"): "flow_value", ("pcapng", "top_dst_ip"): "flow_value",
    ("pcap", "most_common_dst_ip"): "flow_value", ("pcapng", "most_common_dst_ip"): "flow_value",
    ("pcap", "most_common_destination_ip"): "flow_value", ("pcapng", "most_common_destination_ip"): "flow_value",
    ("pcap", "most_frequent_dst_ip"): "flow_value", ("pcapng", "most_frequent_dst_ip"): "flow_value",
    ("pcap", "most_frequent_destination_ip"): "flow_value",
    ("pcapng", "most_frequent_destination_ip"): "flow_value",
    ("pcap", "conversation_count"): "flow_value", ("pcapng", "conversation_count"): "flow_value",
    ("pcap", "ip_conversation_count"): "flow_value", ("pcapng", "ip_conversation_count"): "flow_value",
    ("pcap", "conversations"): "flow_value", ("pcapng", "conversations"): "flow_value",
    ("pcap", "unique_conversations"): "flow_value", ("pcapng", "unique_conversations"): "flow_value",
    ("pcap", "ip_pair_count"): "flow_value", ("pcapng", "ip_pair_count"): "flow_value",
    ("pcap", "unique_ip_pair_count"): "flow_value", ("pcapng", "unique_ip_pair_count"): "flow_value",
    ("pcap", "conversations_count"): "flow_value", ("pcapng", "conversations_count"): "flow_value",
    ("pcap", "flow_count"): "flow_value", ("pcapng", "flow_count"): "flow_value",
    ("pcap", "flows"): "flow_value", ("pcapng", "flows"): "flow_value",
    ("pcap", "unique_flow_count"): "flow_value", ("pcapng", "unique_flow_count"): "flow_value",
    ("pcap", "five_tuple_count"): "flow_value", ("pcapng", "five_tuple_count"): "flow_value",
    ("pcap", "unique_5_tuple_count"): "flow_value", ("pcapng", "unique_5_tuple_count"): "flow_value",
    ("pcap", "connection_count"): "flow_value", ("pcapng", "connection_count"): "flow_value",
    ("pcap", "tcp_udp_flow_count"): "flow_value", ("pcapng", "tcp_udp_flow_count"): "flow_value",
    ("pcap", "flows_count"): "flow_value", ("pcapng", "flows_count"): "flow_value",
    ("pcap", "tcp_packet_count"): "flow_value", ("pcapng", "tcp_packet_count"): "flow_value",
    ("pcap", "tcp_packets"): "flow_value", ("pcapng", "tcp_packets"): "flow_value",
    ("pcap", "tcp_count"): "flow_value", ("pcapng", "tcp_count"): "flow_value",
    ("pcap", "num_tcp_packets"): "flow_value", ("pcapng", "num_tcp_packets"): "flow_value",
    ("pcap", "tcp_frame_count"): "flow_value", ("pcapng", "tcp_frame_count"): "flow_value",
    ("pcap", "udp_packet_count"): "flow_value", ("pcapng", "udp_packet_count"): "flow_value",
    ("pcap", "udp_packets"): "flow_value", ("pcapng", "udp_packets"): "flow_value",
    ("pcap", "udp_count"): "flow_value", ("pcapng", "udp_count"): "flow_value",
    ("pcap", "num_udp_packets"): "flow_value", ("pcapng", "num_udp_packets"): "flow_value",
    ("pcap", "udp_frame_count"): "flow_value", ("pcapng", "udp_frame_count"): "flow_value",
    ("pcap", "icmp_packet_count"): "flow_value", ("pcapng", "icmp_packet_count"): "flow_value",
    ("pcap", "icmp_packets"): "flow_value", ("pcapng", "icmp_packets"): "flow_value",
    ("pcap", "icmp_count"): "flow_value", ("pcapng", "icmp_count"): "flow_value",
    ("pcap", "num_icmp_packets"): "flow_value", ("pcapng", "num_icmp_packets"): "flow_value",
    ("pcap", "icmpv6_packet_count"): "flow_value", ("pcapng", "icmpv6_packet_count"): "flow_value",
    ("pcap", "icmpv6_packets"): "flow_value", ("pcapng", "icmpv6_packets"): "flow_value",
    ("pcap", "icmpv6_count"): "flow_value", ("pcapng", "icmpv6_count"): "flow_value",
    ("pcap", "arp_packet_count"): "flow_value", ("pcapng", "arp_packet_count"): "flow_value",
    ("pcap", "arp_packets"): "flow_value", ("pcapng", "arp_packets"): "flow_value",
    ("pcap", "arp_count"): "flow_value", ("pcapng", "arp_count"): "flow_value",
    ("pcap", "num_arp_packets"): "flow_value", ("pcapng", "num_arp_packets"): "flow_value",
    ("pcap", "ipv6_packet_count"): "flow_value", ("pcapng", "ipv6_packet_count"): "flow_value",
    ("pcap", "ipv6_packets"): "flow_value", ("pcapng", "ipv6_packets"): "flow_value",
    ("pcap", "ipv6_count"): "flow_value", ("pcapng", "ipv6_count"): "flow_value",
    ("pcap", "num_ipv6_packets"): "flow_value", ("pcapng", "num_ipv6_packets"): "flow_value",
    ("pcap", "ipv4_packet_count"): "flow_value", ("pcapng", "ipv4_packet_count"): "flow_value",
    ("pcap", "ipv4_packets"): "flow_value", ("pcapng", "ipv4_packets"): "flow_value",
    ("pcap", "ipv4_count"): "flow_value", ("pcapng", "ipv4_count"): "flow_value",
    ("pcap", "ip_packet_count"): "flow_value", ("pcapng", "ip_packet_count"): "flow_value",
    ("pcap", "ip_packets"): "flow_value", ("pcapng", "ip_packets"): "flow_value",
    ("pcap", "non_ip_packet_count"): "flow_value", ("pcapng", "non_ip_packet_count"): "flow_value",
    ("pcap", "non_ip_packets"): "flow_value", ("pcapng", "non_ip_packets"): "flow_value",
    ("pcap", "protocol_counts"): "flow_value", ("pcapng", "protocol_counts"): "flow_value",
    ("pcap", "protocol_distribution"): "flow_value", ("pcapng", "protocol_distribution"): "flow_value",
    ("pcap", "protocol_histogram"): "flow_value", ("pcapng", "protocol_histogram"): "flow_value",
    ("pcap", "protocols_count"): "flow_value", ("pcapng", "protocols_count"): "flow_value",
    ("pcap", "ip_protocol_counts"): "flow_value", ("pcapng", "ip_protocol_counts"): "flow_value",
    ("pcap", "protocol_hierarchy"): "flow_value", ("pcapng", "protocol_hierarchy"): "flow_value",
    ("pcap", "dst_ports"): "flow_value", ("pcapng", "dst_ports"): "flow_value",
    ("pcap", "destination_ports"): "flow_value", ("pcapng", "destination_ports"): "flow_value",
    ("pcap", "unique_dst_ports"): "flow_value", ("pcapng", "unique_dst_ports"): "flow_value",
    ("pcap", "unique_destination_ports"): "flow_value", ("pcapng", "unique_destination_ports"): "flow_value",
    ("pcap", "dest_ports"): "flow_value", ("pcapng", "dest_ports"): "flow_value",
    ("pcap", "src_ports"): "flow_value", ("pcapng", "src_ports"): "flow_value",
    ("pcap", "source_ports"): "flow_value", ("pcapng", "source_ports"): "flow_value",
    ("pcap", "unique_src_ports"): "flow_value", ("pcapng", "unique_src_ports"): "flow_value",
    ("pcap", "unique_source_ports"): "flow_value", ("pcapng", "unique_source_ports"): "flow_value",
    ("pcap", "tcp_dst_ports"): "flow_value", ("pcapng", "tcp_dst_ports"): "flow_value",
    ("pcap", "tcp_destination_ports"): "flow_value", ("pcapng", "tcp_destination_ports"): "flow_value",
    ("pcap", "tcp_ports"): "flow_value", ("pcapng", "tcp_ports"): "flow_value",
    ("pcap", "udp_dst_ports"): "flow_value", ("pcapng", "udp_dst_ports"): "flow_value",
    ("pcap", "udp_destination_ports"): "flow_value", ("pcapng", "udp_destination_ports"): "flow_value",
    ("pcap", "udp_ports"): "flow_value", ("pcapng", "udp_ports"): "flow_value",
    ("pcap", "unique_dst_port_count"): "flow_value", ("pcapng", "unique_dst_port_count"): "flow_value",
    ("pcap", "dst_port_count"): "flow_value", ("pcapng", "dst_port_count"): "flow_value",
    ("pcap", "unique_destination_port_count"): "flow_value",
    ("pcapng", "unique_destination_port_count"): "flow_value",
    ("pcap", "destination_port_count"): "flow_value", ("pcapng", "destination_port_count"): "flow_value",
    ("pcap", "most_common_dst_port"): "flow_value", ("pcapng", "most_common_dst_port"): "flow_value",
    ("pcap", "most_common_destination_port"): "flow_value", ("pcapng", "most_common_destination_port"): "flow_value",
    ("pcap", "top_dst_port"): "flow_value", ("pcapng", "top_dst_port"): "flow_value",
    ("pcap", "top_destination_port"): "flow_value", ("pcapng", "top_destination_port"): "flow_value",
    ("pcap", "most_frequent_dst_port"): "flow_value", ("pcapng", "most_frequent_dst_port"): "flow_value",
    ("pcap", "most_frequent_destination_port"): "flow_value",
    ("pcapng", "most_frequent_destination_port"): "flow_value",
    ("pcap", "most_common_port"): "flow_value", ("pcapng", "most_common_port"): "flow_value",
    ("pcap", "top_port"): "flow_value", ("pcapng", "top_port"): "flow_value",
    ("pcap", "total_bytes"): "flow_value", ("pcapng", "total_bytes"): "flow_value",
    ("pcap", "total_byte_count"): "flow_value", ("pcapng", "total_byte_count"): "flow_value",
    ("pcap", "total_packet_bytes"): "flow_value", ("pcapng", "total_packet_bytes"): "flow_value",
    ("pcap", "data_size"): "flow_value", ("pcapng", "data_size"): "flow_value",
    ("pcap", "data_size_bytes"): "flow_value", ("pcapng", "data_size_bytes"): "flow_value",
    ("pcap", "total_orig_len"): "flow_value", ("pcapng", "total_orig_len"): "flow_value",
    ("pcap", "total_original_bytes"): "flow_value", ("pcapng", "total_original_bytes"): "flow_value",
    ("pcap", "total_wire_bytes"): "flow_value", ("pcapng", "total_wire_bytes"): "flow_value",
    ("pcap", "total_length_bytes"): "flow_value", ("pcapng", "total_length_bytes"): "flow_value",
    ("pcap", "byte_count"): "flow_value", ("pcapng", "byte_count"): "flow_value",
    ("pcap", "bytes_total"): "flow_value", ("pcapng", "bytes_total"): "flow_value",
    ("pcap", "total_size_bytes"): "flow_value", ("pcapng", "total_size_bytes"): "flow_value",
    ("pcap", "captured_bytes"): "flow_value", ("pcapng", "captured_bytes"): "flow_value",
    ("pcap", "total_captured_bytes"): "flow_value", ("pcapng", "total_captured_bytes"): "flow_value",
    ("pcap", "captured_byte_count"): "flow_value", ("pcapng", "captured_byte_count"): "flow_value",
    ("pcap", "total_incl_len"): "flow_value", ("pcapng", "total_incl_len"): "flow_value",
    ("pcap", "total_caplen"): "flow_value", ("pcapng", "total_caplen"): "flow_value",
    ("pcap", "captured_data_size"): "flow_value", ("pcapng", "captured_data_size"): "flow_value",
    ("pcap", "captured_size_bytes"): "flow_value", ("pcapng", "captured_size_bytes"): "flow_value",
    ("pcap", "tcp_syn_count"): "flow_value", ("pcapng", "tcp_syn_count"): "flow_value",
    ("pcap", "syn_count"): "flow_value", ("pcapng", "syn_count"): "flow_value",
    ("pcap", "syn_packet_count"): "flow_value", ("pcapng", "syn_packet_count"): "flow_value",
    ("pcap", "tcp_syn_packets"): "flow_value", ("pcapng", "tcp_syn_packets"): "flow_value",
    ("pcap", "syn_packets"): "flow_value", ("pcapng", "syn_packets"): "flow_value",
    ("pcap", "tcp_syn_packet_count"): "flow_value", ("pcapng", "tcp_syn_packet_count"): "flow_value",
    ("pcap", "tcp_syn_flag_count"): "flow_value", ("pcapng", "tcp_syn_flag_count"): "flow_value",
    ("pcap", "syn_flag_count"): "flow_value", ("pcapng", "syn_flag_count"): "flow_value",
    ("pcap", "tcp_synack_count"): "flow_value", ("pcapng", "tcp_synack_count"): "flow_value",
    ("pcap", "synack_count"): "flow_value", ("pcapng", "synack_count"): "flow_value",
    ("pcap", "syn_ack_count"): "flow_value", ("pcapng", "syn_ack_count"): "flow_value",
    ("pcap", "tcp_syn_ack_count"): "flow_value", ("pcapng", "tcp_syn_ack_count"): "flow_value",
    ("pcap", "tcp_rst_count"): "flow_value", ("pcapng", "tcp_rst_count"): "flow_value",
    ("pcap", "rst_count"): "flow_value", ("pcapng", "rst_count"): "flow_value",
    ("pcap", "rst_packet_count"): "flow_value", ("pcapng", "rst_packet_count"): "flow_value",
    ("pcap", "tcp_fin_count"): "flow_value", ("pcapng", "tcp_fin_count"): "flow_value",
    ("pcap", "fin_count"): "flow_value", ("pcapng", "fin_count"): "flow_value",
    ("pcap", "fin_packet_count"): "flow_value", ("pcapng", "fin_packet_count"): "flow_value",
    ("pcap", "capture_duration_seconds"): "flow_value", ("pcapng", "capture_duration_seconds"): "flow_value",
    ("pcap", "capture_duration"): "flow_value", ("pcapng", "capture_duration"): "flow_value",
    ("pcap", "duration_seconds"): "flow_value", ("pcapng", "duration_seconds"): "flow_value",
    ("pcap", "duration"): "flow_value", ("pcapng", "duration"): "flow_value",
    ("pcap", "capture_duration_secs"): "flow_value", ("pcapng", "capture_duration_secs"): "flow_value",
    ("pcap", "time_span_seconds"): "flow_value", ("pcapng", "time_span_seconds"): "flow_value",
}
_FIELD_KIND = {f: kind for kind, names in _ALIASES.items() for f in names}

_PCAP_MAGIC = {0xA1B2C3D4: (16, 6), 0xA1B23C4D: (16, 9), 0xA1B2CD34: (24, 6)}
_AF6 = (10, 24, 28, 30)
_PROTO_NAMES = {1: "icmp", 2: "igmp", 6: "tcp", 17: "udp", 47: "gre", 50: "esp", 51: "ah", 58: "icmpv6",
                89: "ospf", 132: "sctp"}
_V6_EXT = (0, 43, 60, 135, 139, 140)


def _records(b):
    """[(linktype, sec, frac, res, incl_len, orig_len, bytes)] of a classic pcap or pcapng, or None."""
    if len(b) >= 28 and bytes(b[:4]) == b"\x0a\x0d\x0d\x0a":
        return _records_ng(b)
    if len(b) < 24:
        return None
    for e in "<>":
        magic, = struct.unpack_from(e + "I", b, 0)
        if magic in _PCAP_MAGIC:
            break
    else:
        return None
    rh, digits = _PCAP_MAGIC[magic]
    lt = struct.unpack_from(e + "I", b, 20)[0] & 0x0FFFFFFF
    out, off = [], 24
    while off + rh <= len(b):
        sec, frac, incl, orig = struct.unpack_from(e + "IIII", b, off)
        if off + rh + incl > len(b):
            break
        out.append((lt, sec, frac, 10 ** digits, incl, orig, b[off + rh:off + rh + incl]))
        off += rh + incl
    return out


def _records_ng(b):
    out, off, e, idbs, seen_shb = [], 0, None, [], False
    while off + 12 <= len(b):
        if bytes(b[off:off + 4]) == b"\x0a\x0d\x0d\x0a":
            bom = bytes(b[off + 8:off + 12])
            e = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">" if bom == b"\x1a\x2b\x3c\x4d" else None
            if e is None:
                break
            idbs, seen_shb = [], True
        if e is None:
            break
        btype, blen = struct.unpack_from(e + "II", b, off)
        if blen < 12 or blen % 4 or off + blen > len(b):
            break
        body, end = off + 8, off + blen - 4
        if btype == 1 and end - body >= 8:
            lt, = struct.unpack_from(e + "H", b, body)
            res, o = 10 ** 6, body + 8
            while o + 4 <= end:                      # options: if_tsresol (9) sets the tick rate
                code, ln = struct.unpack_from(e + "HH", b, o)
                if code == 0 or o + 4 + ln > end:
                    break
                if code == 9 and ln:
                    v = b[o + 4]
                    res = (1 << (v & 0x7F)) if v & 0x80 else 10 ** (v & 0x7F)
                o += 4 + ((ln + 3) & ~3)
            idbs.append((lt, res))
        elif btype in (6, 2) and end - body >= 20:
            if btype == 6:
                ifid, hi, lo, cap, orig = struct.unpack_from(e + "IIIII", b, body)
            else:
                ifid, _d, hi, lo, cap, orig = struct.unpack_from(e + "HHIIII", b, body)
            lt, res = idbs[ifid] if ifid < len(idbs) else (None, 10 ** 6)
            ts = (hi << 32) | lo
            cap = min(cap, end - body - 20)
            out.append((lt, ts // res, ts % res, res, cap, orig, b[body + 20:body + 20 + cap]))
        elif btype == 3 and end - body >= 4:
            orig, = struct.unpack_from(e + "I", b, body)
            lt = idbs[0][0] if idbs else None
            cap = min(orig, end - body - 4)
            out.append((lt, None, 0, 1, cap, orig, b[body + 4:body + 4 + cap]))
        off += blen
    return out if seen_shb else None


def _ethertype_payload(d, o):
    """Ethernet-style dispatch from offset o (at the type/length field): (ethertype, payload offset) or None."""
    while o + 2 <= len(d):
        et, = struct.unpack_from("!H", d, o)
        if et in (0x8100, 0x88A8, 0x9100):
            o += 4
            continue
        if et <= 1500:     # 802.3 length: LLC, SNAP carries an ethertype
            if d[o + 2:o + 5] == b"\xaa\xaa\x03" and o + 10 <= len(d):
                return struct.unpack_from("!H", d, o + 8)[0], o + 10
            return None
        return et, o + 2
    return None


def _dot11(d, o):
    if o + 24 > len(d):
        return None
    fc0, fc1 = d[o], d[o + 1]
    if (fc0 >> 2) & 3 != 2 or fc1 & 0x40:     # not a data frame, or protected
        return None
    sub = fc0 >> 4
    if sub & 0x4:                               # null / no-data subtypes
        return None
    hl = 24 + (6 if (fc1 & 3) == 3 else 0)
    if sub & 0x8:
        hl += 2 + (4 if fc1 & 0x80 else 0)
    p = o + hl
    if d[p:p + 3] == b"\xaa\xaa\x03" and p + 8 <= len(d):
        return struct.unpack_from("!H", d, p + 6)[0], p + 8
    return None


def _l3(lt, d):
    """(ethertype, offset of the L3 header) for a record, or None (not decodable / non-IP link)."""
    if lt == 1:
        return _ethertype_payload(d, 12)
    if lt in (0, 108):
        if len(d) < 4:
            return None
        af, = struct.unpack_from(">I" if lt == 108 else "<I", d, 0)
        if af > 0xFFFF:
            af = struct.unpack_from(">I", d, 0)[0]
        return (0x0800, 4) if af == 2 else (0x86DD, 4) if af in _AF6 else None
    if lt in (101, 12, 14, 228, 229):
        v = d[0] >> 4 if d else 0
        return (0x0800, 0) if v == 4 else (0x86DD, 0) if v == 6 else None
    if lt == 113:
        return (struct.unpack_from("!H", d, 14)[0], 16) if len(d) >= 16 else None
    if lt == 276:
        return (struct.unpack_from("!H", d, 0)[0], 20) if len(d) >= 20 else None
    if lt == 105:
        return _dot11(d, 0)
    if lt == 127:
        if len(d) < 4:
            return None
        rl, = struct.unpack_from("<H", d, 2)
        return _dot11(d, rl)
    return None


def _ip(d, o, et):
    """(src, dst, proto, l4 offset or None) of an IPv4/IPv6 header at o, or None."""
    if et == 0x0800:
        if o + 20 > len(d) or d[o] >> 4 != 4:
            return None
        ihl = (d[o] & 0x0F) * 4
        fo, = struct.unpack_from("!H", d, o + 6)
        src = ipaddress.IPv4Address(bytes(d[o + 12:o + 16]))
        dst = ipaddress.IPv4Address(bytes(d[o + 16:o + 20]))
        return src, dst, d[o + 9], (o + ihl if fo & 0x1FFF == 0 and ihl >= 20 else None)
    if o + 40 > len(d) or d[o] >> 4 != 6:
        return None
    src = ipaddress.IPv6Address(bytes(d[o + 8:o + 24]))
    dst = ipaddress.IPv6Address(bytes(d[o + 24:o + 40]))
    nh, p = d[o + 6], o + 40
    for _ in range(16):
        if nh in _V6_EXT and p + 2 <= len(d):
            nh, p = d[p], p + (d[p + 1] + 1) * 8
        elif nh == 44 and p + 8 <= len(d):
            fo, = struct.unpack_from("!H", d, p + 2)
            nh, p = d[p], p + 8
            if fo >> 3:
                return src, dst, nh, None
        elif nh == 51 and p + 2 <= len(d):
            nh, p = d[p], p + (d[p + 1] + 2) * 4
        else:
            break
    return src, dst, nh, (p if p <= len(d) else None)


def _analyze(recs):
    st = {"packets": len(recs), "total": 0, "captured": 0, "times": [], "ips": set(), "src": collections.Counter(),
          "dst": collections.Counter(), "talk": collections.Counter(), "pairs": set(), "flows": set(),
          "proto": collections.Counter(), "dports": collections.Counter(), "sports": set(), "tcp_dports": set(),
          "udp_dports": set(), "n": collections.Counter()}
    n = st["n"]
    for lt, sec, frac, res, incl, orig, d in recs:
        st["total"] += orig
        st["captured"] += incl
        if sec is not None:
            st["times"].append((sec * res + frac, res))
        try:
            l3 = _l3(lt, d)
            ip = _ip(d, l3[1], l3[0]) if l3 and l3[0] in (0x0800, 0x86DD) else None
        except (struct.error, IndexError, ValueError):
            l3, ip = None, None
        if l3 and l3[0] == 0x0806:
            n["arp"] += 1
            st["proto"]["arp"] += 1
            continue
        if ip is None:
            n["non_ip"] += 1
            st["proto"]["other"] += 1
            continue
        src, dst, proto, l4 = ip
        n["ipv6" if src.version == 6 else "ipv4"] += 1
        st["ips"].update((src, dst))
        st["src"][src] += 1
        st["dst"][dst] += 1
        st["talk"][src] += 1
        if dst != src:
            st["talk"][dst] += 1
        st["pairs"].add(frozenset((src, dst)))
        name = _PROTO_NAMES.get(proto, "ip_%d" % proto)
        st["proto"][name] += 1
        if proto in (1, 58):
            n[name] += 1
        if proto in (6, 17) and l4 is not None and l4 + (20 if proto == 6 else 8) <= len(d):
            sp, dp = struct.unpack_from("!HH", d, l4)
            n[name] += 1
            st["dports"][dp] += 1
            st["sports"].add(sp)
            st["tcp_dports" if proto == 6 else "udp_dports"].add(dp)
            st["flows"].add((proto, frozenset(((src, sp), (dst, dp)))))
            if proto == 6:
                fl = d[l4 + 13]
                syn, ack = fl & 0x02, fl & 0x10
                n["syn"] += bool(syn and not ack)
                n["synflag"] += bool(syn)
                n["synack"] += bool(syn and ack)
                n["rst"] += bool(fl & 0x04)
                n["fin"] += bool(fl & 0x01)
    return st


def _ipkey(a):
    return (a.version, int(a))


def _top(counter):
    if not counter:
        return "none"
    best = max(counter.values())
    return str(min((a for a, c in counter.items() if c == best), key=_ipkey))


def _duration(times):
    if not times:
        return "none"
    res = max(r for _, r in times)
    ticks = [t * (res // r) if res % r == 0 else t * res // r for t, r in times]
    span = max(ticks) - min(ticks)
    whole, frac = divmod(span, res)
    if not frac:
        return whole
    digits = len(str(res - 1)) if res == 10 ** len(str(res - 1)) else 9
    if digits == 9 and res != 10 ** 9:
        frac = frac * 10 ** 9 // res
    return ("%d.%0*d" % (whole, digits, frac)).rstrip("0")


def _parse(data):
    from .pcap import _unwrap
    recs = _records(data)
    if recs is None:
        inner = _unwrap(data)
        recs = _records(inner) if inner else None
    return recs


def flow_value(data, ctx):
    """pcap.<field> / pcapng.<field>: L2-L4 decode aggregates (see module doc)."""
    if not data:
        return None
    try:
        recs = _parse(data)
    except (struct.error, ValueError, OverflowError):
        recs = None
    if recs is None:
        return "none"
    kind = _FIELD_KIND.get((ctx or {}).get("field") or "")
    if kind is None:
        return None
    st = _analyze(recs)
    n = st["n"]
    txt = lambda s: sorted(str(a) for a in s)   # noqa: E731 -- sorted() of the spellings (see module doc)
    simple = {
        "unique_ip_count": lambda: len(st["ips"]),
        "unique_ips": lambda: txt(st["ips"]),
        "unique_src_ips": lambda: txt(st["src"]),
        "unique_dst_ips": lambda: txt(st["dst"]),
        "unique_src_ip_count": lambda: len(st["src"]),
        "unique_dst_ip_count": lambda: len(st["dst"]),
        "top_talker_ip": lambda: _top(st["talk"]),
        "top_src_ip": lambda: _top(st["src"]),
        "top_dst_ip": lambda: _top(st["dst"]),
        "conversation_count": lambda: len(st["pairs"]),
        "flow_count": lambda: len(st["flows"]),
        "tcp_packet_count": lambda: n["tcp"],
        "udp_packet_count": lambda: n["udp"],
        "icmp_packet_count": lambda: n["icmp"],
        "icmpv6_packet_count": lambda: n["icmpv6"],
        "arp_packet_count": lambda: n["arp"],
        "ipv6_packet_count": lambda: n["ipv6"],
        "ipv4_packet_count": lambda: n["ipv4"],
        "non_ip_packet_count": lambda: n["non_ip"] + n["arp"],
        "protocol_counts": lambda: dict(sorted(st["proto"].items())),
        "dst_ports": lambda: sorted(st["dports"]),
        "src_ports": lambda: sorted(st["sports"]),
        "tcp_dst_ports": lambda: sorted(st["tcp_dports"]),
        "udp_dst_ports": lambda: sorted(st["udp_dports"]),
        "dst_port_count": lambda: len(st["dports"]),
        "most_common_dst_port": lambda: (min(p for p, c in st["dports"].items() if c == max(st["dports"].values()))
                                         if st["dports"] else "none"),
        "total_bytes": lambda: st["total"],
        "captured_bytes": lambda: st["captured"],
        "tcp_syn_count": lambda: n["syn"],
        "tcp_syn_flag_count": lambda: n["synflag"],
        "tcp_synack_count": lambda: n["synack"],
        "tcp_rst_count": lambda: n["rst"],
        "tcp_fin_count": lambda: n["fin"],
        "duration": lambda: _duration(st["times"]),
    }
    return simple[kind]()
