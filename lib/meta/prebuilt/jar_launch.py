"""JAR launcher / nested-jar / manifest-structure fields (prebuilt, SPECULATIVE -- never GM-asked yet; D22 flavor:
Spring Boot Start-Class vs launcher Main-Class, nested jars, "is it runnable?"). fmt jar + aliases java_archive / war /
ear / spring_boot. Manifest = JAR File Specification: `Name: value` lines (CRLF/LF/CR, 72-byte wrapped, a continuation
line starts with ONE space which is dropped), main section until the first blank line, then per-entry sections
each opening with `Name:`. Names are case-insensitive. Every field first descend()s the artifact ref
(`x.zip -> app.jar -> BOOT-INF/lib/dep.jar`, `app.jar!/BOOT-INF/lib/dep.jar`), so nested jars answer too.
Runtime semantics follow the JDK (checked with a java.util.jar oracle, see the fixtures):
  - java.util.jar.Attributes keeps the LAST value of a duplicated main attribute (`Main-Class` twice -> the 2nd runs);
    main_class_first / main_class_last expose both, duplicate_main_attribute_names lists names seen > 1 time
    (first-seen order, first spelling). The plain `<attr>` fields (and the GM-verified jar.main_class) stay FIRST-wins.
  - JarFile (java -jar) finds the manifest through the central directory: exact `META-INF/MANIFEST.MF`, else a
    case-insensitive match; JarInputStream reads local entries in stream order and only sees the manifest when it is
    entry 1, or entry 2 right after a `META-INF/` directory entry -> jar_input_stream_main_class / jar_file_main_class.
  - manifest_entry_index: 1-based position of the manifest member in stream (local header) order; absent -> "none".
  - main_class_is_launcher: Main-Class is a known fat-jar launcher (Spring Boot loader / launch Jar|War|Properties
    Launcher, Eclipse jar-in-jar JarRsrcLoader, One-JAR Boot, Capsule); effective_main_class = the launcher's target
    attribute (Start-Class / Rsrc-Main-Class / One-Jar-Main-Class / Application-Class; launcher without one -> "none"),
    else Main-Class.
  - main_class_entry_name = dotted Main-Class -> `a/b/C.class`; is_runnable / main_class_entry_present = Main-Class
    present AND that entry exists in the archive (library jar -> false). start_class_entry_* look under
    Spring-Boot-Classes (default BOOT-INF/classes/).
  - nested_jar_names: every non-directory member ending .jar/.war (any depth: BOOT-INF/lib, WEB-INF/lib, lib/),
    central-directory order; nested_jar_count its length.
  - add_opens / add_exports: whitespace-split JSON list; sealed / can_*: bool (value == "true", absent -> false).
  - entry_section_names: the `Name:` values of the per-entry sections, stored order.
Not a zip / no manifest -> "none"."""
import re

from .jar import _attr, _manifest_bytes, _zip, descend, parse_manifest

