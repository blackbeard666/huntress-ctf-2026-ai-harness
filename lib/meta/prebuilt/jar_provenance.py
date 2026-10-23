"""JAR provenance (prebuilt, SPECULATIVE -- never GM-asked yet): v1 signer, signed vs unsigned entries, OSGi bundle
headers, WAR/EAR deployment descriptors, Maven coordinates. fmt jar (+ java_archive / war / ear / osgi aliases).

v1 JAR signing (JAR File Specification "Signed JAR File"): META-INF/MANIFEST.MF per-entry sections `Name: <path>` +
`<ALG>-Digest: b64`; META-INF/<SIGNER>.SF main section `<ALG>-Digest-Manifest: b64`; META-INF/<SIGNER>.RSA|DSA|EC =
PKCS#7 SignedData (cert walk reused from apk_signing._p7_certs, x509.py spellings).
  signer_cert_sha256 / _sha1   lowercase hex digest of the first cert of the first PKCS#7 block (CD order) =
                               keytool -printcert -jarfile fingerprint without colons, lowercased
  signer_subject_cn / _dn / signer_issuer_cn / signer_serial_hex   via x509.py (serial: lowercase, even length)
  sf_digest_algorithm          the `<ALG>` prefix of the first .SF's `<ALG>-Digest-Manifest` key ("SHA-256")
  unsigned_entries             CD order file members (no directories) with no MANIFEST.MF `Name:` section carrying a
                               `*-Digest` attribute, excluding the signing-related META-INF files (MANIFEST.MF,
                               *.SF/.RSA/.DSA/.EC, SIG-*) -- what JarFile reports as getCodeSigners() == null.
                               Unsigned jar (no .SF) -> "none".  signed_entries = the complement; *_count = len.
  modified_entries             entries whose stored manifest digest != the digest of their bytes (tampered).
OSGi (Core spec 3.2.1 header grammar: clause *(',' clause); clause = path *(';' path) *(';' param)):
  bundle_symbolic_name         the first clause's first path (directives like `;singleton:=true` dropped)
  bundle_version / bundle_activator / bundle_name / bundle_vendor / bundle_manifest_version   verbatim, trimmed
  export_package / import_package   JSON list of every package path, header order, duplicates kept once
WAR: WEB-INF/web.xml (javax / jakarta / DTD-era no-namespace: matched by LOCAL name), document order:
  servlet_classes (servlet/servlet-class), servlet_names, servlet_url_patterns (servlet-mapping/url-pattern),
  filter_classes, listener_classes, welcome_files (welcome-file-list/welcome-file), web_app_version (@version).
EAR: META-INF/application.xml module/{web/web-uri, ejb, java, connector}, document order -> ear_modules;
  context_roots (web/context-root), module_count.
Maven: META-INF/maven/<g>/<a>/pom.properties (java.util.Properties text), CD order -> "groupId:artifactId:version"
  list; maven_group_id/_artifact_id/_version of the one whose artifactId-version matches the member file name, else
  the first. nested_maven_coordinates also walks nested *.jar members (BOOT-INF/lib, WEB-INF/lib, lib/), CD order.
Not a zip -> None; a jar lacking the asked structure -> "none"."""
import base64
import hashlib
import re
import xml.etree.ElementTree as ET

from .jar import _manifest_bytes, _zip, descend, parse_manifest

