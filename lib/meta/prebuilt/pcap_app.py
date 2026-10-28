"""PCAP / PCAPNG application-layer indicators: DNS, HTTP/1.x, TLS ClientHello (SNI / ALPN / JA3) + Certificate,
FTP USER/PASS, SMTP MAIL FROM / RCPT TO, ICMP payload strings (prebuilt, SPECULATIVE -- never GM-verified).
The container walk and the L2-L4 decode are pcap_flows' (_parse / _l3 / _ip): every link layer it knows works here.

DNS  = UDP with port 53 on either side, and TCP/53 (reassembled, u16 length-prefixed messages). Opcode QUERY only.
  Names: labels joined by '.', compression pointers followed, lowercased, no trailing dot (tshark dns.qry.name).
  dns_query_names = question names of every DNS message (queries and responses), sorted unique.
  dns_query_count = query messages (QR=0); most_queried_domain = most frequent question name over QUERIES, tie ->
  lexicographically smallest. dns_answer_ips = A/AAAA rdata of the ANSWER section (text, sorted() like pcap_flows).
  dns_nxdomain_count = responses with rcode 3.
HTTP = any TCP payload whose first line is `<METHOD> <uri> HTTP/1.x` (request) or `HTTP/1.x NNN` (response); headers
  read from that same segment (retransmissions of the same seq+len counted once). Host / User-Agent / Content-Type
  values verbatim (trimmed). http_first_request_url = 'http://' + Host + URI of the earliest request (an absolute
  proxy URI is kept as is). http_status_codes = sorted unique ints.
TLS  = per TCP direction the stream is reassembled by seq; records of type 22 are joined, handshake messages walked
  until ChangeCipherSpec. ClientHello: SNI (ext 0, lowercased), ALPN (16), version = highest supported_versions
  (43) entry else client_version, spelled 'TLSv1.2'. JA3 = md5 of 'client_version,ciphers,extensions,groups,
  point_formats' (decimal, '-'-joined, GREASE 0x?a?a removed, extensions in wire order) -- tshark tls.handshake.ja3.
  Certificate (TLS <= 1.2 only; 1.3 certs are encrypted): the first DER of a chain is the leaf; its sha256 / CNs are
  rendered by prebuilt/x509.py (lowercase hex of the whole DER, no colons; the LAST CN attribute).
FTP  = client lines to TCP/21: USER / PASS args (verbatim), commands, RETR/STOR/... file args.
SMTP = client lines to 25/465/587/2525: the address inside <...> of MAIL FROM: / RCPT TO:, HELO/EHLO argument.
ICMP = echo request/reply (and ICMPv6 128/129) data: printable-ASCII runs of >= 4 bytes, stripped.
Lists are sorted + de-duplicated (JSON); *_first = the value of the earliest packet; *_count = int. Absent indicator
-> "none" (counts -> 0). Not a capture (text, renamed impostor) -> "none"."""
import collections
import hashlib
import ipaddress
import re
import struct

from .pcap_flows import _ip, _l3
from .pcap_flows import _parse as _flows_parse