FIELDS = {
    ("jar", "start_class"): "jl_attr",
    ("jar", "spring_boot_version"): "jl_attr",
    ("jar", "spring_boot_classes"): "jl_attr",
    ("jar", "spring_boot_lib"): "jl_attr",
    ("jar", "spring_boot_classpath_index"): "jl_attr",
    ("jar", "spring_boot_layers_index"): "jl_attr",
    ("jar", "enable_native_access"): "jl_attr",
    ("jar", "rsrc_main_class"): "jl_attr",
    ("jar", "one_jar_main_class"): "jl_attr",
    ("jar", "sealed"): "jl_bool_attr",
    ("jar", "can_redefine_classes"): "jl_bool_attr",
    ("jar", "can_retransform_classes"): "jl_bool_attr",
    ("jar", "can_set_native_method_prefix"): "jl_bool_attr",
    ("jar", "add_opens"): "jl_list_attr",
    ("jar", "add_exports"): "jl_list_attr",
    ("jar", "manifest_add_opens"): "jl_list_attr",
    ("jar", "manifest_add_exports"): "jl_list_attr",
    ("jar", "main_class_is_launcher"): "jl_is_launcher",
    ("jar", "is_launcher_jar"): "jl_is_launcher",
    ("jar", "uses_launcher"): "jl_is_launcher",
    ("jar", "main_class_launcher"): "jl_is_launcher",
    ("jar", "effective_main_class"): "jl_effective_main",
    ("jar", "real_main_class"): "jl_effective_main",
    ("jar", "application_main_class"): "jl_effective_main",
    ("jar", "actual_main_class"): "jl_effective_main",
    ("jar", "nested_jar_names"): "jl_nested",
    ("jar", "nested_jars"): "jl_nested",
    ("jar", "nested_jar_count"): "jl_nested",
    ("jar", "nested_jar_member_names"): "jl_nested",
    ("jar", "nested_jars_count"): "jl_nested",
    ("jar", "nested_archive_names"): "jl_nested",
    ("jar", "nested_archive_count"): "jl_nested",
    ("jar", "main_class_entry_name"): "jl_entry_name",
    ("jar", "main_class_entry"): "jl_entry_name",
    ("jar", "main_class_path"): "jl_entry_name",
    ("jar", "main_class_file"): "jl_entry_name",
    ("jar", "start_class_entry_name"): "jl_entry_name",
    ("jar", "main_class_entry_present"): "jl_runnable",
    ("jar", "main_class_entry_exists"): "jl_runnable",
    ("jar", "main_class_present"): "jl_runnable",
    ("jar", "is_runnable"): "jl_runnable",
    ("jar", "runnable"): "jl_runnable",
    ("jar", "is_executable"): "jl_runnable",
    ("jar", "is_executable_jar"): "jl_runnable",
    ("jar", "start_class_entry_present"): "jl_runnable",
    ("jar", "entry_section_names"): "jl_sections",
    ("jar", "per_entry_section_names"): "jl_sections",
    ("jar", "section_names"): "jl_sections",
    ("jar", "manifest_section_names"): "jl_sections",
    ("jar", "named_section_names"): "jl_sections",
    ("jar", "manifest_entry_section_names"): "jl_sections",
    ("jar", "entry_section_count"): "jl_sections",
    ("jar", "section_count"): "jl_sections",
    ("jar", "manifest_section_count"): "jl_sections",
    ("jar", "duplicate_main_attribute_names"): "jl_dups",
    ("jar", "duplicate_main_attributes"): "jl_dups",
    ("jar", "duplicate_attribute_names"): "jl_dups",
    ("jar", "has_duplicate_main_attributes"): "jl_dups",
    ("jar", "main_class_first"): "jl_dups",
    ("jar", "main_class_last"): "jl_dups",
    ("jar", "first_main_class"): "jl_dups",
    ("jar", "last_main_class"): "jl_dups",
    ("jar", "start_class_first"): "jl_dups",
    ("jar", "start_class_last"): "jl_dups",
    ("jar", "manifest_entry_index"): "jl_entry_index",
    ("jar", "manifest_index"): "jl_entry_index",
    ("jar", "manifest_entry_position"): "jl_entry_index",
    ("jar", "jar_input_stream_main_class"): "jl_stream_main",
    ("jar", "jarinputstream_main_class"): "jl_stream_main",
    ("jar", "jar_input_stream_sees_manifest"): "jl_stream_main",
    ("jar", "jar_input_stream_manifest_present"): "jl_stream_main",
    ("jar", "jar_file_main_class"): "jl_jarfile_main",
    ("jar", "jarfile_main_class"): "jl_jarfile_main",
    ("java_archive", "start_class"): "jl_attr",
    ("java_archive", "spring_boot_version"): "jl_attr",
    ("java_archive", "spring_boot_classes"): "jl_attr",
    ("java_archive", "spring_boot_lib"): "jl_attr",
    ("java_archive", "spring_boot_classpath_index"): "jl_attr",
    ("java_archive", "spring_boot_layers_index"): "jl_attr",
    ("java_archive", "launcher_agent_class"): "jl_attr",
    ("java_archive", "premain_class"): "jl_attr",
    ("java_archive", "agent_class"): "jl_attr",
    ("java_archive", "enable_native_access"): "jl_attr",
    ("java_archive", "rsrc_main_class"): "jl_attr",
    ("java_archive", "one_jar_main_class"): "jl_attr",
    ("java_archive", "sealed"): "jl_bool_attr",
    ("java_archive", "can_redefine_classes"): "jl_bool_attr",
    ("java_archive", "can_retransform_classes"): "jl_bool_attr",
    ("java_archive", "can_set_native_method_prefix"): "jl_bool_attr",
    ("java_archive", "add_opens"): "jl_list_attr",
    ("java_archive", "add_exports"): "jl_list_attr",
    ("java_archive", "manifest_add_opens"): "jl_list_attr",
    ("java_archive", "manifest_add_exports"): "jl_list_attr",
    ("java_archive", "main_class_is_launcher"): "jl_is_launcher",
    ("java_archive", "is_launcher_jar"): "jl_is_launcher",
    ("java_archive", "uses_launcher"): "jl_is_launcher",
    ("java_archive", "main_class_launcher"): "jl_is_launcher",
    ("java_archive", "effective_main_class"): "jl_effective_main",
    ("java_archive", "real_main_class"): "jl_effective_main",
    ("java_archive", "application_main_class"): "jl_effective_main",
    ("java_archive", "actual_main_class"): "jl_effective_main",
    ("java_archive", "nested_jar_names"): "jl_nested",
    ("java_archive", "nested_jars"): "jl_nested",
    ("java_archive", "nested_jar_count"): "jl_nested",
    ("java_archive", "nested_jar_member_names"): "jl_nested",
    ("java_archive", "nested_jars_count"): "jl_nested",
    ("java_archive", "nested_archive_names"): "jl_nested",
    ("java_archive", "nested_archive_count"): "jl_nested",
    ("java_archive", "main_class_entry_name"): "jl_entry_name",
    ("java_archive", "main_class_entry"): "jl_entry_name",
    ("java_archive", "main_class_path"): "jl_entry_name",
    ("java_archive", "main_class_file"): "jl_entry_name",
    ("java_archive", "start_class_entry_name"): "jl_entry_name",
    ("java_archive", "main_class_entry_present"): "jl_runnable",
    ("java_archive", "main_class_entry_exists"): "jl_runnable",
    ("java_archive", "main_class_present"): "jl_runnable",
    ("java_archive", "is_runnable"): "jl_runnable",
    ("java_archive", "runnable"): "jl_runnable",
    ("java_archive", "is_executable"): "jl_runnable",
    ("java_archive", "is_executable_jar"): "jl_runnable",
    ("java_archive", "start_class_entry_present"): "jl_runnable",
    ("java_archive", "entry_section_names"): "jl_sections",
    ("java_archive", "per_entry_section_names"): "jl_sections",
    ("java_archive", "section_names"): "jl_sections",
    ("java_archive", "manifest_section_names"): "jl_sections",
    ("java_archive", "named_section_names"): "jl_sections",
    ("java_archive", "manifest_entry_section_names"): "jl_sections",
    ("java_archive", "entry_section_count"): "jl_sections",
    ("java_archive", "section_count"): "jl_sections",
    ("java_archive", "manifest_section_count"): "jl_sections",
    ("java_archive", "duplicate_main_attribute_names"): "jl_dups",
    ("java_archive", "duplicate_main_attributes"): "jl_dups",
    ("java_archive", "duplicate_attribute_names"): "jl_dups",
    ("java_archive", "has_duplicate_main_attributes"): "jl_dups",
    ("java_archive", "main_class_first"): "jl_dups",
    ("java_archive", "main_class_last"): "jl_dups",
    ("java_archive", "first_main_class"): "jl_dups",
    ("java_archive", "last_main_class"): "jl_dups",
    ("java_archive", "start_class_first"): "jl_dups",
    ("java_archive", "start_class_last"): "jl_dups",
    ("java_archive", "manifest_entry_index"): "jl_entry_index",
    ("java_archive", "manifest_index"): "jl_entry_index",
    ("java_archive", "manifest_entry_position"): "jl_entry_index",
    ("java_archive", "jar_input_stream_main_class"): "jl_stream_main",
    ("java_archive", "jarinputstream_main_class"): "jl_stream_main",
    ("java_archive", "jar_input_stream_sees_manifest"): "jl_stream_main",
    ("java_archive", "jar_input_stream_manifest_present"): "jl_stream_main",
    ("java_archive", "jar_file_main_class"): "jl_jarfile_main",
    ("java_archive", "jarfile_main_class"): "jl_jarfile_main",
    ("war", "start_class"): "jl_attr",
    ("war", "spring_boot_version"): "jl_attr",
    ("war", "spring_boot_classes"): "jl_attr",
    ("war", "spring_boot_lib"): "jl_attr",
    ("war", "spring_boot_classpath_index"): "jl_attr",
    ("war", "spring_boot_layers_index"): "jl_attr",
    ("war", "launcher_agent_class"): "jl_attr",
    ("war", "premain_class"): "jl_attr",
    ("war", "agent_class"): "jl_attr",
    ("war", "enable_native_access"): "jl_attr",
    ("war", "rsrc_main_class"): "jl_attr",
    ("war", "one_jar_main_class"): "jl_attr",
    ("war", "sealed"): "jl_bool_attr",
    ("war", "can_redefine_classes"): "jl_bool_attr",
    ("war", "can_retransform_classes"): "jl_bool_attr",
    ("war", "can_set_native_method_prefix"): "jl_bool_attr",
    ("war", "add_opens"): "jl_list_attr",
    ("war", "add_exports"): "jl_list_attr",
    ("war", "manifest_add_opens"): "jl_list_attr",
    ("war", "manifest_add_exports"): "jl_list_attr",
    ("war", "main_class_is_launcher"): "jl_is_launcher",
    ("war", "is_launcher_jar"): "jl_is_launcher",
    ("war", "uses_launcher"): "jl_is_launcher",
    ("war", "main_class_launcher"): "jl_is_launcher",
    ("war", "effective_main_class"): "jl_effective_main",
    ("war", "real_main_class"): "jl_effective_main",
    ("war", "application_main_class"): "jl_effective_main",
    ("war", "actual_main_class"): "jl_effective_main",
    ("war", "nested_jar_names"): "jl_nested",
    ("war", "nested_jars"): "jl_nested",
    ("war", "nested_jar_count"): "jl_nested",
    ("war", "nested_jar_member_names"): "jl_nested",
    ("war", "nested_jars_count"): "jl_nested",
    ("war", "nested_archive_names"): "jl_nested",
    ("war", "nested_archive_count"): "jl_nested",
    ("war", "main_class_entry_name"): "jl_entry_name",
    ("war", "main_class_entry"): "jl_entry_name",
    ("war", "main_class_path"): "jl_entry_name",
    ("war", "main_class_file"): "jl_entry_name",
    ("war", "start_class_entry_name"): "jl_entry_name",
    ("war", "main_class_entry_present"): "jl_runnable",
    ("war", "main_class_entry_exists"): "jl_runnable",
    ("war", "main_class_present"): "jl_runnable",
    ("war", "is_runnable"): "jl_runnable",
    ("war", "runnable"): "jl_runnable",
    ("war", "is_executable"): "jl_runnable",
    ("war", "is_executable_jar"): "jl_runnable",
    ("war", "start_class_entry_present"): "jl_runnable",
    ("war", "entry_section_names"): "jl_sections",
    ("war", "per_entry_section_names"): "jl_sections",
    ("war", "section_names"): "jl_sections",
    ("war", "manifest_section_names"): "jl_sections",
    ("war", "named_section_names"): "jl_sections",
    ("war", "manifest_entry_section_names"): "jl_sections",
    ("war", "entry_section_count"): "jl_sections",
    ("war", "section_count"): "jl_sections",
    ("war", "manifest_section_count"): "jl_sections",
    ("war", "duplicate_main_attribute_names"): "jl_dups",
    ("war", "duplicate_main_attributes"): "jl_dups",
    ("war", "duplicate_attribute_names"): "jl_dups",
    ("war", "has_duplicate_main_attributes"): "jl_dups",
    ("war", "main_class_first"): "jl_dups",
    ("war", "main_class_last"): "jl_dups",
    ("war", "first_main_class"): "jl_dups",
    ("war", "last_main_class"): "jl_dups",
    ("war", "start_class_first"): "jl_dups",
    ("war", "start_class_last"): "jl_dups",
    ("war", "manifest_entry_index"): "jl_entry_index",
    ("war", "manifest_index"): "jl_entry_index",
    ("war", "manifest_entry_position"): "jl_entry_index",
    ("war", "jar_input_stream_main_class"): "jl_stream_main",
    ("war", "jarinputstream_main_class"): "jl_stream_main",
    ("war", "jar_input_stream_sees_manifest"): "jl_stream_main",
    ("war", "jar_input_stream_manifest_present"): "jl_stream_main",
    ("war", "jar_file_main_class"): "jl_jarfile_main",
    ("war", "jarfile_main_class"): "jl_jarfile_main",
    ("ear", "start_class"): "jl_attr",
    ("ear", "spring_boot_version"): "jl_attr",
    ("ear", "spring_boot_classes"): "jl_attr",
    ("ear", "spring_boot_lib"): "jl_attr",
    ("ear", "spring_boot_classpath_index"): "jl_attr",
    ("ear", "spring_boot_layers_index"): "jl_attr",
    ("ear", "launcher_agent_class"): "jl_attr",
    ("ear", "premain_class"): "jl_attr",
    ("ear", "agent_class"): "jl_attr",
    ("ear", "enable_native_access"): "jl_attr",
    ("ear", "rsrc_main_class"): "jl_attr",
    ("ear", "one_jar_main_class"): "jl_attr",
    ("ear", "sealed"): "jl_bool_attr",
    ("ear", "can_redefine_classes"): "jl_bool_attr",
    ("ear", "can_retransform_classes"): "jl_bool_attr",
    ("ear", "can_set_native_method_prefix"): "jl_bool_attr",
    ("ear", "add_opens"): "jl_list_attr",
    ("ear", "add_exports"): "jl_list_attr",
    ("ear", "manifest_add_opens"): "jl_list_attr",
    ("ear", "manifest_add_exports"): "jl_list_attr",
    ("ear", "main_class_is_launcher"): "jl_is_launcher",
    ("ear", "is_launcher_jar"): "jl_is_launcher",
    ("ear", "uses_launcher"): "jl_is_launcher",
    ("ear", "main_class_launcher"): "jl_is_launcher",
    ("ear", "effective_main_class"): "jl_effective_main",
    ("ear", "real_main_class"): "jl_effective_main",
    ("ear", "application_main_class"): "jl_effective_main",
    ("ear", "actual_main_class"): "jl_effective_main",
    ("ear", "nested_jar_names"): "jl_nested",
    ("ear", "nested_jars"): "jl_nested",
    ("ear", "nested_jar_count"): "jl_nested",
    ("ear", "nested_jar_member_names"): "jl_nested",
    ("ear", "nested_jars_count"): "jl_nested",
    ("ear", "nested_archive_names"): "jl_nested",
    ("ear", "nested_archive_count"): "jl_nested",
    ("ear", "main_class_entry_name"): "jl_entry_name",
    ("ear", "main_class_entry"): "jl_entry_name",
    ("ear", "main_class_path"): "jl_entry_name",
    ("ear", "main_class_file"): "jl_entry_name",
    ("ear", "start_class_entry_name"): "jl_entry_name",
    ("ear", "main_class_entry_present"): "jl_runnable",
    ("ear", "main_class_entry_exists"): "jl_runnable",
    ("ear", "main_class_present"): "jl_runnable",
    ("ear", "is_runnable"): "jl_runnable",
    ("ear", "runnable"): "jl_runnable",
    ("ear", "is_executable"): "jl_runnable",
    ("ear", "is_executable_jar"): "jl_runnable",
    ("ear", "start_class_entry_present"): "jl_runnable",
    ("ear", "entry_section_names"): "jl_sections",
    ("ear", "per_entry_section_names"): "jl_sections",
    ("ear", "section_names"): "jl_sections",
    ("ear", "manifest_section_names"): "jl_sections",
    ("ear", "named_section_names"): "jl_sections",
    ("ear", "manifest_entry_section_names"): "jl_sections",
    ("ear", "entry_section_count"): "jl_sections",
    ("ear", "section_count"): "jl_sections",
    ("ear", "manifest_section_count"): "jl_sections",
    ("ear", "duplicate_main_attribute_names"): "jl_dups",
    ("ear", "duplicate_main_attributes"): "jl_dups",
    ("ear", "duplicate_attribute_names"): "jl_dups",
    ("ear", "has_duplicate_main_attributes"): "jl_dups",
    ("ear", "main_class_first"): "jl_dups",
    ("ear", "main_class_last"): "jl_dups",
    ("ear", "first_main_class"): "jl_dups",
    ("ear", "last_main_class"): "jl_dups",
    ("ear", "start_class_first"): "jl_dups",
    ("ear", "start_class_last"): "jl_dups",
    ("ear", "manifest_entry_index"): "jl_entry_index",
    ("ear", "manifest_index"): "jl_entry_index",
    ("ear", "manifest_entry_position"): "jl_entry_index",
    ("ear", "jar_input_stream_main_class"): "jl_stream_main",
    ("ear", "jarinputstream_main_class"): "jl_stream_main",
    ("ear", "jar_input_stream_sees_manifest"): "jl_stream_main",
    ("ear", "jar_input_stream_manifest_present"): "jl_stream_main",
    ("ear", "jar_file_main_class"): "jl_jarfile_main",
    ("ear", "jarfile_main_class"): "jl_jarfile_main",
    ("spring_boot", "start_class"): "jl_attr",
    ("spring_boot", "spring_boot_version"): "jl_attr",
    ("spring_boot", "spring_boot_classes"): "jl_attr",
    ("spring_boot", "spring_boot_lib"): "jl_attr",
    ("spring_boot", "spring_boot_classpath_index"): "jl_attr",
    ("spring_boot", "spring_boot_layers_index"): "jl_attr",
    ("spring_boot", "launcher_agent_class"): "jl_attr",
    ("spring_boot", "premain_class"): "jl_attr",
    ("spring_boot", "agent_class"): "jl_attr",
    ("spring_boot", "enable_native_access"): "jl_attr",
    ("spring_boot", "rsrc_main_class"): "jl_attr",
    ("spring_boot", "one_jar_main_class"): "jl_attr",
    ("spring_boot", "sealed"): "jl_bool_attr",
    ("spring_boot", "can_redefine_classes"): "jl_bool_attr",
    ("spring_boot", "can_retransform_classes"): "jl_bool_attr",
    ("spring_boot", "can_set_native_method_prefix"): "jl_bool_attr",
    ("spring_boot", "add_opens"): "jl_list_attr",
    ("spring_boot", "add_exports"): "jl_list_attr",
    ("spring_boot", "manifest_add_opens"): "jl_list_attr",
    ("spring_boot", "manifest_add_exports"): "jl_list_attr",
    ("spring_boot", "main_class_is_launcher"): "jl_is_launcher",
    ("spring_boot", "is_launcher_jar"): "jl_is_launcher",
    ("spring_boot", "uses_launcher"): "jl_is_launcher",
    ("spring_boot", "main_class_launcher"): "jl_is_launcher",
    ("spring_boot", "effective_main_class"): "jl_effective_main",
    ("spring_boot", "real_main_class"): "jl_effective_main",
    ("spring_boot", "application_main_class"): "jl_effective_main",
    ("spring_boot", "actual_main_class"): "jl_effective_main",
    ("spring_boot", "nested_jar_names"): "jl_nested",
    ("spring_boot", "nested_jars"): "jl_nested",
    ("spring_boot", "nested_jar_count"): "jl_nested",
    ("spring_boot", "nested_jar_member_names"): "jl_nested",
    ("spring_boot", "nested_jars_count"): "jl_nested",
    ("spring_boot", "nested_archive_names"): "jl_nested",
    ("spring_boot", "nested_archive_count"): "jl_nested",
    ("spring_boot", "main_class_entry_name"): "jl_entry_name",
    ("spring_boot", "main_class_entry"): "jl_entry_name",
    ("spring_boot", "main_class_path"): "jl_entry_name",
    ("spring_boot", "main_class_file"): "jl_entry_name",
    ("spring_boot", "start_class_entry_name"): "jl_entry_name",
    ("spring_boot", "main_class_entry_present"): "jl_runnable",
    ("spring_boot", "main_class_entry_exists"): "jl_runnable",
    ("spring_boot", "main_class_present"): "jl_runnable",
    ("spring_boot", "is_runnable"): "jl_runnable",
    ("spring_boot", "runnable"): "jl_runnable",
    ("spring_boot", "is_executable"): "jl_runnable",
    ("spring_boot", "is_executable_jar"): "jl_runnable",
    ("spring_boot", "start_class_entry_present"): "jl_runnable",
    ("spring_boot", "entry_section_names"): "jl_sections",
    ("spring_boot", "per_entry_section_names"): "jl_sections",
    ("spring_boot", "section_names"): "jl_sections",
    ("spring_boot", "manifest_section_names"): "jl_sections",
    ("spring_boot", "named_section_names"): "jl_sections",
    ("spring_boot", "manifest_entry_section_names"): "jl_sections",
    ("spring_boot", "entry_section_count"): "jl_sections",
    ("spring_boot", "section_count"): "jl_sections",
    ("spring_boot", "manifest_section_count"): "jl_sections",
    ("spring_boot", "duplicate_main_attribute_names"): "jl_dups",
    ("spring_boot", "duplicate_main_attributes"): "jl_dups",
    ("spring_boot", "duplicate_attribute_names"): "jl_dups",
    ("spring_boot", "has_duplicate_main_attributes"): "jl_dups",
    ("spring_boot", "main_class_first"): "jl_dups",
    ("spring_boot", "main_class_last"): "jl_dups",
    ("spring_boot", "first_main_class"): "jl_dups",
    ("spring_boot", "last_main_class"): "jl_dups",
    ("spring_boot", "start_class_first"): "jl_dups",
    ("spring_boot", "start_class_last"): "jl_dups",
    ("spring_boot", "manifest_entry_index"): "jl_entry_index",
    ("spring_boot", "manifest_index"): "jl_entry_index",
    ("spring_boot", "manifest_entry_position"): "jl_entry_index",
    ("spring_boot", "jar_input_stream_main_class"): "jl_stream_main",
    ("spring_boot", "jarinputstream_main_class"): "jl_stream_main",
    ("spring_boot", "jar_input_stream_sees_manifest"): "jl_stream_main",
    ("spring_boot", "jar_input_stream_manifest_present"): "jl_stream_main",
    ("spring_boot", "jar_file_main_class"): "jl_jarfile_main",
    ("spring_boot", "jarfile_main_class"): "jl_jarfile_main",
    ("spring_boot", "main_class"): "jl_attr",
    ("spring_boot", "manifest_main_class"): "jl_attr",
    ("spring_boot", "manifest_*"): "jl_attr",
    ("spring_boot", "manifest_version"): "jl_attr",
    ("spring_boot", "created_by"): "jl_attr",
    ("spring_boot", "implementation_title"): "jl_attr",
    ("spring_boot", "implementation_version"): "jl_attr",
    ("spring_boot", "implementation_vendor"): "jl_attr",
}