FIELDS = {
    ("jar", "signer_cert_sha256"): "signing",
    ("jar", "signer_certificate_sha256"): "signing",
    ("jar", "signer_sha256"): "signing",
    ("jar", "cert_sha256"): "signing",
    ("jar", "v1_signer_cert_sha256"): "signing",
    ("jar", "signer_cert_sha256_digest"): "signing",
    ("jar", "signer_cert_sha1"): "signing",
    ("jar", "signer_certificate_sha1"): "signing",
    ("jar", "signer_sha1"): "signing",
    ("jar", "signer_subject_cn"): "signing",
    ("jar", "signer_cn"): "signing",
    ("jar", "signer_cert_subject_cn"): "signing",
    ("jar", "signer_common_name"): "signing",
    ("jar", "signer_subject_dn"): "signing",
    ("jar", "signer_dn"): "signing",
    ("jar", "signer_cert_subject_dn"): "signing",
    ("jar", "signer_issuer_cn"): "signing",
    ("jar", "signer_cert_issuer_cn"): "signing",
    ("jar", "signer_issuer_dn"): "signing",
    ("jar", "signer_cert_issuer_dn"): "signing",
    ("jar", "signer_serial_hex"): "signing",
    ("jar", "signer_cert_serial_hex"): "signing",
    ("jar", "signer_serial_number_hex"): "signing",
    ("jar", "signer_not_before_utc"): "signing",
    ("jar", "signer_not_after_utc"): "signing",
    ("jar", "sf_digest_algorithm"): "signing",
    ("jar", "signature_file_digest_algorithm"): "signing",
    ("jar", "digest_algorithm"): "signing",
    ("jar", "sf_manifest_digest_algorithm"): "signing",
    ("jar", "manifest_digest_algorithm"): "signing",
    ("jar", "unsigned_entries"): "signing",
    ("jar", "unsigned_entry_names"): "signing",
    ("jar", "unsigned_entry_count"): "signing",
    ("jar", "signed_entries"): "signing",
    ("jar", "signed_entry_names"): "signing",
    ("jar", "signed_entry_count"): "signing",
    ("jar", "has_unsigned_entries"): "signing",
    ("jar", "modified_entries"): "signing",
    ("jar", "tampered_entries"): "signing",
    ("jar", "digest_mismatch_entries"): "signing",
    ("jar", "is_signed"): "signing",
    ("jar", "v1_signed"): "signing",
    ("jar", "signer_count"): "signing",
    ("jar", "signer_names"): "signing",
    ("jar", "v1_signer_names"): "signing",
    ("jar", "bundle_symbolic_name"): "osgi",
    ("jar", "osgi_bundle_symbolic_name"): "osgi",
    ("jar", "symbolic_name"): "osgi",
    ("jar", "bundle_version"): "osgi",
    ("jar", "osgi_bundle_version"): "osgi",
    ("jar", "bundle_activator"): "osgi",
    ("jar", "osgi_bundle_activator"): "osgi",
    ("jar", "bundle_name"): "osgi",
    ("jar", "osgi_bundle_name"): "osgi",
    ("jar", "bundle_vendor"): "osgi",
    ("jar", "bundle_manifest_version"): "osgi",
    ("jar", "export_package"): "osgi",
    ("jar", "osgi_export_package"): "osgi",
    ("jar", "exported_packages"): "osgi",
    ("jar", "import_package"): "osgi",
    ("jar", "osgi_import_package"): "osgi",
    ("jar", "imported_packages"): "osgi",
    ("jar", "war_servlet_classes"): "war",
    ("jar", "servlet_classes"): "war",
    ("jar", "servlet_class_names"): "war",
    ("jar", "war_servlet_names"): "war",
    ("jar", "servlet_names"): "war",
    ("jar", "war_servlet_url_patterns"): "war",
    ("jar", "servlet_url_patterns"): "war",
    ("jar", "url_patterns"): "war",
    ("jar", "war_filter_classes"): "war",
    ("jar", "filter_classes"): "war",
    ("jar", "war_listener_classes"): "war",
    ("jar", "listener_classes"): "war",
    ("jar", "war_welcome_files"): "war",
    ("jar", "welcome_files"): "war",
    ("jar", "welcome_file_list"): "war",
    ("jar", "web_app_version"): "war",
    ("jar", "web_xml_version"): "war",
    ("jar", "servlet_count"): "war",
    ("jar", "ear_modules"): "ear",
    ("jar", "modules"): "ear",
    ("jar", "module_uris"): "ear",
    ("jar", "application_modules"): "ear",
    ("jar", "ear_module_count"): "ear",
    ("jar", "module_count"): "ear",
    ("jar", "context_roots"): "ear",
    ("jar", "ear_context_roots"): "ear",
    ("jar", "web_modules"): "ear",
    ("jar", "ejb_modules"): "ear",
    ("jar", "maven_coordinates"): "maven",
    ("jar", "maven_gav"): "maven",
    ("jar", "maven_gavs"): "maven",
    ("jar", "pom_coordinates"): "maven",
    ("jar", "nested_maven_coordinates"): "maven",
    ("jar", "nested_dependency_coordinates"): "maven",
    ("jar", "maven_group_id"): "maven",
    ("jar", "maven_artifact_id"): "maven",
    ("jar", "maven_version"): "maven",
    ("jar", "pom_group_id"): "maven",
    ("jar", "pom_artifact_id"): "maven",
    ("jar", "pom_version"): "maven",
    ("jar", "maven_coordinate"): "maven",
    ("jar", "maven_count"): "maven",
    ("jar", "pom_properties_count"): "maven",
    ("java_archive", "signer_cert_sha256"): "signing",
    ("java_archive", "signer_certificate_sha256"): "signing",
    ("java_archive", "signer_sha256"): "signing",
    ("java_archive", "cert_sha256"): "signing",
    ("java_archive", "v1_signer_cert_sha256"): "signing",
    ("java_archive", "signer_cert_sha256_digest"): "signing",
    ("java_archive", "signer_cert_sha1"): "signing",
    ("java_archive", "signer_certificate_sha1"): "signing",
    ("java_archive", "signer_sha1"): "signing",
    ("java_archive", "signer_subject_cn"): "signing",
    ("java_archive", "signer_cn"): "signing",
    ("java_archive", "signer_cert_subject_cn"): "signing",
    ("java_archive", "signer_common_name"): "signing",
    ("java_archive", "signer_subject_dn"): "signing",
    ("java_archive", "signer_dn"): "signing",
    ("java_archive", "signer_cert_subject_dn"): "signing",
    ("java_archive", "signer_issuer_cn"): "signing",
    ("java_archive", "signer_cert_issuer_cn"): "signing",
    ("java_archive", "signer_issuer_dn"): "signing",
    ("java_archive", "signer_cert_issuer_dn"): "signing",
    ("java_archive", "signer_serial_hex"): "signing",
    ("java_archive", "signer_cert_serial_hex"): "signing",
    ("java_archive", "signer_serial_number_hex"): "signing",
    ("java_archive", "signer_not_before_utc"): "signing",
    ("java_archive", "signer_not_after_utc"): "signing",
    ("java_archive", "sf_digest_algorithm"): "signing",
    ("java_archive", "signature_file_digest_algorithm"): "signing",
    ("java_archive", "digest_algorithm"): "signing",
    ("java_archive", "sf_manifest_digest_algorithm"): "signing",
    ("java_archive", "manifest_digest_algorithm"): "signing",
    ("java_archive", "unsigned_entries"): "signing",
    ("java_archive", "unsigned_entry_names"): "signing",
    ("java_archive", "unsigned_entry_count"): "signing",
    ("java_archive", "signed_entries"): "signing",
    ("java_archive", "signed_entry_names"): "signing",
    ("java_archive", "signed_entry_count"): "signing",
    ("java_archive", "has_unsigned_entries"): "signing",
    ("java_archive", "modified_entries"): "signing",
    ("java_archive", "tampered_entries"): "signing",
    ("java_archive", "digest_mismatch_entries"): "signing",
    ("java_archive", "is_signed"): "signing",
    ("java_archive", "v1_signed"): "signing",
    ("java_archive", "signer_count"): "signing",
    ("java_archive", "signer_names"): "signing",
    ("java_archive", "v1_signer_names"): "signing",
    ("java_archive", "bundle_symbolic_name"): "osgi",
    ("java_archive", "osgi_bundle_symbolic_name"): "osgi",
    ("java_archive", "symbolic_name"): "osgi",
    ("java_archive", "bundle_version"): "osgi",
    ("java_archive", "osgi_bundle_version"): "osgi",
    ("java_archive", "bundle_activator"): "osgi",
    ("java_archive", "osgi_bundle_activator"): "osgi",
    ("java_archive", "bundle_name"): "osgi",
    ("java_archive", "osgi_bundle_name"): "osgi",
    ("java_archive", "bundle_vendor"): "osgi",
    ("java_archive", "bundle_manifest_version"): "osgi",
    ("java_archive", "export_package"): "osgi",
    ("java_archive", "osgi_export_package"): "osgi",
    ("java_archive", "exported_packages"): "osgi",
    ("java_archive", "import_package"): "osgi",
    ("java_archive", "osgi_import_package"): "osgi",
    ("java_archive", "imported_packages"): "osgi",
    ("java_archive", "war_servlet_classes"): "war",
    ("java_archive", "servlet_classes"): "war",
    ("java_archive", "servlet_class_names"): "war",
    ("java_archive", "war_servlet_names"): "war",
    ("java_archive", "servlet_names"): "war",
    ("java_archive", "war_servlet_url_patterns"): "war",
    ("java_archive", "servlet_url_patterns"): "war",
    ("java_archive", "url_patterns"): "war",
    ("java_archive", "war_filter_classes"): "war",
    ("java_archive", "filter_classes"): "war",
    ("java_archive", "war_listener_classes"): "war",
    ("java_archive", "listener_classes"): "war",
    ("java_archive", "war_welcome_files"): "war",
    ("java_archive", "welcome_files"): "war",
    ("java_archive", "welcome_file_list"): "war",
    ("java_archive", "web_app_version"): "war",
    ("java_archive", "web_xml_version"): "war",
    ("java_archive", "servlet_count"): "war",
    ("java_archive", "ear_modules"): "ear",
    ("java_archive", "modules"): "ear",
    ("java_archive", "module_uris"): "ear",
    ("java_archive", "application_modules"): "ear",
    ("java_archive", "ear_module_count"): "ear",
    ("java_archive", "module_count"): "ear",
    ("java_archive", "context_roots"): "ear",
    ("java_archive", "ear_context_roots"): "ear",
    ("java_archive", "web_modules"): "ear",
    ("java_archive", "ejb_modules"): "ear",
    ("java_archive", "maven_coordinates"): "maven",
    ("java_archive", "maven_gav"): "maven",
    ("java_archive", "maven_gavs"): "maven",
    ("java_archive", "pom_coordinates"): "maven",
    ("java_archive", "nested_maven_coordinates"): "maven",
    ("java_archive", "nested_dependency_coordinates"): "maven",
    ("java_archive", "maven_group_id"): "maven",
    ("java_archive", "maven_artifact_id"): "maven",
    ("java_archive", "maven_version"): "maven",
    ("java_archive", "pom_group_id"): "maven",
    ("java_archive", "pom_artifact_id"): "maven",
    ("java_archive", "pom_version"): "maven",
    ("java_archive", "maven_coordinate"): "maven",
    ("java_archive", "maven_count"): "maven",
    ("java_archive", "pom_properties_count"): "maven",
    ("war", "signer_cert_sha256"): "signing",
    ("war", "signer_certificate_sha256"): "signing",
    ("war", "signer_sha256"): "signing",
    ("war", "cert_sha256"): "signing",
    ("war", "v1_signer_cert_sha256"): "signing",
    ("war", "signer_cert_sha256_digest"): "signing",
    ("war", "signer_cert_sha1"): "signing",
    ("war", "signer_certificate_sha1"): "signing",
    ("war", "signer_sha1"): "signing",
    ("war", "signer_subject_cn"): "signing",
    ("war", "signer_cn"): "signing",
    ("war", "signer_cert_subject_cn"): "signing",
    ("war", "signer_common_name"): "signing",
    ("war", "signer_subject_dn"): "signing",
    ("war", "signer_dn"): "signing",
    ("war", "signer_cert_subject_dn"): "signing",
    ("war", "signer_issuer_cn"): "signing",
    ("war", "signer_cert_issuer_cn"): "signing",
    ("war", "signer_issuer_dn"): "signing",
    ("war", "signer_cert_issuer_dn"): "signing",
    ("war", "signer_serial_hex"): "signing",
    ("war", "signer_cert_serial_hex"): "signing",
    ("war", "signer_serial_number_hex"): "signing",
    ("war", "signer_not_before_utc"): "signing",
    ("war", "signer_not_after_utc"): "signing",
    ("war", "sf_digest_algorithm"): "signing",
    ("war", "signature_file_digest_algorithm"): "signing",
    ("war", "digest_algorithm"): "signing",
    ("war", "sf_manifest_digest_algorithm"): "signing",
    ("war", "manifest_digest_algorithm"): "signing",
    ("war", "unsigned_entries"): "signing",
    ("war", "unsigned_entry_names"): "signing",
    ("war", "unsigned_entry_count"): "signing",
    ("war", "signed_entries"): "signing",
    ("war", "signed_entry_names"): "signing",
    ("war", "signed_entry_count"): "signing",
    ("war", "has_unsigned_entries"): "signing",
    ("war", "modified_entries"): "signing",
    ("war", "tampered_entries"): "signing",
    ("war", "digest_mismatch_entries"): "signing",
    ("war", "is_signed"): "signing",
    ("war", "v1_signed"): "signing",
    ("war", "signer_count"): "signing",
    ("war", "signer_names"): "signing",
    ("war", "v1_signer_names"): "signing",
    ("war", "bundle_symbolic_name"): "osgi",
    ("war", "osgi_bundle_symbolic_name"): "osgi",
    ("war", "symbolic_name"): "osgi",
    ("war", "bundle_version"): "osgi",
    ("war", "osgi_bundle_version"): "osgi",
    ("war", "bundle_activator"): "osgi",
    ("war", "osgi_bundle_activator"): "osgi",
    ("war", "bundle_name"): "osgi",
    ("war", "osgi_bundle_name"): "osgi",
    ("war", "bundle_vendor"): "osgi",
    ("war", "bundle_manifest_version"): "osgi",
    ("war", "export_package"): "osgi",
    ("war", "osgi_export_package"): "osgi",
    ("war", "exported_packages"): "osgi",
    ("war", "import_package"): "osgi",
    ("war", "osgi_import_package"): "osgi",
    ("war", "imported_packages"): "osgi",
    ("war", "war_servlet_classes"): "war",
    ("war", "servlet_classes"): "war",
    ("war", "servlet_class_names"): "war",
    ("war", "war_servlet_names"): "war",
    ("war", "servlet_names"): "war",
    ("war", "war_servlet_url_patterns"): "war",
    ("war", "servlet_url_patterns"): "war",
    ("war", "url_patterns"): "war",
    ("war", "war_filter_classes"): "war",
    ("war", "filter_classes"): "war",
    ("war", "war_listener_classes"): "war",
    ("war", "listener_classes"): "war",
    ("war", "war_welcome_files"): "war",
    ("war", "welcome_files"): "war",
    ("war", "welcome_file_list"): "war",
    ("war", "web_app_version"): "war",
    ("war", "web_xml_version"): "war",
    ("war", "servlet_count"): "war",
    ("war", "ear_modules"): "ear",
    ("war", "modules"): "ear",
    ("war", "module_uris"): "ear",
    ("war", "application_modules"): "ear",
    ("war", "ear_module_count"): "ear",
    ("war", "module_count"): "ear",
    ("war", "context_roots"): "ear",
    ("war", "ear_context_roots"): "ear",
    ("war", "web_modules"): "ear",
    ("war", "ejb_modules"): "ear",
    ("war", "maven_coordinates"): "maven",
    ("war", "maven_gav"): "maven",
    ("war", "maven_gavs"): "maven",
    ("war", "pom_coordinates"): "maven",
    ("war", "nested_maven_coordinates"): "maven",
    ("war", "nested_dependency_coordinates"): "maven",
    ("war", "maven_group_id"): "maven",
    ("war", "maven_artifact_id"): "maven",
    ("war", "maven_version"): "maven",
    ("war", "pom_group_id"): "maven",
    ("war", "pom_artifact_id"): "maven",
    ("war", "pom_version"): "maven",
    ("war", "maven_coordinate"): "maven",
    ("war", "maven_count"): "maven",
    ("war", "pom_properties_count"): "maven",
    ("ear", "signer_cert_sha256"): "signing",
    ("ear", "signer_certificate_sha256"): "signing",
    ("ear", "signer_sha256"): "signing",
    ("ear", "cert_sha256"): "signing",
    ("ear", "v1_signer_cert_sha256"): "signing",
    ("ear", "signer_cert_sha256_digest"): "signing",
    ("ear", "signer_cert_sha1"): "signing",
    ("ear", "signer_certificate_sha1"): "signing",
    ("ear", "signer_sha1"): "signing",
    ("ear", "signer_subject_cn"): "signing",
    ("ear", "signer_cn"): "signing",
    ("ear", "signer_cert_subject_cn"): "signing",
    ("ear", "signer_common_name"): "signing",
    ("ear", "signer_subject_dn"): "signing",
    ("ear", "signer_dn"): "signing",
    ("ear", "signer_cert_subject_dn"): "signing",
    ("ear", "signer_issuer_cn"): "signing",
    ("ear", "signer_cert_issuer_cn"): "signing",
    ("ear", "signer_issuer_dn"): "signing",
    ("ear", "signer_cert_issuer_dn"): "signing",
    ("ear", "signer_serial_hex"): "signing",
    ("ear", "signer_cert_serial_hex"): "signing",
    ("ear", "signer_serial_number_hex"): "signing",
    ("ear", "signer_not_before_utc"): "signing",
    ("ear", "signer_not_after_utc"): "signing",
    ("ear", "sf_digest_algorithm"): "signing",
    ("ear", "signature_file_digest_algorithm"): "signing",
    ("ear", "digest_algorithm"): "signing",
    ("ear", "sf_manifest_digest_algorithm"): "signing",
    ("ear", "manifest_digest_algorithm"): "signing",
    ("ear", "unsigned_entries"): "signing",
    ("ear", "unsigned_entry_names"): "signing",
    ("ear", "unsigned_entry_count"): "signing",
    ("ear", "signed_entries"): "signing",
    ("ear", "signed_entry_names"): "signing",
    ("ear", "signed_entry_count"): "signing",
    ("ear", "has_unsigned_entries"): "signing",
    ("ear", "modified_entries"): "signing",
    ("ear", "tampered_entries"): "signing",
    ("ear", "digest_mismatch_entries"): "signing",
    ("ear", "is_signed"): "signing",
    ("ear", "v1_signed"): "signing",
    ("ear", "signer_count"): "signing",
    ("ear", "signer_names"): "signing",
    ("ear", "v1_signer_names"): "signing",
    ("ear", "bundle_symbolic_name"): "osgi",
    ("ear", "osgi_bundle_symbolic_name"): "osgi",
    ("ear", "symbolic_name"): "osgi",
    ("ear", "bundle_version"): "osgi",
    ("ear", "osgi_bundle_version"): "osgi",
    ("ear", "bundle_activator"): "osgi",
    ("ear", "osgi_bundle_activator"): "osgi",
    ("ear", "bundle_name"): "osgi",
    ("ear", "osgi_bundle_name"): "osgi",
    ("ear", "bundle_vendor"): "osgi",
    ("ear", "bundle_manifest_version"): "osgi",
    ("ear", "export_package"): "osgi",
    ("ear", "osgi_export_package"): "osgi",
    ("ear", "exported_packages"): "osgi",
    ("ear", "import_package"): "osgi",
    ("ear", "osgi_import_package"): "osgi",
    ("ear", "imported_packages"): "osgi",
    ("ear", "war_servlet_classes"): "war",
    ("ear", "servlet_classes"): "war",
    ("ear", "servlet_class_names"): "war",
    ("ear", "war_servlet_names"): "war",
    ("ear", "servlet_names"): "war",
    ("ear", "war_servlet_url_patterns"): "war",
    ("ear", "servlet_url_patterns"): "war",
    ("ear", "url_patterns"): "war",
    ("ear", "war_filter_classes"): "war",
    ("ear", "filter_classes"): "war",
    ("ear", "war_listener_classes"): "war",
    ("ear", "listener_classes"): "war",
    ("ear", "war_welcome_files"): "war",
    ("ear", "welcome_files"): "war",
    ("ear", "welcome_file_list"): "war",
    ("ear", "web_app_version"): "war",
    ("ear", "web_xml_version"): "war",
    ("ear", "servlet_count"): "war",
    ("ear", "ear_modules"): "ear",
    ("ear", "modules"): "ear",
    ("ear", "module_uris"): "ear",
    ("ear", "application_modules"): "ear",
    ("ear", "ear_module_count"): "ear",
    ("ear", "module_count"): "ear",
    ("ear", "context_roots"): "ear",
    ("ear", "ear_context_roots"): "ear",
    ("ear", "web_modules"): "ear",
    ("ear", "ejb_modules"): "ear",
    ("ear", "maven_coordinates"): "maven",
    ("ear", "maven_gav"): "maven",
    ("ear", "maven_gavs"): "maven",
    ("ear", "pom_coordinates"): "maven",
    ("ear", "nested_maven_coordinates"): "maven",
    ("ear", "nested_dependency_coordinates"): "maven",
    ("ear", "maven_group_id"): "maven",
    ("ear", "maven_artifact_id"): "maven",
    ("ear", "maven_version"): "maven",
    ("ear", "pom_group_id"): "maven",
    ("ear", "pom_artifact_id"): "maven",
    ("ear", "pom_version"): "maven",
    ("ear", "maven_coordinate"): "maven",
    ("ear", "maven_count"): "maven",
    ("ear", "pom_properties_count"): "maven",
}