_ALIASES = {
 "dns_query_names": [
  "dns_query_names",
  "dns_queries",
  "dns_queried_domains",
  "dns_domains",
  "queried_domains",
  "dns_qnames",
  "dns_query_domains",
  "dns_names",
  "unique_dns_queries",
  "unique_dns_query_names"
 ],
 "dns_query_first": [
  "dns_query_name_first",
  "dns_query_first",
  "first_dns_query",
  "first_dns_query_name",
  "first_queried_domain"
 ],
 "dns_query_count": [
  "dns_query_count",
  "dns_queries_count",
  "dns_query_packet_count",
  "dns_request_count"
 ],
 "dns_query_name_count": [
  "dns_query_names_count",
  "unique_dns_query_count",
  "unique_dns_name_count",
  "dns_unique_query_count"
 ],
 "dns_response_count": [
  "dns_response_count",
  "dns_responses_count"
 ],
 "dns_answer_ips": [
  "dns_answer_ips",
  "dns_answer_addresses",
  "dns_resolved_ips",
  "resolved_ips",
  "dns_a_records",
  "dns_answers",
  "dns_answer_ip_addresses"
 ],
 "dns_answer_ip_count": [
  "dns_answer_ips_count",
  "dns_answer_ip_count",
  "resolved_ip_count"
 ],
 "dns_cname_targets": [
  "dns_cname_targets",
  "dns_cnames",
  "dns_cname_records",
  "dns_answer_cnames"
 ],
 "dns_qtypes": [
  "dns_qtypes",
  "dns_query_types",
  "dns_record_types"
 ],
 "most_queried_domain": [
  "most_queried_domain",
  "dns_most_queried_domain",
  "most_common_dns_query",
  "top_dns_query",
  "most_queried_dns_name",
  "most_frequent_dns_query",
  "top_queried_domain"
 ],
 "dns_nxdomain_count": [
  "dns_nxdomain_count",
  "nxdomain_count",
  "dns_nxdomain_response_count"
 ],
 "dns_nxdomain_names": [
  "dns_nxdomain_names",
  "nxdomain_names",
  "nxdomain_domains",
  "dns_nxdomain_domains"
 ],
 "http_hosts": [
  "http_hosts",
  "http_host_headers",
  "http_host_names",
  "http_hostnames"
 ],
 "http_host_first": [
  "http_host_first",
  "first_http_host"
 ],
 "http_host_count": [
  "http_hosts_count",
  "http_host_count"
 ],
 "http_user_agents": [
  "http_user_agents",
  "user_agents",
  "http_user_agent_strings",
  "http_uas"
 ],
 "http_user_agent_first": [
  "http_user_agent_first",
  "http_user_agent",
  "first_http_user_agent",
  "user_agent"
 ],
 "http_user_agent_count": [
  "http_user_agents_count",
  "http_user_agent_count"
 ],
 "http_request_uris": [
  "http_request_uris",
  "http_uris",
  "http_request_paths",
  "http_paths",
  "request_uris"
 ],
 "http_request_uri_first": [
  "http_request_uri_first",
  "first_http_request_uri",
  "first_http_uri"
 ],
 "http_methods": [
  "http_methods",
  "http_request_methods"
 ],
 "http_request_count": [
  "http_request_count",
  "http_requests_count",
  "http_requests"
 ],
 "http_status_codes": [
  "http_status_codes",
  "http_response_codes",
  "http_response_status_codes"
 ],
 "http_response_count": [
  "http_response_count",
  "http_responses_count"
 ],
 "http_content_types": [
  "http_content_types",
  "http_response_content_types"
 ],
 "http_first_request_url": [
  "http_first_request_url",
  "first_http_request_url",
  "http_request_url_first",
  "first_request_url",
  "first_http_url",
  "http_url_first"
 ],
 "http_request_urls": [
  "http_request_urls",
  "http_urls",
  "http_full_urls",
  "request_urls"
 ],
 "tls_sni_names": [
  "tls_sni_names",
  "tls_server_names",
  "tls_sni",
  "sni_names",
  "tls_snis",
  "server_name_indications",
  "tls_sni_hostnames",
  "sni_hostnames"
 ],
 "tls_sni_first": [
  "tls_sni_first",
  "first_tls_sni",
  "tls_server_name",
  "first_sni",
  "tls_sni_name"
 ],
 "tls_sni_count": [
  "tls_sni_count",
  "tls_sni_names_count",
  "sni_count"
 ],
 "tls_client_hello_count": [
  "tls_client_hello_count",
  "client_hello_count",
  "tls_clienthello_count"
 ],
 "tls_alpn_protocols": [
  "tls_alpn_protocols",
  "tls_alpn",
  "alpn_protocols",
  "tls_alpn_names"
 ],
 "tls_versions": [
  "tls_versions",
  "tls_client_versions",
  "tls_handshake_versions"
 ],
 "tls_version_first": [
  "tls_version",
  "tls_client_version",
  "tls_version_first",
  "tls_handshake_version"
 ],
 "tls_ja3_md5": [
  "tls_ja3_md5",
  "ja3_md5",
  "tls_ja3",
  "ja3",
  "ja3_hashes",
  "tls_ja3_hashes",
  "tls_ja3_md5s"
 ],
 "tls_ja3_first": [
  "tls_ja3_md5_first",
  "tls_ja3_first",
  "ja3_first",
  "first_ja3"
 ],
 "tls_ja3_strings": [
  "tls_ja3_strings",
  "ja3_strings",
  "tls_ja3_full",
  "ja3_full"
 ],
 "tls_cert_sha256": [
  "tls_cert_sha256",
  "tls_certificate_sha256",
  "tls_cert_sha256_fingerprint",
  "tls_certificate_fingerprint_sha256",
  "tls_cert_fingerprint_sha256",
  "server_cert_sha256",
  "tls_leaf_cert_sha256"
 ],
 "tls_cert_sha256s": [
  "tls_cert_sha256s",
  "tls_certificate_sha256s",
  "tls_cert_fingerprints_sha256",
  "tls_certificate_fingerprints"
 ],
 "tls_cert_subject_cn": [
  "tls_cert_subject_cn",
  "tls_certificate_subject_cn",
  "server_cert_subject_cn",
  "tls_cert_cn",
  "tls_leaf_cert_subject_cn"
 ],
 "tls_cert_subject_cns": [
  "tls_cert_subject_cns",
  "tls_certificate_subject_cns",
  "tls_cert_cns"
 ],
 "tls_cert_issuer_cn": [
  "tls_cert_issuer_cn",
  "tls_certificate_issuer_cn"
 ],
 "tls_cert_count": [
  "tls_cert_count",
  "tls_certificate_count"
 ],
 "ftp_usernames": [
  "ftp_usernames",
  "ftp_users",
  "ftp_user_names",
  "ftp_user"
 ],
 "ftp_username_first": [
  "ftp_username",
  "ftp_username_first",
  "first_ftp_username"
 ],
 "ftp_passwords": [
  "ftp_passwords",
  "ftp_pass",
  "ftp_password_list"
 ],
 "ftp_password_first": [
  "ftp_password",
  "ftp_password_first",
  "first_ftp_password"
 ],
 "ftp_commands": [
  "ftp_commands",
  "ftp_request_commands"
 ],
 "ftp_filenames": [
  "ftp_filenames",
  "ftp_file_names",
  "ftp_retr_files",
  "ftp_transferred_files",
  "ftp_stor_files"
 ],
 "smtp_mail_from": [
  "smtp_mail_from",
  "smtp_senders",
  "smtp_mail_from_addresses",
  "smtp_envelope_from",
  "mail_from_addresses"
 ],
 "smtp_mail_from_first": [
  "smtp_mail_from_first",
  "first_smtp_mail_from",
  "smtp_sender"
 ],
 "smtp_rcpt_to": [
  "smtp_rcpt_to",
  "smtp_recipients",
  "smtp_rcpt_to_addresses",
  "smtp_envelope_to",
  "rcpt_to_addresses"
 ],
 "smtp_rcpt_to_first": [
  "smtp_rcpt_to_first",
  "first_smtp_rcpt_to",
  "smtp_recipient"
 ],
 "smtp_helo": [
  "smtp_helo",
  "smtp_ehlo",
  "smtp_helo_names",
  "smtp_helo_hostnames"
 ],
 "icmp_payload_strings": [
  "icmp_payload_strings",
  "icmp_payloads",
  "icmp_data_strings",
  "icmp_strings"
 ],
 "icmp_payload_first": [
  "icmp_payload_first",
  "first_icmp_payload",
  "icmp_payload",
  "icmp_payload_string"
 ]
}
FIELDS = {
    ("pcap", "dns_query_names"): "app_value", ("pcapng", "dns_query_names"): "app_value",
    ("pcap", "dns_queries"): "app_value", ("pcapng", "dns_queries"): "app_value",
    ("pcap", "dns_queried_domains"): "app_value", ("pcapng", "dns_queried_domains"): "app_value",
    ("pcap", "dns_domains"): "app_value", ("pcapng", "dns_domains"): "app_value",
    ("pcap", "queried_domains"): "app_value", ("pcapng", "queried_domains"): "app_value",
    ("pcap", "dns_qnames"): "app_value", ("pcapng", "dns_qnames"): "app_value",
    ("pcap", "dns_query_domains"): "app_value", ("pcapng", "dns_query_domains"): "app_value",
    ("pcap", "dns_names"): "app_value", ("pcapng", "dns_names"): "app_value",
    ("pcap", "unique_dns_queries"): "app_value", ("pcapng", "unique_dns_queries"): "app_value",
    ("pcap", "unique_dns_query_names"): "app_value", ("pcapng", "unique_dns_query_names"): "app_value",
    ("pcap", "dns_query_name_first"): "app_value", ("pcapng", "dns_query_name_first"): "app_value",
    ("pcap", "dns_query_first"): "app_value", ("pcapng", "dns_query_first"): "app_value",
    ("pcap", "first_dns_query"): "app_value", ("pcapng", "first_dns_query"): "app_value",
    ("pcap", "first_dns_query_name"): "app_value", ("pcapng", "first_dns_query_name"): "app_value",
    ("pcap", "first_queried_domain"): "app_value", ("pcapng", "first_queried_domain"): "app_value",
    ("pcap", "dns_query_count"): "app_value", ("pcapng", "dns_query_count"): "app_value",
    ("pcap", "dns_queries_count"): "app_value", ("pcapng", "dns_queries_count"): "app_value",
    ("pcap", "dns_query_packet_count"): "app_value", ("pcapng", "dns_query_packet_count"): "app_value",
    ("pcap", "dns_request_count"): "app_value", ("pcapng", "dns_request_count"): "app_value",
    ("pcap", "dns_query_names_count"): "app_value", ("pcapng", "dns_query_names_count"): "app_value",
    ("pcap", "unique_dns_query_count"): "app_value", ("pcapng", "unique_dns_query_count"): "app_value",
    ("pcap", "unique_dns_name_count"): "app_value", ("pcapng", "unique_dns_name_count"): "app_value",
    ("pcap", "dns_unique_query_count"): "app_value", ("pcapng", "dns_unique_query_count"): "app_value",
    ("pcap", "dns_response_count"): "app_value", ("pcapng", "dns_response_count"): "app_value",
    ("pcap", "dns_responses_count"): "app_value", ("pcapng", "dns_responses_count"): "app_value",
    ("pcap", "dns_answer_ips"): "app_value", ("pcapng", "dns_answer_ips"): "app_value",
    ("pcap", "dns_answer_addresses"): "app_value", ("pcapng", "dns_answer_addresses"): "app_value",
    ("pcap", "dns_resolved_ips"): "app_value", ("pcapng", "dns_resolved_ips"): "app_value",
    ("pcap", "resolved_ips"): "app_value", ("pcapng", "resolved_ips"): "app_value",
    ("pcap", "dns_a_records"): "app_value", ("pcapng", "dns_a_records"): "app_value",
    ("pcap", "dns_answers"): "app_value", ("pcapng", "dns_answers"): "app_value",
    ("pcap", "dns_answer_ip_addresses"): "app_value", ("pcapng", "dns_answer_ip_addresses"): "app_value",
    ("pcap", "dns_answer_ips_count"): "app_value", ("pcapng", "dns_answer_ips_count"): "app_value",
    ("pcap", "dns_answer_ip_count"): "app_value", ("pcapng", "dns_answer_ip_count"): "app_value",
    ("pcap", "resolved_ip_count"): "app_value", ("pcapng", "resolved_ip_count"): "app_value",
    ("pcap", "dns_cname_targets"): "app_value", ("pcapng", "dns_cname_targets"): "app_value",
    ("pcap", "dns_cnames"): "app_value", ("pcapng", "dns_cnames"): "app_value",
    ("pcap", "dns_cname_records"): "app_value", ("pcapng", "dns_cname_records"): "app_value",
    ("pcap", "dns_answer_cnames"): "app_value", ("pcapng", "dns_answer_cnames"): "app_value",
    ("pcap", "dns_qtypes"): "app_value", ("pcapng", "dns_qtypes"): "app_value",
    ("pcap", "dns_query_types"): "app_value", ("pcapng", "dns_query_types"): "app_value",
    ("pcap", "dns_record_types"): "app_value", ("pcapng", "dns_record_types"): "app_value",
    ("pcap", "most_queried_domain"): "app_value", ("pcapng", "most_queried_domain"): "app_value",
    ("pcap", "dns_most_queried_domain"): "app_value", ("pcapng", "dns_most_queried_domain"): "app_value",
    ("pcap", "most_common_dns_query"): "app_value", ("pcapng", "most_common_dns_query"): "app_value",
    ("pcap", "top_dns_query"): "app_value", ("pcapng", "top_dns_query"): "app_value",
    ("pcap", "most_queried_dns_name"): "app_value", ("pcapng", "most_queried_dns_name"): "app_value",
    ("pcap", "most_frequent_dns_query"): "app_value", ("pcapng", "most_frequent_dns_query"): "app_value",
    ("pcap", "top_queried_domain"): "app_value", ("pcapng", "top_queried_domain"): "app_value",
    ("pcap", "dns_nxdomain_count"): "app_value", ("pcapng", "dns_nxdomain_count"): "app_value",
    ("pcap", "nxdomain_count"): "app_value", ("pcapng", "nxdomain_count"): "app_value",
    ("pcap", "dns_nxdomain_response_count"): "app_value", ("pcapng", "dns_nxdomain_response_count"): "app_value",
    ("pcap", "dns_nxdomain_names"): "app_value", ("pcapng", "dns_nxdomain_names"): "app_value",
    ("pcap", "nxdomain_names"): "app_value", ("pcapng", "nxdomain_names"): "app_value",
    ("pcap", "nxdomain_domains"): "app_value", ("pcapng", "nxdomain_domains"): "app_value",
    ("pcap", "dns_nxdomain_domains"): "app_value", ("pcapng", "dns_nxdomain_domains"): "app_value",
    ("pcap", "http_hosts"): "app_value", ("pcapng", "http_hosts"): "app_value",
    ("pcap", "http_host_headers"): "app_value", ("pcapng", "http_host_headers"): "app_value",
    ("pcap", "http_host_names"): "app_value", ("pcapng", "http_host_names"): "app_value",
    ("pcap", "http_hostnames"): "app_value", ("pcapng", "http_hostnames"): "app_value",
    ("pcap", "http_host_first"): "app_value", ("pcapng", "http_host_first"): "app_value",
    ("pcap", "first_http_host"): "app_value", ("pcapng", "first_http_host"): "app_value",
    ("pcap", "http_hosts_count"): "app_value", ("pcapng", "http_hosts_count"): "app_value",
    ("pcap", "http_host_count"): "app_value", ("pcapng", "http_host_count"): "app_value",
    ("pcap", "http_user_agents"): "app_value", ("pcapng", "http_user_agents"): "app_value",
    ("pcap", "user_agents"): "app_value", ("pcapng", "user_agents"): "app_value",
    ("pcap", "http_user_agent_strings"): "app_value", ("pcapng", "http_user_agent_strings"): "app_value",
    ("pcap", "http_uas"): "app_value", ("pcapng", "http_uas"): "app_value",
    ("pcap", "http_user_agent_first"): "app_value", ("pcapng", "http_user_agent_first"): "app_value",
    ("pcap", "http_user_agent"): "app_value", ("pcapng", "http_user_agent"): "app_value",
    ("pcap", "first_http_user_agent"): "app_value", ("pcapng", "first_http_user_agent"): "app_value",
    ("pcap", "user_agent"): "app_value", ("pcapng", "user_agent"): "app_value",
    ("pcap", "http_user_agents_count"): "app_value", ("pcapng", "http_user_agents_count"): "app_value",
    ("pcap", "http_user_agent_count"): "app_value", ("pcapng", "http_user_agent_count"): "app_value",
    ("pcap", "http_request_uris"): "app_value", ("pcapng", "http_request_uris"): "app_value",
    ("pcap", "http_uris"): "app_value", ("pcapng", "http_uris"): "app_value",
    ("pcap", "http_request_paths"): "app_value", ("pcapng", "http_request_paths"): "app_value",
    ("pcap", "http_paths"): "app_value", ("pcapng", "http_paths"): "app_value",
    ("pcap", "request_uris"): "app_value", ("pcapng", "request_uris"): "app_value",
    ("pcap", "http_request_uri_first"): "app_value", ("pcapng", "http_request_uri_first"): "app_value",
    ("pcap", "first_http_request_uri"): "app_value", ("pcapng", "first_http_request_uri"): "app_value",
    ("pcap", "first_http_uri"): "app_value", ("pcapng", "first_http_uri"): "app_value",
    ("pcap", "http_methods"): "app_value", ("pcapng", "http_methods"): "app_value",
    ("pcap", "http_request_methods"): "app_value", ("pcapng", "http_request_methods"): "app_value",
    ("pcap", "http_request_count"): "app_value", ("pcapng", "http_request_count"): "app_value",
    ("pcap", "http_requests_count"): "app_value", ("pcapng", "http_requests_count"): "app_value",
    ("pcap", "http_requests"): "app_value", ("pcapng", "http_requests"): "app_value",
    ("pcap", "http_status_codes"): "app_value", ("pcapng", "http_status_codes"): "app_value",
    ("pcap", "http_response_codes"): "app_value", ("pcapng", "http_response_codes"): "app_value",
    ("pcap", "http_response_status_codes"): "app_value", ("pcapng", "http_response_status_codes"): "app_value",
    ("pcap", "http_response_count"): "app_value", ("pcapng", "http_response_count"): "app_value",
    ("pcap", "http_responses_count"): "app_value", ("pcapng", "http_responses_count"): "app_value",
    ("pcap", "http_content_types"): "app_value", ("pcapng", "http_content_types"): "app_value",
    ("pcap", "http_response_content_types"): "app_value", ("pcapng", "http_response_content_types"): "app_value",
    ("pcap", "http_first_request_url"): "app_value", ("pcapng", "http_first_request_url"): "app_value",
    ("pcap", "first_http_request_url"): "app_value", ("pcapng", "first_http_request_url"): "app_value",
    ("pcap", "http_request_url_first"): "app_value", ("pcapng", "http_request_url_first"): "app_value",
    ("pcap", "first_request_url"): "app_value", ("pcapng", "first_request_url"): "app_value",
    ("pcap", "first_http_url"): "app_value", ("pcapng", "first_http_url"): "app_value",
    ("pcap", "http_url_first"): "app_value", ("pcapng", "http_url_first"): "app_value",
    ("pcap", "http_request_urls"): "app_value", ("pcapng", "http_request_urls"): "app_value",
    ("pcap", "http_urls"): "app_value", ("pcapng", "http_urls"): "app_value",
    ("pcap", "http_full_urls"): "app_value", ("pcapng", "http_full_urls"): "app_value",
    ("pcap", "request_urls"): "app_value", ("pcapng", "request_urls"): "app_value",
    ("pcap", "tls_sni_names"): "app_value", ("pcapng", "tls_sni_names"): "app_value",
    ("pcap", "tls_server_names"): "app_value", ("pcapng", "tls_server_names"): "app_value",
    ("pcap", "tls_sni"): "app_value", ("pcapng", "tls_sni"): "app_value",
    ("pcap", "sni_names"): "app_value", ("pcapng", "sni_names"): "app_value",
    ("pcap", "tls_snis"): "app_value", ("pcapng", "tls_snis"): "app_value",
    ("pcap", "server_name_indications"): "app_value", ("pcapng", "server_name_indications"): "app_value",
    ("pcap", "tls_sni_hostnames"): "app_value", ("pcapng", "tls_sni_hostnames"): "app_value",
    ("pcap", "sni_hostnames"): "app_value", ("pcapng", "sni_hostnames"): "app_value",
    ("pcap", "tls_sni_first"): "app_value", ("pcapng", "tls_sni_first"): "app_value",
    ("pcap", "first_tls_sni"): "app_value", ("pcapng", "first_tls_sni"): "app_value",
    ("pcap", "tls_server_name"): "app_value", ("pcapng", "tls_server_name"): "app_value",
    ("pcap", "first_sni"): "app_value", ("pcapng", "first_sni"): "app_value",
    ("pcap", "tls_sni_name"): "app_value", ("pcapng", "tls_sni_name"): "app_value",
    ("pcap", "tls_sni_count"): "app_value", ("pcapng", "tls_sni_count"): "app_value",
    ("pcap", "tls_sni_names_count"): "app_value", ("pcapng", "tls_sni_names_count"): "app_value",
    ("pcap", "sni_count"): "app_value", ("pcapng", "sni_count"): "app_value",
    ("pcap", "tls_client_hello_count"): "app_value", ("pcapng", "tls_client_hello_count"): "app_value",
    ("pcap", "client_hello_count"): "app_value", ("pcapng", "client_hello_count"): "app_value",
    ("pcap", "tls_clienthello_count"): "app_value", ("pcapng", "tls_clienthello_count"): "app_value",
    ("pcap", "tls_alpn_protocols"): "app_value", ("pcapng", "tls_alpn_protocols"): "app_value",
    ("pcap", "tls_alpn"): "app_value", ("pcapng", "tls_alpn"): "app_value",
    ("pcap", "alpn_protocols"): "app_value", ("pcapng", "alpn_protocols"): "app_value",
    ("pcap", "tls_alpn_names"): "app_value", ("pcapng", "tls_alpn_names"): "app_value",
    ("pcap", "tls_versions"): "app_value", ("pcapng", "tls_versions"): "app_value",
    ("pcap", "tls_client_versions"): "app_value", ("pcapng", "tls_client_versions"): "app_value",
    ("pcap", "tls_handshake_versions"): "app_value", ("pcapng", "tls_handshake_versions"): "app_value",
    ("pcap", "tls_version"): "app_value", ("pcapng", "tls_version"): "app_value",
    ("pcap", "tls_client_version"): "app_value", ("pcapng", "tls_client_version"): "app_value",
    ("pcap", "tls_version_first"): "app_value", ("pcapng", "tls_version_first"): "app_value",
    ("pcap", "tls_handshake_version"): "app_value", ("pcapng", "tls_handshake_version"): "app_value",
    ("pcap", "tls_ja3_md5"): "app_value", ("pcapng", "tls_ja3_md5"): "app_value",
    ("pcap", "ja3_md5"): "app_value", ("pcapng", "ja3_md5"): "app_value",
    ("pcap", "tls_ja3"): "app_value", ("pcapng", "tls_ja3"): "app_value",
    ("pcap", "ja3"): "app_value", ("pcapng", "ja3"): "app_value",
    ("pcap", "ja3_hashes"): "app_value", ("pcapng", "ja3_hashes"): "app_value",
    ("pcap", "tls_ja3_hashes"): "app_value", ("pcapng", "tls_ja3_hashes"): "app_value",
    ("pcap", "tls_ja3_md5s"): "app_value", ("pcapng", "tls_ja3_md5s"): "app_value",
    ("pcap", "tls_ja3_md5_first"): "app_value", ("pcapng", "tls_ja3_md5_first"): "app_value",
    ("pcap", "tls_ja3_first"): "app_value", ("pcapng", "tls_ja3_first"): "app_value",
    ("pcap", "ja3_first"): "app_value", ("pcapng", "ja3_first"): "app_value",
    ("pcap", "first_ja3"): "app_value", ("pcapng", "first_ja3"): "app_value",
    ("pcap", "tls_ja3_strings"): "app_value", ("pcapng", "tls_ja3_strings"): "app_value",
    ("pcap", "ja3_strings"): "app_value", ("pcapng", "ja3_strings"): "app_value",
    ("pcap", "tls_ja3_full"): "app_value", ("pcapng", "tls_ja3_full"): "app_value",
    ("pcap", "ja3_full"): "app_value", ("pcapng", "ja3_full"): "app_value",
    ("pcap", "tls_cert_sha256"): "app_value", ("pcapng", "tls_cert_sha256"): "app_value",
    ("pcap", "tls_certificate_sha256"): "app_value", ("pcapng", "tls_certificate_sha256"): "app_value",
    ("pcap", "tls_cert_sha256_fingerprint"): "app_value", ("pcapng", "tls_cert_sha256_fingerprint"): "app_value",
    ("pcap", "tls_certificate_fingerprint_sha256"): "app_value", ("pcapng", "tls_certificate_fingerprint_sha256"): "app_value",
    ("pcap", "tls_cert_fingerprint_sha256"): "app_value", ("pcapng", "tls_cert_fingerprint_sha256"): "app_value",
    ("pcap", "server_cert_sha256"): "app_value", ("pcapng", "server_cert_sha256"): "app_value",
    ("pcap", "tls_leaf_cert_sha256"): "app_value", ("pcapng", "tls_leaf_cert_sha256"): "app_value",
    ("pcap", "tls_cert_sha256s"): "app_value", ("pcapng", "tls_cert_sha256s"): "app_value",
    ("pcap", "tls_certificate_sha256s"): "app_value", ("pcapng", "tls_certificate_sha256s"): "app_value",
    ("pcap", "tls_cert_fingerprints_sha256"): "app_value", ("pcapng", "tls_cert_fingerprints_sha256"): "app_value",
    ("pcap", "tls_certificate_fingerprints"): "app_value", ("pcapng", "tls_certificate_fingerprints"): "app_value",
    ("pcap", "tls_cert_subject_cn"): "app_value", ("pcapng", "tls_cert_subject_cn"): "app_value",
    ("pcap", "tls_certificate_subject_cn"): "app_value", ("pcapng", "tls_certificate_subject_cn"): "app_value",
    ("pcap", "server_cert_subject_cn"): "app_value", ("pcapng", "server_cert_subject_cn"): "app_value",
    ("pcap", "tls_cert_cn"): "app_value", ("pcapng", "tls_cert_cn"): "app_value",
    ("pcap", "tls_leaf_cert_subject_cn"): "app_value", ("pcapng", "tls_leaf_cert_subject_cn"): "app_value",
    ("pcap", "tls_cert_subject_cns"): "app_value", ("pcapng", "tls_cert_subject_cns"): "app_value",
    ("pcap", "tls_certificate_subject_cns"): "app_value", ("pcapng", "tls_certificate_subject_cns"): "app_value",
    ("pcap", "tls_cert_cns"): "app_value", ("pcapng", "tls_cert_cns"): "app_value",
    ("pcap", "tls_cert_issuer_cn"): "app_value", ("pcapng", "tls_cert_issuer_cn"): "app_value",
    ("pcap", "tls_certificate_issuer_cn"): "app_value", ("pcapng", "tls_certificate_issuer_cn"): "app_value",
    ("pcap", "tls_cert_count"): "app_value", ("pcapng", "tls_cert_count"): "app_value",
    ("pcap", "tls_certificate_count"): "app_value", ("pcapng", "tls_certificate_count"): "app_value",
    ("pcap", "ftp_usernames"): "app_value", ("pcapng", "ftp_usernames"): "app_value",
    ("pcap", "ftp_users"): "app_value", ("pcapng", "ftp_users"): "app_value",
    ("pcap", "ftp_user_names"): "app_value", ("pcapng", "ftp_user_names"): "app_value",
    ("pcap", "ftp_user"): "app_value", ("pcapng", "ftp_user"): "app_value",
    ("pcap", "ftp_username"): "app_value", ("pcapng", "ftp_username"): "app_value",
    ("pcap", "ftp_username_first"): "app_value", ("pcapng", "ftp_username_first"): "app_value",
    ("pcap", "first_ftp_username"): "app_value", ("pcapng", "first_ftp_username"): "app_value",
    ("pcap", "ftp_passwords"): "app_value", ("pcapng", "ftp_passwords"): "app_value",
    ("pcap", "ftp_pass"): "app_value", ("pcapng", "ftp_pass"): "app_value",
    ("pcap", "ftp_password_list"): "app_value", ("pcapng", "ftp_password_list"): "app_value",
    ("pcap", "ftp_password"): "app_value", ("pcapng", "ftp_password"): "app_value",
    ("pcap", "ftp_password_first"): "app_value", ("pcapng", "ftp_password_first"): "app_value",
    ("pcap", "first_ftp_password"): "app_value", ("pcapng", "first_ftp_password"): "app_value",
    ("pcap", "ftp_commands"): "app_value", ("pcapng", "ftp_commands"): "app_value",
    ("pcap", "ftp_request_commands"): "app_value", ("pcapng", "ftp_request_commands"): "app_value",
    ("pcap", "ftp_filenames"): "app_value", ("pcapng", "ftp_filenames"): "app_value",
    ("pcap", "ftp_file_names"): "app_value", ("pcapng", "ftp_file_names"): "app_value",
    ("pcap", "ftp_retr_files"): "app_value", ("pcapng", "ftp_retr_files"): "app_value",
    ("pcap", "ftp_transferred_files"): "app_value", ("pcapng", "ftp_transferred_files"): "app_value",
    ("pcap", "ftp_stor_files"): "app_value", ("pcapng", "ftp_stor_files"): "app_value",
    ("pcap", "smtp_mail_from"): "app_value", ("pcapng", "smtp_mail_from"): "app_value",
    ("pcap", "smtp_senders"): "app_value", ("pcapng", "smtp_senders"): "app_value",
    ("pcap", "smtp_mail_from_addresses"): "app_value", ("pcapng", "smtp_mail_from_addresses"): "app_value",
    ("pcap", "smtp_envelope_from"): "app_value", ("pcapng", "smtp_envelope_from"): "app_value",
    ("pcap", "mail_from_addresses"): "app_value", ("pcapng", "mail_from_addresses"): "app_value",
    ("pcap", "smtp_mail_from_first"): "app_value", ("pcapng", "smtp_mail_from_first"): "app_value",
    ("pcap", "first_smtp_mail_from"): "app_value", ("pcapng", "first_smtp_mail_from"): "app_value",
    ("pcap", "smtp_sender"): "app_value", ("pcapng", "smtp_sender"): "app_value",
    ("pcap", "smtp_rcpt_to"): "app_value", ("pcapng", "smtp_rcpt_to"): "app_value",
    ("pcap", "smtp_recipients"): "app_value", ("pcapng", "smtp_recipients"): "app_value",
    ("pcap", "smtp_rcpt_to_addresses"): "app_value", ("pcapng", "smtp_rcpt_to_addresses"): "app_value",
    ("pcap", "smtp_envelope_to"): "app_value", ("pcapng", "smtp_envelope_to"): "app_value",
    ("pcap", "rcpt_to_addresses"): "app_value", ("pcapng", "rcpt_to_addresses"): "app_value",
    ("pcap", "smtp_rcpt_to_first"): "app_value", ("pcapng", "smtp_rcpt_to_first"): "app_value",
    ("pcap", "first_smtp_rcpt_to"): "app_value", ("pcapng", "first_smtp_rcpt_to"): "app_value",
    ("pcap", "smtp_recipient"): "app_value", ("pcapng", "smtp_recipient"): "app_value",
    ("pcap", "smtp_helo"): "app_value", ("pcapng", "smtp_helo"): "app_value",
    ("pcap", "smtp_ehlo"): "app_value", ("pcapng", "smtp_ehlo"): "app_value",
    ("pcap", "smtp_helo_names"): "app_value", ("pcapng", "smtp_helo_names"): "app_value",
    ("pcap", "smtp_helo_hostnames"): "app_value", ("pcapng", "smtp_helo_hostnames"): "app_value",
    ("pcap", "icmp_payload_strings"): "app_value", ("pcapng", "icmp_payload_strings"): "app_value",
    ("pcap", "icmp_payloads"): "app_value", ("pcapng", "icmp_payloads"): "app_value",
    ("pcap", "icmp_data_strings"): "app_value", ("pcapng", "icmp_data_strings"): "app_value",
    ("pcap", "icmp_strings"): "app_value", ("pcapng", "icmp_strings"): "app_value",
    ("pcap", "icmp_payload_first"): "app_value", ("pcapng", "icmp_payload_first"): "app_value",
    ("pcap", "first_icmp_payload"): "app_value", ("pcapng", "first_icmp_payload"): "app_value",
    ("pcap", "icmp_payload"): "app_value", ("pcapng", "icmp_payload"): "app_value",
    ("pcap", "icmp_payload_string"): "app_value", ("pcapng", "icmp_payload_string"): "app_value",
}