_MF = "META-INF/MANIFEST.MF"
_LAUNCH = re.compile(r"^(?:org\.springframework\.boot\.loader(?:\.launch)?\.(?:Jar|War|Properties)Launcher"
                     r"|org\.springframework\.boot\.loader\.wrapper\.ThinJarWrapper"
                     r"|org\.eclipse\.jdt\.internal\.jarinjarloader\.JarRsrcLoader"
                     r"|com\.simontuffs\.onejar\.Boot|Capsule)$")
_TARGET = ("Start-Class", "Rsrc-Main-Class", "One-Jar-Main-Class", "Application-Class")


def parse_sections(raw):
    """([(Name, value)] main section in stored order, [[(Name, value)], ...] per-entry sections), or None."""
    if raw is None:
        return None
    text = raw.decode("utf-8", "replace")
    if text.startswith("﻿"):
        text = text[1:]
    secs, cur = [], []
    for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if ln == "":
            if cur or not secs:
                secs.append(cur)
            cur = []
            continue
        if ln.startswith(" ") and cur:
            n, v = cur[-1]
            cur[-1] = (n, v + ln[1:])
            continue
        n, sep, v = ln.partition(":")
        if sep and n.strip():
            cur.append((n.strip(), v[1:] if v.startswith(" ") else v))
    if cur:
        secs.append(cur)
    if not secs:
        return [], []
    return secs[0], [s for s in secs[1:] if s]