_J = ("jar", "java_archive", "war", "ear")
_SIGN = {
    "signer_cert_sha256": "cert_sha256", "signer_certificate_sha256": "cert_sha256", "signer_sha256": "cert_sha256",
    "cert_sha256": "cert_sha256", "v1_signer_cert_sha256": "cert_sha256", "signer_cert_sha256_digest": "cert_sha256",
    "signer_cert_sha1": "cert_sha1", "signer_certificate_sha1": "cert_sha1", "signer_sha1": "cert_sha1",
    "signer_subject_cn": "subject_cn", "signer_cn": "subject_cn", "signer_cert_subject_cn": "subject_cn",
    "signer_common_name": "subject_cn",
    "signer_subject_dn": "subject_dn", "signer_dn": "subject_dn", "signer_cert_subject_dn": "subject_dn",
    "signer_issuer_cn": "issuer_cn", "signer_cert_issuer_cn": "issuer_cn",
    "signer_issuer_dn": "issuer_dn", "signer_cert_issuer_dn": "issuer_dn",
    "signer_serial_hex": "serial_hex", "signer_cert_serial_hex": "serial_hex", "signer_serial_number_hex": "serial_hex",
    "signer_not_before_utc": "not_before_utc", "signer_not_after_utc": "not_after_utc",
    "sf_digest_algorithm": "sf_alg", "signature_file_digest_algorithm": "sf_alg", "digest_algorithm": "sf_alg",
    "sf_manifest_digest_algorithm": "sf_alg", "manifest_digest_algorithm": "sf_alg",
    "unsigned_entries": "unsigned", "unsigned_entry_names": "unsigned", "unsigned_entry_count": "unsigned_n",
    "signed_entries": "signed", "signed_entry_names": "signed", "signed_entry_count": "signed_n",
    "has_unsigned_entries": "has_unsigned", "modified_entries": "modified", "tampered_entries": "modified",
    "digest_mismatch_entries": "modified", "is_signed": "is_signed", "v1_signed": "is_signed",
    "signer_count": "signer_n", "signer_names": "signer_names", "v1_signer_names": "signer_names",
}
_OSGI = {"bundle_symbolic_name": "bsn", "osgi_bundle_symbolic_name": "bsn", "symbolic_name": "bsn",
         "bundle_version": "Bundle-Version", "osgi_bundle_version": "Bundle-Version",
         "bundle_activator": "Bundle-Activator", "osgi_bundle_activator": "Bundle-Activator",
         "bundle_name": "Bundle-Name", "osgi_bundle_name": "Bundle-Name",
         "bundle_vendor": "Bundle-Vendor", "bundle_manifest_version": "Bundle-ManifestVersion",
         "export_package": "Export-Package", "osgi_export_package": "Export-Package",
         "exported_packages": "Export-Package",
         "import_package": "Import-Package", "osgi_import_package": "Import-Package",
         "imported_packages": "Import-Package"}
