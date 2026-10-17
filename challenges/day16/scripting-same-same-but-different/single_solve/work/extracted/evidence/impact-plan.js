// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_ab72ca27(SoUrCeByTeS) {
  var keyBytes = [143,15,32,170,243];
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ keyBytes[i % keyBytes.length]); }
  return DeCoDeDByTeS;
}
function recover_2b9be446() {
  if (true) {
    var packedText = "f4:2d:53:de:96:ff:7c:02:90:a8:ad:6a:4e:df:9e:ea:7d:41:de:96:d0:7b:41:d8:94:ea:7b:53:88:df:ad:7b:52:cb:9d:fc:69:4f:d8:9e:d0:6c:4f:c4:87:ea:61:54:88:df:ad:78:52:c3:87:ea:50:52:cf:90:e0:79:45:d8:8a:d0:61:4f:de:96:ad:52:0c:88:92:eb:6e:50:de:96:fd:2d:1a:88:b2:cb:40:64:e8:dd:dc:7b:52:cf:92:e2:2d:0c:88:85:ee:63:55:cf:80:ad:35:5b:88:90:ee:62:50:cb:9a:e8:61:7f:c3:97:ad:35:02:c9:92:e2:7f:41:c3:94:e1:22:11:cf:c6:be:6b:45:9e:c2:ed:39:02:86:d1:fb:6e:52:cd:96:fb:50:52:c5:9c:fb:2d:1a:88:b0:b5:53:7c:ff:80:ea:7d:53:f6:af:df:7a:42:c6:9a:ec:53:7c:e2:86:e1:7b:52:cf:80:fc:43:41:c8:af:d3:66:4d:da:92:ec:7b:0d:9b:96:ba:3e:44:cf:c7:be:6d:16:88:df:ad:6a:58:de:96:e1:7c:49:c5:9d:ad:35:02:84:9f:e0:6c:4b:cf:97:a2:3e:45:9f:c2:eb:6a:14:9b:91:b9:2d:0c:88:9d:e0:7b:45:f5:9d:ee:62:45:88:c9:ad:5d:65:e9:bc:d9:4a:72:87:c2:ea:3a:11:ce:96:bb:3e:42:9c:dd:fb:77:54:88:8e:a3:2d:53:de:92:e8:6a:63:c5:86:e1:7b:02:90:c0:f2";
    var packedParts = packedText.split(":");
    var SoUrCeByTeS = [];
    for (var hi = 0; hi < packedParts.length; hi++) { SoUrCeByTeS.push(parseInt(packedParts[hi], 16)); }

    var invoke = function(block, value) { return block(value); };
    var DeCoDeDByTeS = invoke(decode_ab72ca27, SoUrCeByTeS);
    var DeScRiPtOrTeXt = "";
    for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
    return DeScRiPtOrTeXt;
  }
}
function inspect_4896fdee() {
  var DeScRiPtOr = eval("(" + recover_2b9be446() + ")");
  return { steps: DeScRiPtOr["steps"], adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr["values"], stageCount: DeScRiPtOr["stageCount"] };
}
