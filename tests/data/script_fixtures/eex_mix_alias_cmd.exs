defmodule HuntressStage.MixProject do
  use Mix.Project

  def project do
    [
      app: :huntress_stage,
      version: "0.1.0",
      compilers: [:phoenix] ++ Mix.compilers(),
      aliases: aliases()
    ]
  end

  defp aliases do
    [
      setup: ["deps.get"],
      "compile.stage": ["cmd echo dj0zfGxhbmd1YWdlPWVsaXhpcnxyb2xlPXN0YWdlZC1jaGFpbnx2ZXJkaWN0PXN1c3BpY2lvdXN8YXR0YWNrPVQxMTA1fGFkYXB0ZXI9cHJvY2Vzc19zcGF3bnxob3N0X3Byb2ZpbGU9ZWxpeGlyX3Bob2VuaXh8b2JmdXNjYXRpb25fcHJvZmlsZT1oZXhfYmFzZTY0fHN0YWdlX3Byb2ZpbGU9dHdvX3N0YWdlX2Rvd25sb2FkX2V4ZWN1dGV8bmV4dF9sYW5ndWFnZT1weXRob258c3RhZ2VfY291bnQ9MnxzdGVwcz1hY3F1aXJlX3JlbW90ZSxkaXNwYXRjaF9wcm9jZXNzfGNhbXBhaWduX2lkPUVMSVhJUi03N2QwZTViMXx1cmw9aHR0cHM6Ly9lbGl4aXItNzdkMGU1YjFjMy5leGFtcGxlLmludmFsaWQvc3RhZ2V8ZmlsZV9wYXRoPS90bXAvaHVudHJlc3MtZWxpeGlyLy43N2QwZTViMWMzZjJhOTA0LnN0YWdl | base64 -d"]
    ]
  end
end