_WAR = {"war_servlet_classes": "servlet_classes", "servlet_classes": "servlet_classes",
        "servlet_class_names": "servlet_classes", "war_servlet_names": "servlet_names", "servlet_names": "servlet_names",
        "war_servlet_url_patterns": "url_patterns", "servlet_url_patterns": "url_patterns",
        "url_patterns": "url_patterns", "war_filter_classes": "filter_classes", "filter_classes": "filter_classes",
        "war_listener_classes": "listener_classes", "listener_classes": "listener_classes",
        "war_welcome_files": "welcome_files", "welcome_files": "welcome_files", "welcome_file_list": "welcome_files",
        "web_app_version": "web_version", "web_xml_version": "web_version", "servlet_count": "servlet_n"}
_EAR = {"ear_modules": "modules", "modules": "modules", "module_uris": "modules", "application_modules": "modules",
        "ear_module_count": "module_n", "module_count": "module_n", "context_roots": "context_roots",
        "ear_context_roots": "context_roots", "web_modules": "web_modules", "ejb_modules": "ejb_modules"}
_MVN = {"maven_coordinates": "coords", "maven_gav": "coords", "maven_gavs": "coords", "pom_coordinates": "coords",
        "nested_maven_coordinates": "nested", "nested_dependency_coordinates": "nested",
        "maven_group_id": "groupId", "maven_artifact_id": "artifactId", "maven_version": "version",
        "pom_group_id": "groupId", "pom_artifact_id": "artifactId", "pom_version": "version",
        "maven_coordinate": "one", "maven_count": "count", "pom_properties_count": "count"}


