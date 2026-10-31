' dnc_vb fixture: VB.NET module + class/interface/enum/structure, closures (_Closure$__) and #US user strings.
Imports System
Namespace Bravo
  Public Interface IStage
    Function Run() As Integer
  End Interface
  Public Enum Phase
    Start
    Finish
  End Enum
  Public Structure Pair
    Public A As Integer
    Public B As Integer
  End Structure
  Public Class Stage
    Implements IStage
    Public Property Label As String = "vb-stage"
    Public Function Run() As Integer Implements IStage.Run
      Dim k As Integer = 3
      Dim f As Func(Of Integer, Integer) = Function(x) x * k
      Return f(2)
    End Function
  End Class
  Public Module Entry
    Public Function Main() As Integer
      Console.WriteLine("vb-beacon.example.invalid")
      Dim s As New Stage()
      Console.WriteLine(s.Label & Phase.Finish.ToString() & s.Run())
      Return 0
    End Function
  End Module
End Namespace
