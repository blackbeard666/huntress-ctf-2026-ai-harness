"""iOS app packages (`.ipa`): Info.plist identity, embedded.mobileprovision, iTunesMetadata.plist and the main
executable's Mach-O architecture (prebuilt, SPECULATIVE -- never GM-asked yet; D21 asked "Mobile packages" = apk, so
ipa is the plausible next family). Format tokens: ipa (aliases ios, ios_app) + the bare-profile token mobileprovision.

Input `data`: the .ipa zip (Payload/<Name>.app/...), a zip holding one .ipa (one level of nesting), a bare
Info.plist (bundle fields), a bare embedded.mobileprovision (provision fields) or a bare Mach-O (executable fields).
Layout (Apple TN2435 / App Store packaging):
  Payload/<Name>.app/Info.plist            binary bplist00 (Xcode default) or XML -- plistlib reads both
  Payload/<Name>.app/<CFBundleExecutable>  the Mach-O (thin arm64 or fat)
  Payload/<Name>.app/embedded.mobileprovision
                                           CMS SignedData DER (RFC 5652) whose eContent is an XML plist; the bytes
                                           `<?xml` .. `</plist>` are stored contiguously (definite-length OCTET STRING)
                                           so they are sliced out and plistlib-parsed -- no CMS walk.
  iTunesMetadata.plist (zip root)          App Store download metadata (itemId, softwareVersionBundleId, artistName)
Several .app under Payload/: the one the question names, else the shallowest (nested PlugIns/*.appex never win).
Values: plist strings verbatim/trimmed; arrays compact JSON in stored order (UIDeviceFamily ints [1,2],
CFBundleSupportedPlatforms ["iPhoneOS"]); bools true/false. Dates: plist <date> is stored as ISO-8601 UTC text
"YYYY-MM-DDTHH:MM:SSZ" -- rendered back in that exact stored form. executable_cpu_type_set = lib.meta.macho
cpu_type_set (GM-verified D20 spelling "0x%08x" per slice, fat_arch order); executable_lc_uuid = prebuilt macho.py
uuid (LC_UUID lowercase 8-4-4-4-12, first slice of a fat file). provision_team_identifier = TeamIdentifier[0];
provision_application_identifier = Entitlements["application-identifier"] verbatim ("TEAMID.com.x.y").
provision_provisions_all_devices: a profile without the key is a non-enterprise profile -> false;
provision_device_count = len(ProvisionedDevices) (0 when the key is absent but a profile exists).
Not a zip/plist/profile/Mach-O, no .app, no profile, key absent -> "none"."""
import io
import posixpath
import re
import zipfile

_IPA_FMTS = ("ipa", "ios", "ios_app")
_KEYS = {
    "bundle_identifier": "CFBundleIdentifier", "bundle_id": "CFBundleIdentifier",
    "cf_bundle_identifier": "CFBundleIdentifier",
    "bundle_short_version": "CFBundleShortVersionString", "bundle_short_version_string": "CFBundleShortVersionString",
    "cf_bundle_short_version_string": "CFBundleShortVersionString", "short_version_string": "CFBundleShortVersionString",
    "bundle_version": "CFBundleVersion", "cf_bundle_version": "CFBundleVersion",
    "bundle_display_name": "CFBundleDisplayName", "cf_bundle_display_name": "CFBundleDisplayName",
    "display_name": "CFBundleDisplayName",
    "bundle_name": "CFBundleName", "cf_bundle_name": "CFBundleName",
    "bundle_executable": "CFBundleExecutable", "cf_bundle_executable": "CFBundleExecutable",
    "executable_name": "CFBundleExecutable",
    "bundle_package_type": "CFBundlePackageType", "cf_bundle_package_type": "CFBundlePackageType",
    "minimum_os_version": "MinimumOSVersion", "min_os_version": "MinimumOSVersion",
    "supported_platforms": "CFBundleSupportedPlatforms", "cf_bundle_supported_platforms": "CFBundleSupportedPlatforms",
    "device_family": "UIDeviceFamily", "ui_device_family": "UIDeviceFamily",
    "dt_platform_name": "DTPlatformName", "dt_platform_version": "DTPlatformVersion", "dt_sdk_name": "DTSDKName",
    "dt_xcode": "DTXcode", "dt_xcode_build": "DTXcodeBuild",
    "requires_iphone_os": "LSRequiresIPhoneOS", "ls_requires_iphone_os": "LSRequiresIPhoneOS",
    "ui_required_device_capabilities": "UIRequiredDeviceCapabilities",
}
_BUNDLE_META = ("app_bundle_name", "app_name", "app_bundle", "app_bundle_path", "app_path", "info_plist_path",
                "info_plist_format", "app_count", "app_bundle_names", "platform_name")
_EXEC = {"executable_cpu_type_set": "cpu", "executable_cpu_types": "cpu", "executable_cputype_set": "cpu",
         "cpu_type_set": "cpu", "executable_arch_names": "arch", "executable_architectures": "arch",
         "executable_lc_uuid": "uuid", "executable_uuid": "uuid", "lc_uuid": "uuid",
         "executable_min_os": "minos", "executable_min_os_version": "minos", "executable_minos": "minos",
         "executable_is_fat": "fat", "executable_slice_count": "slices", "executable_present": "present",
         "executable_path": "path"}