_SIGREL = re.compile(r"^META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC)|SIG-[^/]*)$", re.I)
_PKCS7 = re.compile(r"^META-INF/[^/]+\.(?:RSA|DSA|EC)$", re.I)
_SF = re.compile(r"^META-INF/[^/]+\.SF$", re.I)
_HASH = {"SHA-256": hashlib.sha256, "SHA-384": hashlib.sha384, "SHA-512": hashlib.sha512, "SHA-1": hashlib.sha1,
         "SHA1": hashlib.sha1, "SHA256": hashlib.sha256, "MD5": hashlib.md5}


def _open(data, ctx):
    """(zipfile, infos) of the (descended) jar, or None when the bytes are not a zip."""
    if data is None:
        return None
    z = _zip(descend(data, ctx))
    if z is None:
        return None
    try:
        return z, z.infolist()
    except Exception:  # noqa: BLE001
        return None


def _read(z, info):
    try:
        return z.read(info)
    except Exception:  # noqa: BLE001 -- encrypted / bad CRC
        return None


def _sections(raw):
    """Per-entry manifest sections [(name, {lower-attr: value})] after the main section (72-byte continuations)."""
    text = raw.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")
    out, cur, last, main = [], None, None, True
    for ln in text.split("\n"):
        if ln == "":
            main, cur, last = False, None, None
            continue
        if ln.startswith(" ") and last is not None:
            last[0][last[1]] += ln[1:]
            continue
        k, sep, v = ln.partition(":")
        if not sep:
            last = None
            continue
        v = v[1:] if v.startswith(" ") else v
        if main:
            last = None
            continue
        if cur is None:
            cur = {}
            out.append(cur)
        key = k.strip().lower()
        cur.setdefault(key, v)
        last = (cur, key)
    return [(s.get("name"), s) for s in out if s.get("name") is not None]