_FIELD_KIND = {f: kind for kind, names in _ALIASES.items() for f in names}

_METHODS = (b"GET", b"POST", b"HEAD", b"PUT", b"DELETE", b"OPTIONS", b"PATCH", b"CONNECT", b"TRACE", b"PROPFIND")
_REQ = re.compile(rb"^(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH|CONNECT|TRACE|PROPFIND) (\S+) HTTP/1\.[01]\r?$")
_RESP = re.compile(rb"^HTTP/1\.[01] (\d{3})(?: [^\r\n]*)?\r?$")
_GREASE = frozenset(0x0A0A + 0x1010 * i for i in range(16))
_SMTP_PORTS = (25, 465, 587, 2525)
_PRINT = re.compile(rb"[\x20-\x7e]{4,}")


def _name(m, o, depth=0):
    """(label-decoded name, offset after the name in place) -- compression pointers followed, max 16 hops."""
    labels, end = [], None
    for _ in range(128):
        if o >= len(m):
            return None, None
        ln = m[o]
        if ln == 0:
            o += 1
            break
        if ln & 0xC0 == 0xC0:
            if o + 1 >= len(m) or depth > 16:
                return None, None
            if end is None:
                end = o + 2
            o = ((ln & 0x3F) << 8) | m[o + 1]
            depth += 1
            continue
        if ln & 0xC0 or o + 1 + ln > len(m):
            return None, None
        labels.append(bytes(m[o + 1:o + 1 + ln]).decode("latin-1"))
        o += 1 + ln
    else:
        return None, None
    return ".".join(labels).lower().rstrip("."), (end if end is not None else o)


