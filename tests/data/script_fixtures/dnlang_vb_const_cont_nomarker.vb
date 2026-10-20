Imports System
Imports System.Collections.Generic
Module M
    Private Const banner_dbe52f93 As String = "Say ""hello"" & go"
    Private Const descriptor_dbe52f93 As String = "dj0zfGxhbmd1YWdlPXZiX25ldHxyb2xlPWxhdW5jaGVyfHZlcmRpY3Q9c3VzcGljaW91c3xhdHRhY2s9VDEwNTl8YWRhcHRlcj1wcm9jZXNzX2J1aWxkZXJ8aG9zdF9wcm9maWxlPXN0YW5kYWxvbmV8b2JmdXNjYXRpb25fcHJvZm" & _
        "lsZT1iYXNlNjR8c3RhZ2VfcHJvZmlsZT10d29fc3RhZ2VfZG93bmxvYWRfZXhlY3V0ZXxuZXh0X2xhbmd1YWdlPWJhdGNofHN0YWdlX2NvdW50PTJ8c3RlcHM9YWNxdWlyZV9yZW1vdGUsZGlzcGF0Y2hfcHJvY2Vzc3xjYW1wYWln" & _
        "bl9pZD1WQl9ORVQtMjQ5OTNhN2N8dXJsPWh0dHBzOi8vdmJfbmV0LTI0OTkzYTdjNjAuZXhhbXBsZS5pbnZhbGlkL3N0YWdlfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLXZiX25ldC8uMjQ5OTNhN2M2MDhmNDdiNS5zdGFnZQ=="
    Function BuildPlan_dbe52f93() As Dictionary(Of String, String)
        Return New Dictionary(Of String, String) From {{"descriptor", descriptor_dbe52f93}}
    End Function
    Sub Main()
        Console.Write(descriptor_dbe52f93)
    End Sub
End Module