def _sign_state(z, infos):
    st = {"sf": [i for i in infos if _SF.match(i.filename)], "p7": [i for i in infos if _PKCS7.match(i.filename)]}
    raw = _manifest_bytes(z)
    st["sections"] = _sections(raw) if raw is not None else []
    return st


def _cert(z, st):
    from .apk_signing import _p7_certs
    for i in st["p7"]:
        der = _read(z, i)
        try:
            certs = _p7_certs(der) if der else []
        except Exception:  # noqa: BLE001
            certs = []
        if certs:
            return certs[0]
    return None


def _digested(sec):
    return any(k.endswith("-digest") for k in sec)


def signing(data, ctx):
    """jar.signer_* / sf_digest_algorithm / unsigned_entries / signed_entries / modified_entries (v1 JAR signing)."""
    zo = _open(data, ctx)
    if zo is None:
        return None
    z, infos = zo
    kind = _SIGN.get(ctx.get("field") or "")
    try:
        st = _sign_state(z, infos)
        signed = bool(st["sf"])
        if kind == "is_signed":
            return signed
        if kind == "signer_n":
            return len(st["sf"])
        if kind == "signer_names":
            return [i.filename.rsplit("/", 1)[1][:-3] for i in st["sf"]] if signed else "none"
        if not signed:
            return False if kind == "has_unsigned" else "none"
        if kind == "sf_alg":
            sf = _read(z, st["sf"][0]) or b""
            mf = parse_manifest(sf) or {}
            for name, _v in mf.values():
                m = re.match(r"^(.+?)-Digest-Manifest$", name, re.I)
                if m:
                    return m.group(1)
            return "none"
        if kind in ("unsigned", "unsigned_n", "signed", "signed_n", "has_unsigned", "modified"):
            secs = {}
            for name, sec in st["sections"]:
                secs.setdefault(name, sec)
            files = [i for i in infos if not i.is_dir() and not _SIGREL.match(i.filename)]
            if kind == "modified":
                bad = []
                for i in files:
                    sec = secs.get(i.filename)
                    if not sec:
                        continue
                    for k, v in sec.items():
                        alg = k[:-len("-digest")].upper() if k.endswith("-digest") else None
                        if alg in _HASH:
                            body = _read(z, i)
                            if body is None or base64.b64encode(_HASH[alg](body).digest()).decode() != v.strip():
                                bad.append(i.filename)
                            break
                return bad
            uns = [i.filename for i in files if not _digested(secs.get(i.filename) or {})]
            sig = [i.filename for i in files if _digested(secs.get(i.filename) or {})]
            return {"unsigned": uns, "unsigned_n": len(uns), "signed": sig, "signed_n": len(sig),
                    "has_unsigned": bool(uns)}[kind]
        der = _cert(z, st)
        if der is None:
            return "none"
        if kind == "cert_sha256":
            return hashlib.sha256(der).hexdigest()
        if kind == "cert_sha1":
            return hashlib.sha1(der).hexdigest()
        from . import x509
        return getattr(x509, kind)(der, {})
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------- OSGi