def _dns(m, ts, st):
    """One DNS message (no TCP length prefix) into the accumulator."""
    if len(m) < 12:
        return
    _id, fl, qd, an, _ns, _ar = struct.unpack_from("!HHHHHH", m, 0)
    if fl & 0x7800:           # opcode != QUERY: not a lookup
        return
    resp = bool(fl & 0x8000)
    o, qnames = 12, []
    for _ in range(min(qd, 64)):
        n, o = _name(m, o)
        if n is None or o + 4 > len(m):
            return
        qt, = struct.unpack_from("!H", m, o)
        o += 4
        qnames.append(n)
        st["dns_names"].append((ts, n))
        st["qtypes"].add(qt)
        if not resp:
            st["dns_q"][n] += 1
    st["dns_resp" if resp else "dns_req"] += 1
    if not resp:
        return
    if fl & 0xF == 3:
        st["nx"] += 1
        st["nx_names"].update(qnames)
    for _ in range(min(an, 256)):
        n, o = _name(m, o)
        if n is None or o + 10 > len(m):
            return
        rt, _c, _ttl, rdl = struct.unpack_from("!HHIH", m, o)
        o += 10
        rd = m[o:o + rdl]
        if len(rd) < rdl:
            return
        if rt == 1 and rdl == 4:
            st["ans_ips"].add(ipaddress.IPv4Address(bytes(rd)))
        elif rt == 28 and rdl == 16:
            st["ans_ips"].add(ipaddress.IPv6Address(bytes(rd)))
        elif rt == 5:
            c, _x = _name(m, o)
            if c is not None:
                st["cnames"].add(c)
        o += rdl