# provision_<field> -> top-level key of the profile plist (or a callable over it)
_PROV = {
    "team_identifier": lambda p: _first(p.get("TeamIdentifier")), "team_id": lambda p: _first(p.get("TeamIdentifier")),
    "team_identifiers": lambda p: p.get("TeamIdentifier"),
    "team_name": "TeamName", "app_id_name": "AppIDName", "uuid": "UUID", "name": "Name",
    "expiration_utc": "ExpirationDate", "expiration_date": "ExpirationDate",
    "creation_utc": "CreationDate", "creation_date": "CreationDate",
    "platform": "Platform", "platforms": "Platform", "version": "Version", "time_to_live": "TimeToLive",
    "is_xcode_managed": "IsXcodeManaged",
    "application_identifier": lambda p: _ent(p, "application-identifier"),
    "app_id": lambda p: _ent(p, "application-identifier"),
    "get_task_allow": lambda p: _ent(p, "get-task-allow"),
    "aps_environment": lambda p: _ent(p, "aps-environment"),
    "keychain_access_groups": lambda p: _ent(p, "keychain-access-groups"),
    "team_identifier_entitlement": lambda p: _ent(p, "com.apple.developer.team-identifier"),
    "entitlement_keys": lambda p: list(p["Entitlements"]) if isinstance(p.get("Entitlements"), dict) else None,
    "provisions_all_devices": lambda p: bool(p.get("ProvisionsAllDevices", False)),
    "device_count": lambda p: len(p.get("ProvisionedDevices") or []),
    "provisioned_device_count": lambda p: len(p.get("ProvisionedDevices") or []),
    "provisioned_devices": "ProvisionedDevices",
    "developer_certificate_count": lambda p: len(p.get("DeveloperCertificates") or []),
    "certificate_count": lambda p: len(p.get("DeveloperCertificates") or []),
}
_ITUNES = {"itunes_item_id": "itemId", "item_id": "itemId", "itunes_metadata_item_id": "itemId",
           "itunes_item_name": "itemName", "item_name": "itemName",
           "itunes_artist_name": "artistName", "artist_name": "artistName",
           "itunes_software_version_bundle_id": "softwareVersionBundleId",
           "software_version_bundle_id": "softwareVersionBundleId",
           "itunes_bundle_short_version_string": "bundleShortVersionString",
           "itunes_bundle_version": "bundleVersion", "itunes_genre": "genre", "itunes_apple_id": "appleId"}
_PRESENT = ("has_mobileprovision", "mobileprovision_present", "embedded_mobileprovision_present",
            "has_embedded_mobileprovision", "provision_present")
_IT_PRESENT = ("has_itunes_metadata", "itunes_metadata_present")