def _split(s, sep):
    """Split on `sep` outside double quotes."""
    out, cur, q = [], [], False
    for ch in s:
        if ch == '"':
            q = not q
        if ch == sep and not q:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def _paths(header):
    out = []
    for clause in _split(header, ","):
        for part in _split(clause, ";"):
            part = part.strip()
            if not part or "=" in part:
                continue
            if part not in out:
                out.append(part)
    return out


def osgi(data, ctx):
    """jar.bundle_* / export_package / import_package: OSGi manifest headers."""
    zo = _open(data, ctx)
    if zo is None:
        return None
    z, _infos = zo
    mf = parse_manifest(_manifest_bytes(z))
    if mf is None:
        return "none"
    kind = _OSGI.get(ctx.get("field") or "")
    hdr = mf.get(("Bundle-SymbolicName" if kind == "bsn" else kind or "").lower())
    if hdr is None:
        return "none"
    v = hdr[1].strip()
    if kind == "bsn":
        p = _paths(v)
        return p[0] if p else "none"
    if kind in ("Export-Package", "Import-Package"):
        return _paths(v)
    return v


# ---------------------------------------------------------------- WAR / EAR descriptors

def _xml(z, infos, path):
    info = next((i for i in infos if i.filename.lower() == path.lower()), None)
    raw = _read(z, info) if info is not None else None
    if not raw or b"<!ENTITY" in raw:
        return None
    try:
        return ET.fromstring(raw)
    except ET.ParseError:
        return None