def _headers(p, start):
    """{lower-name: [values]} of the header block that follows the start line (stops at the blank line)."""
    h = {}
    for line in p[start:].split(b"\n"):
        line = line.rstrip(b"\r")
        if not line:
            break
        k, sep, v = line.partition(b":")
        if sep:
            h.setdefault(k.strip().lower().decode("latin-1"), []).append(v.strip().decode("latin-1"))
    return h


def _http(p, ts, st):
    nl = p.find(b"\n")
    first = p[:nl if nl >= 0 else len(p)]
    m = _REQ.match(first)
    if m:
        h = _headers(p, nl + 1) if nl >= 0 else {}
        meth, uri = m.group(1).decode(), m.group(2).decode("latin-1")
        host = (h.get("host") or [None])[0]
        st["http_req"].append((ts, meth, uri, host, (h.get("user-agent") or [None])[0]))
        return
    m = _RESP.match(first)
    if m:
        h = _headers(p, nl + 1) if nl >= 0 else {}
        st["http_resp"].append((ts, int(m.group(1)), (h.get("content-type") or [None])[0]))


def _lines(p):
    return [ln.rstrip(b"\r").decode("latin-1") for ln in p.split(b"\n") if ln.strip()]


def _addr(arg):
    m = re.search(r"<([^>]*)>", arg)
    a = (m.group(1) if m else arg.split()[0] if arg.split() else "").strip()
    return a or None