FIELDS = {
    ("ipa", "bundle_identifier"): "ipa_value", ("ipa", "bundle_id"): "ipa_value",
    ("ipa", "cf_bundle_identifier"): "ipa_value", ("ipa", "bundle_short_version"): "ipa_value",
    ("ipa", "bundle_short_version_string"): "ipa_value", ("ipa", "cf_bundle_short_version_string"): "ipa_value",
    ("ipa", "short_version_string"): "ipa_value", ("ipa", "bundle_version"): "ipa_value",
    ("ipa", "cf_bundle_version"): "ipa_value", ("ipa", "bundle_display_name"): "ipa_value",
    ("ipa", "cf_bundle_display_name"): "ipa_value", ("ipa", "display_name"): "ipa_value",
    ("ipa", "bundle_name"): "ipa_value", ("ipa", "cf_bundle_name"): "ipa_value",
    ("ipa", "bundle_executable"): "ipa_value", ("ipa", "cf_bundle_executable"): "ipa_value",
    ("ipa", "executable_name"): "ipa_value", ("ipa", "bundle_package_type"): "ipa_value",
    ("ipa", "cf_bundle_package_type"): "ipa_value", ("ipa", "minimum_os_version"): "ipa_value",
    ("ipa", "min_os_version"): "ipa_value", ("ipa", "supported_platforms"): "ipa_value",
    ("ipa", "cf_bundle_supported_platforms"): "ipa_value", ("ipa", "device_family"): "ipa_value",
    ("ipa", "ui_device_family"): "ipa_value", ("ipa", "dt_platform_name"): "ipa_value",
    ("ipa", "dt_platform_version"): "ipa_value", ("ipa", "dt_sdk_name"): "ipa_value",
    ("ipa", "dt_xcode"): "ipa_value", ("ipa", "dt_xcode_build"): "ipa_value",
    ("ipa", "requires_iphone_os"): "ipa_value", ("ipa", "ls_requires_iphone_os"): "ipa_value",
    ("ipa", "ui_required_device_capabilities"): "ipa_value", ("ipa", "app_bundle_name"): "ipa_value",
    ("ipa", "app_name"): "ipa_value", ("ipa", "app_bundle"): "ipa_value", ("ipa", "app_bundle_path"): "ipa_value",
    ("ipa", "app_path"): "ipa_value", ("ipa", "info_plist_path"): "ipa_value",
    ("ipa", "info_plist_format"): "ipa_value", ("ipa", "app_count"): "ipa_value",
    ("ipa", "app_bundle_names"): "ipa_value", ("ipa", "platform_name"): "ipa_value",
    ("ipa", "executable_cpu_type_set"): "ipa_value", ("ipa", "executable_cpu_types"): "ipa_value",
    ("ipa", "executable_cputype_set"): "ipa_value", ("ipa", "cpu_type_set"): "ipa_value",
    ("ipa", "executable_arch_names"): "ipa_value", ("ipa", "executable_architectures"): "ipa_value",
    ("ipa", "executable_lc_uuid"): "ipa_value", ("ipa", "executable_uuid"): "ipa_value",
    ("ipa", "lc_uuid"): "ipa_value", ("ipa", "executable_min_os"): "ipa_value",
    ("ipa", "executable_min_os_version"): "ipa_value", ("ipa", "executable_minos"): "ipa_value",
    ("ipa", "executable_is_fat"): "ipa_value", ("ipa", "executable_slice_count"): "ipa_value",
    ("ipa", "executable_present"): "ipa_value", ("ipa", "executable_path"): "ipa_value",
    ("ipa", "itunes_item_id"): "ipa_value", ("ipa", "item_id"): "ipa_value",
    ("ipa", "itunes_metadata_item_id"): "ipa_value", ("ipa", "itunes_item_name"): "ipa_value",
    ("ipa", "item_name"): "ipa_value", ("ipa", "itunes_artist_name"): "ipa_value",
    ("ipa", "artist_name"): "ipa_value", ("ipa", "itunes_software_version_bundle_id"): "ipa_value",
    ("ipa", "software_version_bundle_id"): "ipa_value", ("ipa", "itunes_bundle_short_version_string"): "ipa_value",
    ("ipa", "itunes_bundle_version"): "ipa_value", ("ipa", "itunes_genre"): "ipa_value",
    ("ipa", "itunes_apple_id"): "ipa_value", ("ipa", "has_mobileprovision"): "ipa_value",
    ("ipa", "mobileprovision_present"): "ipa_value", ("ipa", "embedded_mobileprovision_present"): "ipa_value",
    ("ipa", "has_embedded_mobileprovision"): "ipa_value", ("ipa", "provision_present"): "ipa_value",
    ("ipa", "has_itunes_metadata"): "ipa_value", ("ipa", "itunes_metadata_present"): "ipa_value",
    ("ipa", "provision_team_identifier"): "ipa_value", ("ipa", "mobileprovision_team_identifier"): "ipa_value",
    ("ipa", "provision_team_id"): "ipa_value", ("ipa", "mobileprovision_team_id"): "ipa_value",
    ("ipa", "provision_team_identifiers"): "ipa_value", ("ipa", "mobileprovision_team_identifiers"): "ipa_value",
    ("ipa", "provision_team_name"): "ipa_value", ("ipa", "mobileprovision_team_name"): "ipa_value",
    ("ipa", "provision_app_id_name"): "ipa_value", ("ipa", "mobileprovision_app_id_name"): "ipa_value",
    ("ipa", "provision_uuid"): "ipa_value", ("ipa", "mobileprovision_uuid"): "ipa_value",
    ("ipa", "provision_name"): "ipa_value", ("ipa", "mobileprovision_name"): "ipa_value",
    ("ipa", "provision_expiration_utc"): "ipa_value", ("ipa", "mobileprovision_expiration_utc"): "ipa_value",
    ("ipa", "provision_expiration_date"): "ipa_value", ("ipa", "mobileprovision_expiration_date"): "ipa_value",
    ("ipa", "provision_creation_utc"): "ipa_value", ("ipa", "mobileprovision_creation_utc"): "ipa_value",
    ("ipa", "provision_creation_date"): "ipa_value", ("ipa", "mobileprovision_creation_date"): "ipa_value",
    ("ipa", "provision_platform"): "ipa_value", ("ipa", "mobileprovision_platform"): "ipa_value",
    ("ipa", "provision_platforms"): "ipa_value", ("ipa", "mobileprovision_platforms"): "ipa_value",
    ("ipa", "provision_version"): "ipa_value", ("ipa", "mobileprovision_version"): "ipa_value",
    ("ipa", "provision_time_to_live"): "ipa_value", ("ipa", "mobileprovision_time_to_live"): "ipa_value",
    ("ipa", "provision_is_xcode_managed"): "ipa_value", ("ipa", "mobileprovision_is_xcode_managed"): "ipa_value",
    ("ipa", "provision_application_identifier"): "ipa_value",
    ("ipa", "mobileprovision_application_identifier"): "ipa_value", ("ipa", "provision_app_id"): "ipa_value",
    ("ipa", "mobileprovision_app_id"): "ipa_value", ("ipa", "provision_get_task_allow"): "ipa_value",
    ("ipa", "mobileprovision_get_task_allow"): "ipa_value", ("ipa", "provision_aps_environment"): "ipa_value",
    ("ipa", "mobileprovision_aps_environment"): "ipa_value", ("ipa", "provision_keychain_access_groups"): "ipa_value",
    ("ipa", "mobileprovision_keychain_access_groups"): "ipa_value",
    ("ipa", "provision_team_identifier_entitlement"): "ipa_value",
    ("ipa", "mobileprovision_team_identifier_entitlement"): "ipa_value",
    ("ipa", "provision_entitlement_keys"): "ipa_value", ("ipa", "mobileprovision_entitlement_keys"): "ipa_value",
    ("ipa", "provision_provisions_all_devices"): "ipa_value",
    ("ipa", "mobileprovision_provisions_all_devices"): "ipa_value", ("ipa", "provision_device_count"): "ipa_value",
    ("ipa", "mobileprovision_device_count"): "ipa_value", ("ipa", "provision_provisioned_device_count"): "ipa_value",
    ("ipa", "mobileprovision_provisioned_device_count"): "ipa_value",
    ("ipa", "provision_provisioned_devices"): "ipa_value",
    ("ipa", "mobileprovision_provisioned_devices"): "ipa_value",
    ("ipa", "provision_developer_certificate_count"): "ipa_value",
    ("ipa", "mobileprovision_developer_certificate_count"): "ipa_value",
    ("ipa", "provision_certificate_count"): "ipa_value", ("ipa", "mobileprovision_certificate_count"): "ipa_value",
    ("ipa", "value_*"): "ipa_value",
    ("ios", "bundle_identifier"): "ipa_value", ("ios", "bundle_id"): "ipa_value",
    ("ios", "cf_bundle_identifier"): "ipa_value", ("ios", "bundle_short_version"): "ipa_value",
    ("ios", "bundle_short_version_string"): "ipa_value", ("ios", "cf_bundle_short_version_string"): "ipa_value",
    ("ios", "short_version_string"): "ipa_value", ("ios", "bundle_version"): "ipa_value",
    ("ios", "cf_bundle_version"): "ipa_value", ("ios", "bundle_display_name"): "ipa_value",
    ("ios", "cf_bundle_display_name"): "ipa_value", ("ios", "display_name"): "ipa_value",
    ("ios", "bundle_name"): "ipa_value", ("ios", "cf_bundle_name"): "ipa_value",
    ("ios", "bundle_executable"): "ipa_value", ("ios", "cf_bundle_executable"): "ipa_value",
    ("ios", "executable_name"): "ipa_value", ("ios", "bundle_package_type"): "ipa_value",
    ("ios", "cf_bundle_package_type"): "ipa_value", ("ios", "minimum_os_version"): "ipa_value",
    ("ios", "min_os_version"): "ipa_value", ("ios", "supported_platforms"): "ipa_value",
    ("ios", "cf_bundle_supported_platforms"): "ipa_value", ("ios", "device_family"): "ipa_value",
    ("ios", "ui_device_family"): "ipa_value", ("ios", "dt_platform_name"): "ipa_value",
    ("ios", "dt_platform_version"): "ipa_value", ("ios", "dt_sdk_name"): "ipa_value",
    ("ios", "dt_xcode"): "ipa_value", ("ios", "dt_xcode_build"): "ipa_value",
    ("ios", "requires_iphone_os"): "ipa_value", ("ios", "ls_requires_iphone_os"): "ipa_value",
    ("ios", "ui_required_device_capabilities"): "ipa_value", ("ios", "app_bundle_name"): "ipa_value",
    ("ios", "app_name"): "ipa_value", ("ios", "app_bundle"): "ipa_value", ("ios", "app_bundle_path"): "ipa_value",
    ("ios", "app_path"): "ipa_value", ("ios", "info_plist_path"): "ipa_value",
    ("ios", "info_plist_format"): "ipa_value", ("ios", "app_count"): "ipa_value",
    ("ios", "app_bundle_names"): "ipa_value", ("ios", "platform_name"): "ipa_value",
    ("ios", "executable_cpu_type_set"): "ipa_value", ("ios", "executable_cpu_types"): "ipa_value",
    ("ios", "executable_cputype_set"): "ipa_value", ("ios", "cpu_type_set"): "ipa_value",
    ("ios", "executable_arch_names"): "ipa_value", ("ios", "executable_architectures"): "ipa_value",
    ("ios", "executable_lc_uuid"): "ipa_value", ("ios", "executable_uuid"): "ipa_value",
    ("ios", "lc_uuid"): "ipa_value", ("ios", "executable_min_os"): "ipa_value",
    ("ios", "executable_min_os_version"): "ipa_value", ("ios", "executable_minos"): "ipa_value",
    ("ios", "executable_is_fat"): "ipa_value", ("ios", "executable_slice_count"): "ipa_value",
    ("ios", "executable_present"): "ipa_value", ("ios", "executable_path"): "ipa_value",
    ("ios", "itunes_item_id"): "ipa_value", ("ios", "item_id"): "ipa_value",
    ("ios", "itunes_metadata_item_id"): "ipa_value", ("ios", "itunes_item_name"): "ipa_value",
    ("ios", "item_name"): "ipa_value", ("ios", "itunes_artist_name"): "ipa_value",
    ("ios", "artist_name"): "ipa_value", ("ios", "itunes_software_version_bundle_id"): "ipa_value",
    ("ios", "software_version_bundle_id"): "ipa_value", ("ios", "itunes_bundle_short_version_string"): "ipa_value",
    ("ios", "itunes_bundle_version"): "ipa_value", ("ios", "itunes_genre"): "ipa_value",
    ("ios", "itunes_apple_id"): "ipa_value", ("ios", "has_mobileprovision"): "ipa_value",
    ("ios", "mobileprovision_present"): "ipa_value", ("ios", "embedded_mobileprovision_present"): "ipa_value",
    ("ios", "has_embedded_mobileprovision"): "ipa_value", ("ios", "provision_present"): "ipa_value",
    ("ios", "has_itunes_metadata"): "ipa_value", ("ios", "itunes_metadata_present"): "ipa_value",
    ("ios", "provision_team_identifier"): "ipa_value", ("ios", "mobileprovision_team_identifier"): "ipa_value",
    ("ios", "provision_team_id"): "ipa_value", ("ios", "mobileprovision_team_id"): "ipa_value",
    ("ios", "provision_team_identifiers"): "ipa_value", ("ios", "mobileprovision_team_identifiers"): "ipa_value",
    ("ios", "provision_team_name"): "ipa_value", ("ios", "mobileprovision_team_name"): "ipa_value",
    ("ios", "provision_app_id_name"): "ipa_value", ("ios", "mobileprovision_app_id_name"): "ipa_value",
    ("ios", "provision_uuid"): "ipa_value", ("ios", "mobileprovision_uuid"): "ipa_value",
    ("ios", "provision_name"): "ipa_value", ("ios", "mobileprovision_name"): "ipa_value",
    ("ios", "provision_expiration_utc"): "ipa_value", ("ios", "mobileprovision_expiration_utc"): "ipa_value",
    ("ios", "provision_expiration_date"): "ipa_value", ("ios", "mobileprovision_expiration_date"): "ipa_value",
    ("ios", "provision_creation_utc"): "ipa_value", ("ios", "mobileprovision_creation_utc"): "ipa_value",
    ("ios", "provision_creation_date"): "ipa_value", ("ios", "mobileprovision_creation_date"): "ipa_value",
    ("ios", "provision_platform"): "ipa_value", ("ios", "mobileprovision_platform"): "ipa_value",
    ("ios", "provision_platforms"): "ipa_value", ("ios", "mobileprovision_platforms"): "ipa_value",
    ("ios", "provision_version"): "ipa_value", ("ios", "mobileprovision_version"): "ipa_value",
    ("ios", "provision_time_to_live"): "ipa_value", ("ios", "mobileprovision_time_to_live"): "ipa_value",
    ("ios", "provision_is_xcode_managed"): "ipa_value", ("ios", "mobileprovision_is_xcode_managed"): "ipa_value",
    ("ios", "provision_application_identifier"): "ipa_value",
    ("ios", "mobileprovision_application_identifier"): "ipa_value", ("ios", "provision_app_id"): "ipa_value",
    ("ios", "mobileprovision_app_id"): "ipa_value", ("ios", "provision_get_task_allow"): "ipa_value",
    ("ios", "mobileprovision_get_task_allow"): "ipa_value", ("ios", "provision_aps_environment"): "ipa_value",
    ("ios", "mobileprovision_aps_environment"): "ipa_value", ("ios", "provision_keychain_access_groups"): "ipa_value",
    ("ios", "mobileprovision_keychain_access_groups"): "ipa_value",
    ("ios", "provision_team_identifier_entitlement"): "ipa_value",
    ("ios", "mobileprovision_team_identifier_entitlement"): "ipa_value",
    ("ios", "provision_entitlement_keys"): "ipa_value", ("ios", "mobileprovision_entitlement_keys"): "ipa_value",
    ("ios", "provision_provisions_all_devices"): "ipa_value",
    ("ios", "mobileprovision_provisions_all_devices"): "ipa_value", ("ios", "provision_device_count"): "ipa_value",
    ("ios", "mobileprovision_device_count"): "ipa_value", ("ios", "provision_provisioned_device_count"): "ipa_value",
    ("ios", "mobileprovision_provisioned_device_count"): "ipa_value",
    ("ios", "provision_provisioned_devices"): "ipa_value",
    ("ios", "mobileprovision_provisioned_devices"): "ipa_value",
    ("ios", "provision_developer_certificate_count"): "ipa_value",
    ("ios", "mobileprovision_developer_certificate_count"): "ipa_value",
    ("ios", "provision_certificate_count"): "ipa_value", ("ios", "mobileprovision_certificate_count"): "ipa_value",
    ("ios", "value_*"): "ipa_value",
    ("ios_app", "bundle_identifier"): "ipa_value", ("ios_app", "bundle_id"): "ipa_value",
    ("ios_app", "cf_bundle_identifier"): "ipa_value", ("ios_app", "bundle_short_version"): "ipa_value",
    ("ios_app", "bundle_short_version_string"): "ipa_value",
    ("ios_app", "cf_bundle_short_version_string"): "ipa_value", ("ios_app", "short_version_string"): "ipa_value",
    ("ios_app", "bundle_version"): "ipa_value", ("ios_app", "cf_bundle_version"): "ipa_value",
    ("ios_app", "bundle_display_name"): "ipa_value", ("ios_app", "cf_bundle_display_name"): "ipa_value",
    ("ios_app", "display_name"): "ipa_value", ("ios_app", "bundle_name"): "ipa_value",
    ("ios_app", "cf_bundle_name"): "ipa_value", ("ios_app", "bundle_executable"): "ipa_value",
    ("ios_app", "cf_bundle_executable"): "ipa_value", ("ios_app", "executable_name"): "ipa_value",
    ("ios_app", "bundle_package_type"): "ipa_value", ("ios_app", "cf_bundle_package_type"): "ipa_value",
    ("ios_app", "minimum_os_version"): "ipa_value", ("ios_app", "min_os_version"): "ipa_value",
    ("ios_app", "supported_platforms"): "ipa_value", ("ios_app", "cf_bundle_supported_platforms"): "ipa_value",
    ("ios_app", "device_family"): "ipa_value", ("ios_app", "ui_device_family"): "ipa_value",
    ("ios_app", "dt_platform_name"): "ipa_value", ("ios_app", "dt_platform_version"): "ipa_value",
    ("ios_app", "dt_sdk_name"): "ipa_value", ("ios_app", "dt_xcode"): "ipa_value",
    ("ios_app", "dt_xcode_build"): "ipa_value", ("ios_app", "requires_iphone_os"): "ipa_value",
    ("ios_app", "ls_requires_iphone_os"): "ipa_value", ("ios_app", "ui_required_device_capabilities"): "ipa_value",
    ("ios_app", "app_bundle_name"): "ipa_value", ("ios_app", "app_name"): "ipa_value",
    ("ios_app", "app_bundle"): "ipa_value", ("ios_app", "app_bundle_path"): "ipa_value",
    ("ios_app", "app_path"): "ipa_value", ("ios_app", "info_plist_path"): "ipa_value",
    ("ios_app", "info_plist_format"): "ipa_value", ("ios_app", "app_count"): "ipa_value",
    ("ios_app", "app_bundle_names"): "ipa_value", ("ios_app", "platform_name"): "ipa_value",
    ("ios_app", "executable_cpu_type_set"): "ipa_value", ("ios_app", "executable_cpu_types"): "ipa_value",
    ("ios_app", "executable_cputype_set"): "ipa_value", ("ios_app", "cpu_type_set"): "ipa_value",
    ("ios_app", "executable_arch_names"): "ipa_value", ("ios_app", "executable_architectures"): "ipa_value",
    ("ios_app", "executable_lc_uuid"): "ipa_value", ("ios_app", "executable_uuid"): "ipa_value",
    ("ios_app", "lc_uuid"): "ipa_value", ("ios_app", "executable_min_os"): "ipa_value",
    ("ios_app", "executable_min_os_version"): "ipa_value", ("ios_app", "executable_minos"): "ipa_value",
    ("ios_app", "executable_is_fat"): "ipa_value", ("ios_app", "executable_slice_count"): "ipa_value",
    ("ios_app", "executable_present"): "ipa_value", ("ios_app", "executable_path"): "ipa_value",
    ("ios_app", "itunes_item_id"): "ipa_value", ("ios_app", "item_id"): "ipa_value",
    ("ios_app", "itunes_metadata_item_id"): "ipa_value", ("ios_app", "itunes_item_name"): "ipa_value",
    ("ios_app", "item_name"): "ipa_value", ("ios_app", "itunes_artist_name"): "ipa_value",
    ("ios_app", "artist_name"): "ipa_value", ("ios_app", "itunes_software_version_bundle_id"): "ipa_value",
    ("ios_app", "software_version_bundle_id"): "ipa_value",
    ("ios_app", "itunes_bundle_short_version_string"): "ipa_value", ("ios_app", "itunes_bundle_version"): "ipa_value",
    ("ios_app", "itunes_genre"): "ipa_value", ("ios_app", "itunes_apple_id"): "ipa_value",
    ("ios_app", "has_mobileprovision"): "ipa_value", ("ios_app", "mobileprovision_present"): "ipa_value",
    ("ios_app", "embedded_mobileprovision_present"): "ipa_value",
    ("ios_app", "has_embedded_mobileprovision"): "ipa_value", ("ios_app", "provision_present"): "ipa_value",
    ("ios_app", "has_itunes_metadata"): "ipa_value", ("ios_app", "itunes_metadata_present"): "ipa_value",
    ("ios_app", "provision_team_identifier"): "ipa_value",
    ("ios_app", "mobileprovision_team_identifier"): "ipa_value", ("ios_app", "provision_team_id"): "ipa_value",
    ("ios_app", "mobileprovision_team_id"): "ipa_value", ("ios_app", "provision_team_identifiers"): "ipa_value",
    ("ios_app", "mobileprovision_team_identifiers"): "ipa_value", ("ios_app", "provision_team_name"): "ipa_value",
    ("ios_app", "mobileprovision_team_name"): "ipa_value", ("ios_app", "provision_app_id_name"): "ipa_value",
    ("ios_app", "mobileprovision_app_id_name"): "ipa_value", ("ios_app", "provision_uuid"): "ipa_value",
    ("ios_app", "mobileprovision_uuid"): "ipa_value", ("ios_app", "provision_name"): "ipa_value",
    ("ios_app", "mobileprovision_name"): "ipa_value", ("ios_app", "provision_expiration_utc"): "ipa_value",
    ("ios_app", "mobileprovision_expiration_utc"): "ipa_value", ("ios_app", "provision_expiration_date"): "ipa_value",
    ("ios_app", "mobileprovision_expiration_date"): "ipa_value", ("ios_app", "provision_creation_utc"): "ipa_value",
    ("ios_app", "mobileprovision_creation_utc"): "ipa_value", ("ios_app", "provision_creation_date"): "ipa_value",
    ("ios_app", "mobileprovision_creation_date"): "ipa_value", ("ios_app", "provision_platform"): "ipa_value",
    ("ios_app", "mobileprovision_platform"): "ipa_value", ("ios_app", "provision_platforms"): "ipa_value",
    ("ios_app", "mobileprovision_platforms"): "ipa_value", ("ios_app", "provision_version"): "ipa_value",
    ("ios_app", "mobileprovision_version"): "ipa_value", ("ios_app", "provision_time_to_live"): "ipa_value",
    ("ios_app", "mobileprovision_time_to_live"): "ipa_value", ("ios_app", "provision_is_xcode_managed"): "ipa_value",
    ("ios_app", "mobileprovision_is_xcode_managed"): "ipa_value",
    ("ios_app", "provision_application_identifier"): "ipa_value",
    ("ios_app", "mobileprovision_application_identifier"): "ipa_value", ("ios_app", "provision_app_id"): "ipa_value",
    ("ios_app", "mobileprovision_app_id"): "ipa_value", ("ios_app", "provision_get_task_allow"): "ipa_value",
    ("ios_app", "mobileprovision_get_task_allow"): "ipa_value", ("ios_app", "provision_aps_environment"): "ipa_value",
    ("ios_app", "mobileprovision_aps_environment"): "ipa_value",
    ("ios_app", "provision_keychain_access_groups"): "ipa_value",
    ("ios_app", "mobileprovision_keychain_access_groups"): "ipa_value",
    ("ios_app", "provision_team_identifier_entitlement"): "ipa_value",
    ("ios_app", "mobileprovision_team_identifier_entitlement"): "ipa_value",
    ("ios_app", "provision_entitlement_keys"): "ipa_value",
    ("ios_app", "mobileprovision_entitlement_keys"): "ipa_value",
    ("ios_app", "provision_provisions_all_devices"): "ipa_value",
    ("ios_app", "mobileprovision_provisions_all_devices"): "ipa_value",
    ("ios_app", "provision_device_count"): "ipa_value", ("ios_app", "mobileprovision_device_count"): "ipa_value",
    ("ios_app", "provision_provisioned_device_count"): "ipa_value",
    ("ios_app", "mobileprovision_provisioned_device_count"): "ipa_value",
    ("ios_app", "provision_provisioned_devices"): "ipa_value",
    ("ios_app", "mobileprovision_provisioned_devices"): "ipa_value",
    ("ios_app", "provision_developer_certificate_count"): "ipa_value",
    ("ios_app", "mobileprovision_developer_certificate_count"): "ipa_value",
    ("ios_app", "provision_certificate_count"): "ipa_value",
    ("ios_app", "mobileprovision_certificate_count"): "ipa_value", ("ios_app", "value_*"): "ipa_value",
    ("mobileprovision", "team_identifier"): "ipa_value", ("mobileprovision", "team_id"): "ipa_value",
    ("mobileprovision", "team_identifiers"): "ipa_value", ("mobileprovision", "team_name"): "ipa_value",
    ("mobileprovision", "app_id_name"): "ipa_value", ("mobileprovision", "uuid"): "ipa_value",
    ("mobileprovision", "name"): "ipa_value", ("mobileprovision", "expiration_utc"): "ipa_value",
    ("mobileprovision", "expiration_date"): "ipa_value", ("mobileprovision", "creation_utc"): "ipa_value",
    ("mobileprovision", "creation_date"): "ipa_value", ("mobileprovision", "platform"): "ipa_value",
    ("mobileprovision", "platforms"): "ipa_value", ("mobileprovision", "version"): "ipa_value",
    ("mobileprovision", "time_to_live"): "ipa_value", ("mobileprovision", "is_xcode_managed"): "ipa_value",
    ("mobileprovision", "application_identifier"): "ipa_value", ("mobileprovision", "app_id"): "ipa_value",
    ("mobileprovision", "get_task_allow"): "ipa_value", ("mobileprovision", "aps_environment"): "ipa_value",
    ("mobileprovision", "keychain_access_groups"): "ipa_value",
    ("mobileprovision", "team_identifier_entitlement"): "ipa_value",
    ("mobileprovision", "entitlement_keys"): "ipa_value", ("mobileprovision", "provisions_all_devices"): "ipa_value",
    ("mobileprovision", "device_count"): "ipa_value", ("mobileprovision", "provisioned_device_count"): "ipa_value",
    ("mobileprovision", "provisioned_devices"): "ipa_value",
    ("mobileprovision", "developer_certificate_count"): "ipa_value",
    ("mobileprovision", "certificate_count"): "ipa_value", ("mobileprovision", "value_*"): "ipa_value",
}