def _ctx_zip(data, ctx):
    z = _zip(descend(data, ctx))
    if z is None:
        return None, None
    return z, _manifest_bytes(z)


def _last(main, name):
    hits = [v.strip() for n, v in main if n.lower() == name.lower()]
    return hits[-1] if hits else None


def _main_attrs(data, ctx):
    z, raw = _ctx_zip(data, ctx)
    if raw is None:
        return None, None
    return z, (parse_sections(raw) or ([], []))[0]


def jl_attr(data, ctx):
    """<fmt>.<attr>: main-section value, trimmed, first occurrence (as jar.manifest_*)."""
    if data is None:
        return None
    z, raw = _ctx_zip(data, ctx)
    mf = parse_manifest(raw)
    if mf is None:
        return "none"
    v = _attr(mf, ctx.get("field"))
    return "none" if v is None else v


def jl_bool_attr(data, ctx):
    if data is None:
        return None
    z, raw = _ctx_zip(data, ctx)
    mf = parse_manifest(raw)
    if mf is None:
        return "none"
    return (_attr(mf, ctx.get("field")) or "").strip().lower() == "true"


def jl_list_attr(data, ctx):
    if data is None:
        return None
    z, raw = _ctx_zip(data, ctx)
    mf = parse_manifest(raw)
    if mf is None:
        return "none"
    field = (ctx.get("field") or "").replace("manifest_", "", 1)
    v = _attr(mf, field)
    return "none" if v is None else v.split()


