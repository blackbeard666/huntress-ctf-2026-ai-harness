val greeting = buildString { append("hello, "); append("world") }
val descriptor_none = listOf("a", "b", "c").joinToString("")
println(greeting + descriptor_none)