_APP = re.compile(r"(?:.*/)?[^/]+\.app$", re.I)
_PL = re.compile(rb"<\?xml.*?</plist>", re.S)


def _first(v):
    return v[0] if isinstance(v, list) and v else None


def _ent(p, k):
    e = p.get("Entitlements")
    return e.get(k) if isinstance(e, dict) else None


def _profile(b):
    """The XML plist dict embedded in a mobileprovision (CMS DER) or a plain profile plist, or None."""
    if not b:
        return None
    from .app import _plist
    m = _PL.search(bytes(b))
    pl = _plist(m.group(0)) if m else _plist(b)
    if pl is None or not any(k in pl for k in ("TeamIdentifier", "ExpirationDate", "UUID", "Entitlements")):
        return None
    return pl


def _render(v):
    import datetime
    if isinstance(v, datetime.datetime):
        if v.tzinfo is not None:
            v = v.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")
    from .app import _render as r
    return r(v)


def _apps(zr):
    """[(app_dir, info_plist_member)], Payload/*.app first, shallowest first."""
    out = []
    for n in zr.info:
        if posixpath.basename(n) == "Info.plist" and _APP.fullmatch(posixpath.dirname(n)):
            d = posixpath.dirname(n)
            out.append((d, n))
    return sorted(out, key=lambda c: (not c[0].startswith("Payload/"), c[0].count("/"), c[0]))


