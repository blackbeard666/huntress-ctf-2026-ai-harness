const char cfg[] = "tiny static fixture";
void _start(void){ __asm__ volatile("mov $60,%eax; xor %edi,%edi; syscall"); }