def _launch(main):
    """(Main-Class as the JDK reads it, is-launcher, effective main class)."""
    mc = _last(main, "Main-Class")
    if mc is None:
        return None, False, None
    if not _LAUNCH.match(mc):
        return mc, False, mc
    tgt = next((t for t in (_last(main, n) for n in _TARGET) if t), None)
    return mc, True, tgt


def jl_is_launcher(data, ctx):
    if data is None:
        return None
    z, main = _main_attrs(data, ctx)
    if main is None:
        return "none"
    return _launch(main)[1]


def jl_effective_main(data, ctx):
    if data is None:
        return None
    z, main = _main_attrs(data, ctx)
    if main is None:
        return "none"
    return _launch(main)[2] or "none"


def jl_nested(data, ctx):
    if data is None:
        return None
    z, raw = _ctx_zip(data, ctx)
    if z is None or raw is None:
        return "none"
    names = [i.filename for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith((".jar", ".war"))]
    return len(names) if (ctx.get("field") or "").endswith("_count") else names


def _class_entry(cls, prefix=""):
    return prefix + cls.replace(".", "/") + ".class"


def _entry(z, main, field):
    """(entry name, present?) for Main-Class, or Start-Class under Spring-Boot-Classes for start_class_* fields."""
    if field.startswith("start_class"):
        cls = _last(main, "Start-Class")
        prefix = (_last(main, "Spring-Boot-Classes") or "BOOT-INF/classes/").lstrip("/")
        prefix = prefix if not prefix or prefix.endswith("/") else prefix + "/"
    else:
        cls, prefix = _last(main, "Main-Class"), ""
    if not cls:
        return None, False
    name = _class_entry(cls, prefix)
    return name, name in z.namelist()