def _pick(apps, ctx):
    hint = " ".join(str(ctx.get(k) or "") for k in ("member", "artifact")).lower()
    hint += " " + str((ctx.get("question") or {}).get("question") or "").lower()
    named = [a for a in apps if posixpath.basename(a[0]).lower() in hint]
    return named[0] if named else apps[0]


def _load(b, ctx, depth=0):
    from .app import _Zip, _plist, _is_macho
    if b[:4] in (b"PK\x03\x04", b"PK\x05\x06"):
        try:
            zr = _Zip(zipfile.ZipFile(io.BytesIO(b)))
        except Exception:
            return None
        apps = _apps(zr)
        if not apps:
            if depth == 0:
                inner = [n for n in zr.info if n.lower().endswith(".ipa")]
                if len(inner) == 1:
                    data = zr.read(inner[0])
                    if data:
                        return _load(data, ctx, 1)
            return {"zip": True, "apps": []}
        app, pm = _pick(apps, ctx)
        raw = zr.read(pm)
        pl = _plist(raw)
        st = {"zip": True, "apps": apps, "app": app, "plist_member": pm, "plist": pl,
              "plist_format": ("binary" if raw.startswith(b"bplist00") else "xml") if pl is not None else None,
              "exe": None, "exe_path": None}
        exe = (pl or {}).get("CFBundleExecutable")
        if isinstance(exe, str) and exe and "/" not in exe:
            data = zr.read(f"{app}/{exe}")
            if data is not None:
                st["exe"], st["exe_path"] = data, zr.resolve(f"{app}/{exe}")
        prov = zr.read(f"{app}/embedded.mobileprovision")
        st["prov_present"] = prov is not None
        st["prov"] = _profile(prov) if prov is not None else None
        root = posixpath.dirname(posixpath.dirname(app)) if app.startswith("Payload/") or "/Payload/" in app else None
        it = zr.read(posixpath.join(root, "iTunesMetadata.plist") if root else "iTunesMetadata.plist")
        st["itunes"] = _plist(it) if it is not None else None
        st["itunes_present"] = it is not None
        return st
    prov = _profile(b)
    if prov is not None:
        return {"prov": prov, "prov_present": True}
    pl = _plist(b)
    if pl is not None:
        return {"plist": pl, "plist_format": "binary" if b.lstrip()[:8] == b"bplist00" else "xml", "exe": False}
    if _is_macho(b):
        return {"exe": b, "bare_exe": True}
    return None