def _local(el):
    t = el.tag if isinstance(el.tag, str) else ""
    return t.rsplit("}", 1)[-1]


def _kids(el, name):
    return [c for c in el if _local(c) == name]


def _text(el):
    return (el.text or "").strip()


def _path(root, names):
    """Texts of every element reached by the local-name path below root, document order."""
    cur = [root]
    for n in names:
        cur = [k for c in cur for k in _kids(c, n)]
    return [_text(c) for c in cur if _text(c)]


def war(data, ctx):
    """WEB-INF/web.xml servlet / filter / listener classes, welcome files (namespace-agnostic)."""
    zo = _open(data, ctx)
    if zo is None:
        return None
    root = _xml(*zo, "WEB-INF/web.xml")
    if root is None or _local(root) != "web-app":
        return "none"
    kind = _WAR.get(ctx.get("field") or "")
    if kind == "web_version":
        return root.get("version") or "none"
    paths = {"servlet_classes": ["servlet", "servlet-class"], "servlet_n": ["servlet", "servlet-name"],
             "servlet_names": ["servlet", "servlet-name"], "url_patterns": ["servlet-mapping", "url-pattern"],
             "filter_classes": ["filter", "filter-class"], "listener_classes": ["listener", "listener-class"],
             "welcome_files": ["welcome-file-list", "welcome-file"]}[kind]
    vals = _path(root, paths)
    if kind == "servlet_n":
        return len(_kids(root, "servlet"))
    return vals or "none"


def ear(data, ctx):
    """META-INF/application.xml modules (web-uri / ejb / java / connector), document order."""
    zo = _open(data, ctx)
    if zo is None:
        return None
    root = _xml(*zo, "META-INF/application.xml")
    if root is None or _local(root) != "application":
        return "none"
    kind = _EAR.get(ctx.get("field") or "")
    mods, roots, web, ejb = [], [], [], []
    for m in _kids(root, "module"):
        for c in m:
            n = _local(c)
            if n == "web":
                uri = next((_text(k) for k in _kids(c, "web-uri")), "")
                cr = next((_text(k) for k in _kids(c, "context-root")), "")
                if uri:
                    mods.append(uri)
                    web.append(uri)
                if cr:
                    roots.append(cr)
            elif n in ("ejb", "java", "connector") and _text(c):
                mods.append(_text(c))
                if n == "ejb":
                    ejb.append(_text(c))
    if kind == "module_n":
        return len(mods)
    return {"modules": mods, "context_roots": roots, "web_modules": web, "ejb_modules": ejb}[kind] or "none"


# ---------------------------------------------------------------- Maven

_POM = re.compile(r"^META-INF/maven/[^/]+/[^/]+/pom\.properties$")


def _props(raw):
    """java.util.Properties text -> dict (comments '#'/'!', '=' / ':' / whitespace separators, '\\' continuations)."""
    out, buf = {}, ""
    for ln in raw.decode("latin-1").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        s = (buf + ln.lstrip()) if buf else ln.lstrip()
        buf = ""
        if not s or (s[0] in "#!" and not buf):
            continue
        if s.endswith("\\") and not s.endswith("\\\\"):
            buf = s[:-1]
            continue
        m = re.match(r"((?:\\.|[^=:\s\\])*)\s*[=:\s]?\s*(.*)$", s)
        if m:
            out.setdefault(m.group(1).replace("\\", ""), m.group(2).rstrip())
    return out


def _gavs(z, infos):
    out = []
    for i in infos:
        if _POM.match(i.filename):
            raw = _read(z, i)
            p = _props(raw) if raw else {}
            if p.get("groupId") and p.get("artifactId") and p.get("version"):
                out.append((p["groupId"], p["artifactId"], p["version"]))
    return out


def maven(data, ctx):
    """META-INF/maven/<g>/<a>/pom.properties -> groupId:artifactId:version (CD order)."""
    zo = _open(data, ctx)
    if zo is None:
        return None
    z, infos = zo
    kind = _MVN.get(ctx.get("field") or "")
    gavs = _gavs(z, infos)
    if kind == "nested":
        out = [":".join(g) for g in gavs]
        for i in infos:
            if i.filename.lower().endswith((".jar", ".war")) and i.file_size < 64 << 20:
                inner = _zip(_read(z, i) or b"")
                if inner is not None:
                    out += [":".join(g) for g in _gavs(inner, inner.infolist())]
        return out or "none"
    if kind == "count":
        return len(gavs)
    if not gavs:
        return "none"
    if kind == "coords":
        return [":".join(g) for g in gavs]
    member = re.split(r"[\\/]|->|!/", str(ctx.get("member") or ctx.get("artifact") or ""))[-1].strip().lower()
    pick = next((g for g in gavs if member.startswith(f"{g[1]}-{g[2]}".lower())), gavs[0])
    if kind == "one":
        return ":".join(pick)
    return {"groupId": pick[0], "artifactId": pick[1], "version": pick[2]}[kind]