def _client_text(p, ts, dport, st):
    if dport == 21:
        for ln in _lines(p):
            cmd, _s, arg = ln.partition(" ")
            cmd = cmd.upper()
            if not cmd.isalpha() or len(cmd) > 4:
                continue
            st["ftp_cmds"].add(cmd)
            if cmd == "USER":
                st["ftp_user"].append((ts, arg.strip()))
            elif cmd == "PASS":
                st["ftp_pass"].append((ts, arg.strip()))
            elif cmd in ("RETR", "STOR", "STOU", "APPE", "DELE") and arg.strip():
                st["ftp_files"].add(arg.strip())
    elif dport in _SMTP_PORTS:
        for ln in _lines(p):
            u = ln.upper()
            if u.startswith("MAIL FROM:"):
                a = _addr(ln[10:])
                if a:
                    st["mail_from"].append((ts, a))
            elif u.startswith("RCPT TO:"):
                a = _addr(ln[8:])
                if a:
                    st["rcpt_to"].append((ts, a))
            elif u.startswith(("HELO ", "EHLO ")):
                st["helo"].add(ln[5:].strip())


def _ext_list(b, o, end):
    """[(type, data)] of a ClientHello extensions block."""
    out = []
    while o + 4 <= end:
        t, ln = struct.unpack_from("!HH", b, o)
        if o + 4 + ln > end:
            break
        out.append((t, b[o + 4:o + 4 + ln]))
        o += 4 + ln
    return out


