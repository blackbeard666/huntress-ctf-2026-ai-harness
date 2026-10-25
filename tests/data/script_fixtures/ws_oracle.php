<?php
// Independent oracle: PHP's own lexer (token_get_all) -> live `line:api` calls. Comments, strings and inline HTML are
// separate tokens; `if (false) {..}` blocks and everything after a top-level `return;` are skipped.
$apis = ['system','exec','passthru','shell_exec','proc_open','popen','eval','assert','create_function',
         'file_put_contents','fwrite','unserialize','fsockopen','curl_exec','include','require'];
$t = array_values(array_filter(token_get_all(file_get_contents($argv[1])),
     fn($x) => !(is_array($x) && in_array($x[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT]))));
$out = []; $req = []; $skip = 0; $dead = false;
for ($i = 0; $i < count($t); $i++) {
    $x = $t[$i]; $v = is_array($x) ? $x[1] : $x;
    if ($dead) break;
    if (is_array($x) && $x[0] == T_IF && $t[$i+1] == '(' && is_array($t[$i+2]) && strtolower($t[$i+2][1]) == 'false'
        && $t[$i+3] == ')' && $t[$i+4] == '{') {
        $d = 0; for ($j = $i + 4; $j < count($t); $j++) { if ($t[$j] == '{') $d++; if ($t[$j] == '}' && --$d == 0) break; }
        $i = $j; continue;
    }
    if (is_array($x) && $x[0] == T_RETURN) { $dead = true; continue; }
    if (is_array($x) && in_array($x[0], [T_STRING, T_EVAL, T_INCLUDE, T_REQUIRE]) && in_array(strtolower($v), $apis)
        && ($t[$i+1] == '(' || in_array($x[0], [T_INCLUDE, T_REQUIRE]))) $out[] = $x[2] . ':' . strtolower($v);
    if (is_array($x) && $x[0] == T_VARIABLE && preg_match('/^\$_(GET|POST|REQUEST|COOKIE|SERVER)$/', $v) && $t[$i+1] == '['
        && is_array($t[$i+2]) && $t[$i+2][0] == T_CONSTANT_ENCAPSED_STRING) $req[] = trim($t[$i+2][1], "'\"");
}
if (($argv[2] ?? 'live') == 'requests') $out = array_values(array_unique($req));
echo $out ? implode(',', $out) : 'none', "\n";
