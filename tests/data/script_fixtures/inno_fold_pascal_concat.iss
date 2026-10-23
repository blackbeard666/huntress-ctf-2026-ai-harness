; Huntress analysis installer
[Setup]
AppName=Huntress Analysis 95e72522
AppVersion=1.0
DefaultDirName={autopf}\Huntress
OutputBaseFilename=huntress-95e72522

[Code]
{ HUNTRESS_ANALYSIS_V1:HEX- descriptor assembled in InitializeWizard }
var
  Descriptor: String;
  ResultCode: Integer;

procedure InitializeWizard();
begin
  Descriptor := '763d33'#$37#99 + '6c616e67756167653d696e6e6f5f7365' +
    '7475707c726f6c653d6c61756e636865727c7665';
  Descriptor := Descriptor + '72646963743d737573706963696f75737c61747461636b3d54313035397c616461707465723d7072';  // piece
  Descriptor := Descriptor + '6f636573735f6275696c6465727c686f73745f70726f66696c653d7374616e64616c6f6e657c6f62';  // piece
  Descriptor := Descriptor + '667573636174696f6e5f70726f66696c653d706c61696e5f6865787c73746167655f70726f66696c';  // piece
  Descriptor := Descriptor + '653d73696e676c655f64657363726970746f727c6e6578745f6c616e67756167653d62617463687c';  // piece
  Descriptor := Descriptor + '73746167655f636f756e743d327c73746570733d6465636f64655f636f6e66696775726174696f6e';  // piece
  Descriptor := Descriptor + '2c72657475726e5f636f6e66696775726174696f6e7c63616d706169676e5f69643d494e4e4f5f53';  // piece
  Descriptor := Descriptor + '455455502d31633636303738347c75726c3d68747470733a2f2f696e6e6f2d73657475702d316336';  // piece
  Descriptor := Descriptor + '363037383431332e6578616d706c652e696e76616c69642f73746167657c66696c655f706174683d';  // piece
  Descriptor := Descriptor + '2f746d702f68756e74726573732d696e6e6f2f2e316336363037383431333534626430382e737461';  // piece
  Descriptor := Descriptor + '6765';  // piece
  Log('Don''t panic: ' + Descriptor);
  Exec(ExpandConstant('{sys}\cmd.exe'), '/c echo ' + Descriptor, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