def _client_hello(b, ts, st):
    """b = ClientHello body (after the 4-byte handshake header)."""
    if len(b) < 38:
        return
    ver, = struct.unpack_from("!H", b, 0)
    o = 34
    o += 1 + b[o]                                      # session id
    if o + 2 > len(b):
        return
    cl, = struct.unpack_from("!H", b, o)
    ciphers = [c for c in struct.unpack_from("!%dH" % (cl // 2), b, o + 2)] if o + 2 + cl <= len(b) else []
    o += 2 + cl
    if o >= len(b):
        return
    o += 1 + b[o]                                      # compression methods
    exts = []
    if o + 2 <= len(b):
        el, = struct.unpack_from("!H", b, o)
        exts = _ext_list(b, o + 2, min(len(b), o + 2 + el))
    groups, fmts, sni, real_ver = [], [], None, ver
    for t, d in exts:
        if t == 0 and len(d) >= 5:                     # server_name list: type 0 host_name
            p = 2
            while p + 3 <= len(d):
                nt, nl = d[p], struct.unpack_from("!H", d, p + 1)[0]
                if nt == 0:
                    sni = bytes(d[p + 3:p + 3 + nl]).decode("latin-1").lower().rstrip(".")
                    break
                p += 3 + nl
        elif t == 16 and len(d) >= 2:                  # ALPN
            p = 2
            while p < len(d):
                ln = d[p]
                st["alpn"].add(bytes(d[p + 1:p + 1 + ln]).decode("latin-1"))
                p += 1 + ln
        elif t == 10 and len(d) >= 2:
            n, = struct.unpack_from("!H", d, 0)
            groups = list(struct.unpack_from("!%dH" % (min(n, len(d) - 2) // 2), d, 2))
        elif t == 11 and len(d) >= 1:
            fmts = list(d[1:1 + d[0]])
        elif t == 43 and len(d) >= 3:                  # supported_versions: highest non-GREASE
            vs = [v for v in struct.unpack_from("!%dH" % (d[0] // 2), d, 1) if v not in _GREASE]
            if vs:
                real_ver = max(vs)
    ja3 = "%d,%s,%s,%s,%s" % (ver, "-".join(str(c) for c in ciphers if c not in _GREASE),
                              "-".join(str(t) for t, _d in exts if t not in _GREASE),
                              "-".join(str(g) for g in groups if g not in _GREASE), "-".join(str(f) for f in fmts))
    st["hello"].append((ts, sni, real_ver, ja3))


def _certificates(b, st):
    """b = Certificate (TLS <= 1.2) body: u24 total, then u24-length DERs; the first is the leaf."""
    if len(b) < 3:
        return
    total = int.from_bytes(b[0:3], "big")
    o, end, chain = 3, min(len(b), 3 + total), []
    while o + 3 <= end:
        ln = int.from_bytes(b[o:o + 3], "big")
        if o + 3 + ln > end:
            break
        chain.append(bytes(b[o + 3:o + 3 + ln]))
        o += 3 + ln
    if chain:
        st["certs"].append(chain)


def _tls_stream(s, ts, st):
    """Walk the TLS records of one reassembled direction; handshake fragments are joined across records."""
    o, hs = 0, bytearray()
    while o + 5 <= len(s):
        ct, ver, ln = s[o], struct.unpack_from("!H", s, o + 1)[0], struct.unpack_from("!H", s, o + 3)[0]
        if ct not in (20, 21, 22, 23) or ver >> 8 != 3:
            break
        if ct == 22:
            hs += s[o + 5:o + 5 + ln]
        elif ct == 20:      # ChangeCipherSpec: what follows is encrypted
            o += 5 + ln
            break
        o += 5 + ln
    p = 0
    while p + 4 <= len(hs):
        t, ln = hs[p], int.from_bytes(hs[p + 1:p + 4], "big")
        body = bytes(hs[p + 4:p + 4 + ln])
        if t == 1:
            _client_hello(body, ts, st)
        elif t == 11:
            _certificates(body, st)
        elif t not in (2, 12, 13, 14, 15, 16, 4, 8):
            break
        p += 4 + ln


def _reassemble(segs):
    """Ordered, de-duplicated byte stream from [(seq, payload)] (overlaps keep the first copy)."""
    out, nxt = bytearray(), None
    for seq, p in sorted(segs, key=lambda x: x[0]):
        if nxt is None:
            nxt = seq
        if seq + len(p) <= nxt:
            continue
        if seq > nxt:               # a gap: stop (the missing bytes are not in the capture)
            break
        out += p[nxt - seq:]
        nxt = seq + len(p)
    return bytes(out)


def _analyze(recs):
    st = {"dns_names": [], "dns_q": collections.Counter(), "qtypes": set(), "dns_req": 0, "dns_resp": 0, "nx": 0,
          "nx_names": set(), "ans_ips": set(), "cnames": set(), "http_req": [], "http_resp": [], "hello": [],
          "alpn": set(), "certs": [], "ftp_user": [], "ftp_pass": [], "ftp_cmds": set(), "ftp_files": set(),
          "mail_from": [], "rcpt_to": [], "helo": set(), "smtp_auth": [], "icmp": []}
    streams, seen = collections.OrderedDict(), set()
    for i, (lt, sec, frac, res, _incl, _orig, d) in enumerate(recs):
        ts = (sec * res + frac) / res if sec is not None else float(i)
        ts = (ts, i)
        try:
            l3 = _l3(lt, d)
            ip = _ip(d, l3[1], l3[0]) if l3 and l3[0] in (0x0800, 0x86DD) else None
            if ip is None or ip[3] is None:
                continue
            src, dst, proto, l4 = ip
            if l3[0] == 0x0800:
                tot, = struct.unpack_from("!H", d, l3[1] + 2)
                end = min(len(d), l3[1] + tot) if tot >= 20 else len(d)
            else:
                pl, = struct.unpack_from("!H", d, l3[1] + 4)
                end = min(len(d), l3[1] + 40 + pl) if pl else len(d)
            if proto == 17 and l4 + 8 <= end:
                sp, dp = struct.unpack_from("!HH", d, l4)
                if 53 in (sp, dp):
                    _dns(bytes(d[l4 + 8:end]), ts, st)
            elif proto == 6 and l4 + 20 <= end:
                sp, dp, seq = struct.unpack_from("!HHI", d, l4)
                p = bytes(d[l4 + (d[l4 + 12] >> 4) * 4:end])
                if not p:
                    continue
                key = (src, sp, dst, dp)
                streams.setdefault(key, [ts, []])[1].append((seq, p))
                if (key, seq, len(p)) in seen:        # a retransmission: counted once
                    continue
                seen.add((key, seq, len(p)))
                if p.startswith(_METHODS) or p.startswith(b"HTTP/1."):
                    _http(p, ts, st)
                else:
                    _client_text(p, ts, dp, st)
            elif proto in (1, 58) and l4 + 8 <= end and d[l4] in ((0, 8) if proto == 1 else (128, 129)):
                for s in _PRINT.findall(bytes(d[l4 + 8:end])):
                    st["icmp"].append((ts, s.decode("ascii").strip()))
        except (struct.error, IndexError, ValueError):
            continue
    for key, (ts, segs) in streams.items():
        try:
            s = _reassemble(segs)
            if 53 in (key[1], key[3]):
                o = 0
                while o + 2 <= len(s):
                    ln, = struct.unpack_from("!H", s, o)
                    _dns(s[o + 2:o + 2 + ln], ts, st)
                    o += 2 + ln
            elif len(s) >= 6 and s[0] == 22 and s[1] == 3:
                _tls_stream(s, ts, st)
        except (struct.error, IndexError, ValueError):
            continue
    return st


def _parse(data):
    try:
        return _flows_parse(data)
    except (struct.error, ValueError, OverflowError):
        return None


def _first(pairs):
    pairs = [p for p in pairs if p[1] not in (None, "")]
    return min(pairs, key=lambda p: p[0])[1] if pairs else "none"


def _uniq(vals):
    v = sorted({x for x in vals if x not in (None, "")})
    return v if v else "none"


def _cert_field(st, fn, leaf_only):
    vals = [fn(c, {}) for chain in st["certs"] for c in (chain[:1] if leaf_only else chain)]
    vals = [v for v in vals if v not in (None, "none")]
    if leaf_only:
        return vals[0] if vals else "none"
    return _uniq(vals)


def app_value(data, ctx):
    """pcap.<field> / pcapng.<field>: application-layer indicators (see module doc)."""
    if not data:
        return None
    kind = _FIELD_KIND.get((ctx or {}).get("field") or "")
    if kind is None:
        return None
    recs = _parse(data)
    if recs is None:
        return "none"
    st = _analyze(recs)
    req, resp, hello = sorted(st["http_req"]), sorted(st["http_resp"]), sorted(st["hello"], key=lambda h: h[0])
    q = st["dns_q"]

    def most_queried():
        if not q:
            return "none"
        best = max(q.values())
        return min(n for n, c in q.items() if c == best)

    def first_url():
        for _ts, _m, uri, host, _ua in req:
            if uri.startswith(("http://", "https://")):
                return uri
            if host:
                return "http://" + host + uri
        return "none"

    def urls():
        return _uniq(u if u.startswith(("http://", "https://")) else ("http://" + h + u if h else None)
                     for _t, _m, u, h, _a in req)

    from .x509 import sha256_fingerprint, subject_cn, issuer_cn
    tv = {0x0300: "SSLv3", 0x0301: "TLSv1.0", 0x0302: "TLSv1.1", 0x0303: "TLSv1.2", 0x0304: "TLSv1.3"}
    table = {
        "dns_query_names": lambda: _uniq(n for _t, n in st["dns_names"]),
        "dns_query_first": lambda: _first(st["dns_names"]),
        "dns_query_count": lambda: st["dns_req"],
        "dns_query_name_count": lambda: len({n for _t, n in st["dns_names"]}),
        "dns_response_count": lambda: st["dns_resp"],
        "dns_answer_ips": lambda: _uniq(str(a) for a in st["ans_ips"]),
        "dns_answer_ip_count": lambda: len(st["ans_ips"]),
        "dns_cname_targets": lambda: _uniq(st["cnames"]),
        "dns_qtypes": lambda: sorted(st["qtypes"]) or "none",
        "most_queried_domain": most_queried,
        "dns_nxdomain_count": lambda: st["nx"],
        "dns_nxdomain_names": lambda: _uniq(st["nx_names"]),
        "http_hosts": lambda: _uniq(r[3] for r in req),
        "http_host_first": lambda: _first((r[0], r[3]) for r in req),
        "http_host_count": lambda: len({r[3] for r in req if r[3]}),
        "http_user_agents": lambda: _uniq(r[4] for r in req),
        "http_user_agent_first": lambda: _first((r[0], r[4]) for r in req),
        "http_user_agent_count": lambda: len({r[4] for r in req if r[4]}),
        "http_request_uris": lambda: _uniq(r[2] for r in req),
        "http_request_uri_first": lambda: _first((r[0], r[2]) for r in req),
        "http_methods": lambda: _uniq(r[1] for r in req),
        "http_request_count": lambda: len(req),
        "http_status_codes": lambda: sorted({r[1] for r in resp}) or "none",
        "http_response_count": lambda: len(resp),
        "http_content_types": lambda: _uniq(r[2] for r in resp),
        "http_first_request_url": first_url,
        "http_request_urls": urls,
        "tls_sni_names": lambda: _uniq(h[1] for h in hello),
        "tls_sni_first": lambda: _first((h[0], h[1]) for h in hello),
        "tls_sni_count": lambda: len({h[1] for h in hello if h[1]}),
        "tls_client_hello_count": lambda: len(hello),
        "tls_alpn_protocols": lambda: _uniq(st["alpn"]),
        "tls_versions": lambda: _uniq(tv.get(h[2], "0x%04x" % h[2]) for h in hello),
        "tls_version_first": lambda: _first((h[0], tv.get(h[2], "0x%04x" % h[2])) for h in hello),
        "tls_ja3_md5": lambda: _uniq(hashlib.md5(h[3].encode()).hexdigest() for h in hello),
        "tls_ja3_first": lambda: _first((h[0], hashlib.md5(h[3].encode()).hexdigest()) for h in hello),
        "tls_ja3_strings": lambda: _uniq(h[3] for h in hello),
        "tls_cert_sha256": lambda: _cert_field(st, sha256_fingerprint, True),
        "tls_cert_sha256s": lambda: _cert_field(st, sha256_fingerprint, False),
        "tls_cert_subject_cn": lambda: _cert_field(st, subject_cn, True),
        "tls_cert_subject_cns": lambda: _cert_field(st, subject_cn, False),
        "tls_cert_issuer_cn": lambda: _cert_field(st, issuer_cn, True),
        "tls_cert_count": lambda: len({c for chain in st["certs"] for c in chain}),
        "ftp_usernames": lambda: _uniq(u for _t, u in st["ftp_user"]),
        "ftp_username_first": lambda: _first(st["ftp_user"]),
        "ftp_passwords": lambda: _uniq(u for _t, u in st["ftp_pass"]),
        "ftp_password_first": lambda: _first(st["ftp_pass"]),
        "ftp_commands": lambda: _uniq(st["ftp_cmds"]),
        "ftp_filenames": lambda: _uniq(st["ftp_files"]),
        "smtp_mail_from": lambda: _uniq(a for _t, a in st["mail_from"]),
        "smtp_mail_from_first": lambda: _first(st["mail_from"]),
        "smtp_rcpt_to": lambda: _uniq(a for _t, a in st["rcpt_to"]),
        "smtp_rcpt_to_first": lambda: _first(st["rcpt_to"]),
        "smtp_helo": lambda: _uniq(st["helo"]),
        "icmp_payload_strings": lambda: _uniq(s for _t, s in st["icmp"]),
        "icmp_payload_first": lambda: _first(st["icmp"]),
    }
    return table[kind]()