def jl_entry_name(data, ctx):
    if data is None:
        return None
    z, main = _main_attrs(data, ctx)
    if main is None:
        return "none"
    return _entry(z, main, ctx.get("field") or "")[0] or "none"


def jl_runnable(data, ctx):
    if data is None:
        return None
    z, main = _main_attrs(data, ctx)
    if main is None:
        return "none"
    return _entry(z, main, ctx.get("field") or "")[1]


def jl_sections(data, ctx):
    if data is None:
        return None
    z, raw = _ctx_zip(data, ctx)
    p = parse_sections(raw)
    if p is None:
        return "none"
    names = []
    for sec in p[1]:
        n = next((v.strip() for k, v in sec if k.lower() == "name"), None)
        if n is not None:
            names.append(n)
    return len(names) if (ctx.get("field") or "").endswith("_count") else names


def jl_dups(data, ctx):
    if data is None:
        return None
    z, main = _main_attrs(data, ctx)
    if main is None:
        return "none"
    field = ctx.get("field") or ""
    if "main_class" in field or "start_class" in field:
        want = "main-class" if "main_class" in field else "start-class"
        hits = [v.strip() for n, v in main if n.lower() == want]
        if not hits:
            return "none"
        return hits[-1] if "last" in field else hits[0]
    seen, first = {}, {}
    for n, _ in main:
        seen[n.lower()] = seen.get(n.lower(), 0) + 1
        first.setdefault(n.lower(), n)
    dups = [first[k] for k in first if seen[k] > 1]
    return bool(dups) if field.startswith("has_") else dups