def _squash(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def ipa_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), ctx or {})
    except Exception:
        return None


def _value(b, ctx):
    f = ctx.get("field") or ""
    fmt = ctx.get("fmt") or ""
    st = _load(b, ctx)
    if st is None:
        return "none"
    if fmt == "mobileprovision" and not f.startswith("provision_"):
        f = "provision_" + f
    if f.startswith("mobileprovision_"):
        f = "provision_" + f[len("mobileprovision_"):]
    if f in _PRESENT:
        return bool(st.get("prov_present")) if "zip" in st or "prov" in st else "none"
    if f in _IT_PRESENT:
        return bool(st.get("itunes_present")) if "zip" in st else "none"
    if f.startswith("provision_") and f[len("provision_"):] in _PROV or (f.startswith("value_") and fmt ==
                                                                          "mobileprovision"):
        p = st.get("prov")
        if p is None:
            return "none"
        if f.startswith("value_"):
            return _by_key(p, ctx.get("param") or f[len("value_"):])
        spec = _PROV[f[len("provision_"):]]
        v = spec(p) if callable(spec) else p.get(spec)
        return "none" if v is None else _render(v)
    if f in _ITUNES:
        it = st.get("itunes")
        v = it.get(_ITUNES[f]) if it else None
        return "none" if v is None else _render(v)
    pl = st.get("plist")
    if f.startswith("value_"):
        return "none" if pl is None else _by_key(pl, ctx.get("param") or f[len("value_"):])
    if f in _KEYS:
        if pl is None:
            return "none"
        v = pl.get(_KEYS[f])
        return "none" if v is None else _render(v)
    if f == "platform_name":
        if pl is None:
            return "none"
        v = pl.get("DTPlatformName") or _first(pl.get("CFBundleSupportedPlatforms"))
        return "none" if v is None else _render(v)
    if f in ("app_bundle_name", "app_name", "app_bundle"):
        return posixpath.basename(st["app"]) if st.get("app") else "none"
    if f in ("app_bundle_path", "app_path"):
        return st.get("app") or "none"
    if f == "info_plist_path":
        return st.get("plist_member") or "none"
    if f == "info_plist_format":
        return st.get("plist_format") or "none"
    if f == "app_count":
        return len(st["apps"]) if "zip" in st else "none"
    if f == "app_bundle_names":
        return [posixpath.basename(a) for a, _ in st["apps"]] if "zip" in st else "none"
    kind = _EXEC.get(f)
    if kind is None:
        return None
    exe = st.get("exe")
    if exe is False:
        return None                       # a bare Info.plist: the executable is not in this member
    if kind == "present":
        return exe is not None if "zip" in st or st.get("bare_exe") else "none"
    if kind == "path":
        return st.get("exe_path") or "none"
    if not exe:
        return "none"
    if kind == "cpu":
        from lib.meta.macho import cpu_type_set
        return cpu_type_set(exe, ctx)
    if kind == "uuid":
        from .macho import macho_value
        return macho_value(exe, dict(ctx, field="uuid"))
    if kind == "minos":
        from .macho import macho_value
        return macho_value(exe, dict(ctx, field="min_os_version"))
    from .app import _slices, _arch_name
    sl = _slices(exe)
    if sl is None:
        return "none"
    if kind == "arch":
        return [_arch_name(c, s) for c, s in sl]
    if kind == "slices":
        return len(sl)
    if kind == "fat":
        return exe[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf")
    return None


def _by_key(d, want):
    w = _squash(want)
    for k, v in d.items():
        if _squash(k) == w:
            return _render(v)
    return "none"