def _stream_order(z):
    return sorted(z.infolist(), key=lambda i: i.header_offset)


def jl_entry_index(data, ctx):
    if data is None:
        return None
    z = _zip(descend(data, ctx))
    if z is None:
        return "none"
    for k, i in enumerate(_stream_order(z), 1):
        if i.filename.upper() == _MF:
            return k
    return "none"


def jl_stream_main(data, ctx):
    """JarInputStream: entry 1 (or 2 after a META-INF/ directory entry), names compared ignoring case."""
    if data is None:
        return None
    z = _zip(descend(data, ctx))
    if z is None:
        return "none"
    order = _stream_order(z)
    if order and order[0].filename.upper() == "META-INF/":
        order = order[1:]
    hit = order[0] if order and order[0].filename.upper() == _MF else None
    raw = None
    if hit is not None:
        try:
            raw = z.read(hit)
        except Exception:  # noqa: BLE001
            raw = None
    if (ctx.get("field") or "").endswith(("_sees_manifest", "_manifest_present")):
        return raw is not None
    p = parse_sections(raw)
    return (_last(p[0], "Main-Class") if p else None) or "none"


def jl_jarfile_main(data, ctx):
    """JarFile/java -jar: the manifest via the central directory (exact name, else case-insensitive), last value."""
    if data is None:
        return None
    z = _zip(descend(data, ctx))
    if z is None:
        return "none"
    infos = z.infolist()
    hit = [i for i in infos if i.filename == _MF] or [i for i in infos if i.filename.upper() == _MF]
    if not hit:
        return "none"
    try:
        raw = z.read(hit[-1])
    except Exception:  # noqa: BLE001
        return "none"
    p = parse_sections(raw)
    return (_last(p[0], "Main-Class") if p else None) or "none"
